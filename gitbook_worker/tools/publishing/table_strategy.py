"""Editorial paper selection for Markdown pipe tables.

The module keeps the decision logic separate from Markdown preprocessing.  It
estimates how table cells would wrap on each candidate paper and selects the
smallest readable option, while preserving the historical column-count fallback
for pathological oversized tables.
"""

from __future__ import annotations

import json
import math
import re
import shlex
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from gitbook_worker.tools.logging_config import get_logger
from gitbook_worker.tools.publishing.paper_info import (
    PaperInfo,
    get_valid_paper_measurements,
)

logger = get_logger(__name__)


COLUMN_WIDTH_MM = 25.0
COLUMN_HEIGHT_MM = 10.0
PIXELS_PER_MM = 11.81
MIN_COLS_FOR_WRAP = 10
TABLE_FONT_SIZE_PT = 10.0
PT_TO_MM = 25.4 / 72.0
MIN_TABLE_COLUMN_WIDTH_MM = 8.0
TABLE_CELL_PADDING_MM = 4.5
TABLE_WIDTH_SAFETY_FACTOR = 1.06
DEFAULT_CANDIDATE_CODES = (
    "a4",
    "a4-landscape",
    "a3",
    "a3-landscape",
    "a2",
    "a2-landscape",
    "a1",
    "a1-landscape",
)

_MARKDOWN_LINK_RE = re.compile(r"(?<!\!)\[(?P<label>[^\]]+)\]\((?P<inner>[^)]+)\)")
_MARKDOWN_IMAGE_RE = re.compile(r"!\[(?P<label>[^\]]*)\]\([^)]+\)")
_MARKDOWN_CODE_SPAN_RE = re.compile(r"`([^`]*)`")
_MARKDOWN_STYLE_MARK_RE = re.compile(r"(?<!\\)[*_~]+")
_HTML_TAG = re.compile(r"<[^>]+>")
_URL_RE = re.compile(r"(?:[a-zA-Z][a-zA-Z0-9+.-]*://|www\.)\S+")
_TABLE_OVERRIDE_RE = re.compile(r"<!--\s*gbw-table(?P<body>.*?)-->", re.I)


@dataclass(frozen=True)
class TablePaperStrategyConfig:
    """Options for editorial table paper selection."""

    enabled: bool = True
    mode: str = "editorial"
    candidates: tuple[PaperInfo, ...] = ()
    max_cell_lines: int = 5
    max_header_lines: int = 3
    preferred_max_avg_row_lines: float = 2.8
    min_readable_column_width_mm: float = 14.0
    unbreakable_overflow_tolerance_mm: float = 2.0
    oversize_policy: str = "preserve-column-heuristic"
    report_path: Path | None = None


@dataclass(frozen=True)
class TableOverride:
    """Explicit per-table source override from a reviewable Markdown comment."""

    paper: str | None = None
    reason: str | None = None
    strategy: str = "force"


@dataclass(frozen=True)
class ColumnProfile:
    """Measured and classified table column."""

    index: int
    kind: str
    header_width_mm: float
    max_text_width_mm: float
    avg_text_width_mm: float
    longest_unbreakable_width_mm: float
    min_readable_width_mm: float
    risk_flags: tuple[str, ...]


@dataclass(frozen=True)
class TableCandidateEvaluation:
    """Editorial layout score for one candidate paper."""

    paper: str
    size_mm: tuple[int, int]
    usable_width_mm: float
    score: float
    acceptable: bool
    max_cell_lines: int
    max_header_lines: int
    average_row_lines: float
    narrow_columns: int
    overflow_mm: float
    unbreakable_overflow_mm: float
    allocated_widths_mm: tuple[float, ...]
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class TableStrategyDecision:
    """Final table paper decision with diagnostics."""

    selected_paper: PaperInfo
    method: str
    reason: str
    columns: int
    estimated_width_mm: float
    paper_by_columns: str
    evaluations: tuple[TableCandidateEvaluation, ...]
    override: TableOverride | None = None


def parse_table_strategy_config(
    raw: Mapping[str, Any] | TablePaperStrategyConfig | None,
) -> TablePaperStrategyConfig:
    """Return a normalized table strategy configuration."""

    if isinstance(raw, TablePaperStrategyConfig):
        return raw
    if not isinstance(raw, Mapping):
        return TablePaperStrategyConfig()

    candidates = tuple(
        _paper_from_candidate(candidate)
        for candidate in _as_sequence(raw.get("candidates"))
        if candidate
    )
    report_path_value = raw.get("report_path") or raw.get("report-file")
    report_path = Path(str(report_path_value)) if report_path_value else None
    return TablePaperStrategyConfig(
        enabled=_as_bool(raw.get("enabled"), default=True),
        mode=str(raw.get("mode") or "editorial").strip() or "editorial",
        candidates=candidates,
        max_cell_lines=_as_int(raw.get("max_cell_lines"), 5),
        max_header_lines=_as_int(raw.get("max_header_lines"), 3),
        preferred_max_avg_row_lines=_as_float(
            raw.get("preferred_max_avg_row_lines"), 2.8
        ),
        min_readable_column_width_mm=_as_float(
            raw.get("min_readable_column_width_mm"), 14.0
        ),
        unbreakable_overflow_tolerance_mm=_as_float(
            raw.get("unbreakable_overflow_tolerance_mm"), 2.0
        ),
        oversize_policy=str(
            raw.get("oversize_policy") or "preserve-column-heuristic"
        ).strip(),
        report_path=report_path,
    )


def parse_table_override_from_context(lines: Sequence[str]) -> TableOverride | None:
    """Parse a trailing ``gbw-table`` HTML comment near a Markdown table."""

    for line in reversed(lines[-4:]):
        stripped = line.strip()
        if not stripped:
            continue
        match = _TABLE_OVERRIDE_RE.fullmatch(stripped)
        if not match:
            return None
        values = _parse_override_body(match.group("body"))
        paper = values.get("paper") or values.get("format")
        if not paper:
            return None
        return TableOverride(
            paper=paper,
            reason=values.get("reason"),
            strategy=values.get("strategy", "force"),
        )
    return None


def iter_paper_candidates(
    base: PaperInfo,
    config: TablePaperStrategyConfig | Mapping[str, Any] | None = None,
) -> Iterable[PaperInfo]:
    """Yield candidate papers starting with ``base`` and preserving order."""

    strategy = parse_table_strategy_config(config)
    configured = strategy.candidates or tuple(
        get_valid_paper_measurements(code) for code in DEFAULT_CANDIDATE_CODES
    )
    seen: set[tuple[str, tuple[int, int], tuple[int, int, int, int]]] = set()

    def register(info: PaperInfo) -> Iterable[PaperInfo]:
        key = (info.norm_name, info.size_mm, info.margins_mm)
        if key in seen:
            return []
        seen.add(key)
        return [info]

    for initial in register(base):
        yield initial

    names = [candidate.norm_name for candidate in configured]
    if base.norm_name in names:
        start_index = names.index(base.norm_name) + 1
    else:
        start_index = 0
    ordered = configured[start_index:] + configured[:start_index]
    for candidate in ordered:
        for item in register(candidate):
            yield item


def available_text_width_mm(paper_info: PaperInfo) -> float:
    """Return usable text width after left and right margins."""

    width, _ = paper_info.size_mm
    left, _, right, _ = paper_info.margins_mm
    return max(0.0, float(width - left - right))


def split_table_row(line: str) -> list[str]:
    """Split a Markdown pipe-table row while respecting escaped pipes."""

    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]

    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in stripped:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\":
            escaped = True
            current.append(char)
            continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    cells.append("".join(current).strip())
    return cells


def is_table_separator_row(line: str) -> bool:
    """Return True for Markdown pipe-table separator rows."""

    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-+:?", cell.strip()) for cell in cells)


def table_rows_for_measurement(table_lines: Sequence[str]) -> list[list[str]]:
    """Return non-separator table rows for measuring."""

    rows: list[list[str]] = []
    for line in table_lines:
        if "|" not in line or is_table_separator_row(line):
            continue
        rows.append(split_table_row(line))
    return rows


def table_column_count(table_lines: Sequence[str]) -> int:
    """Return column count from the first table row."""

    rows = table_rows_for_measurement(table_lines[:1])
    if not rows:
        return 0
    return len(rows[0])


def normalize_table_measurement_text(value: str) -> str:
    """Strip Markdown markup that should not affect table text width."""

    text = value.replace(r"\|", "|")
    text = _MARKDOWN_IMAGE_RE.sub(lambda match: match.group("label"), text)
    text = _MARKDOWN_LINK_RE.sub(lambda match: match.group("label"), text)
    text = _MARKDOWN_CODE_SPAN_RE.sub(lambda match: match.group(1), text)
    text = _strip_html_tags(text)
    text = _MARKDOWN_STYLE_MARK_RE.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


def glyph_width_em(char: str) -> float:
    """Return an approximate glyph width in em units."""

    category = unicodedata.category(char)
    if category.startswith("M"):
        return 0.0
    if char.isspace():
        return 0.32
    if unicodedata.east_asian_width(char) in {"F", "W"}:
        return 1.0
    if category.startswith("S"):
        return 0.85
    if char in "ilI.,:;|'!":
        return 0.28
    if char in "mwMW@#%&":
        return 0.75
    if char.isupper():
        return 0.62
    if char.isdigit():
        return 0.52
    if category.startswith("P"):
        return 0.35
    return 0.52


def estimate_text_width_mm(
    value: str, font_size_pt: float = TABLE_FONT_SIZE_PT
) -> float:
    """Estimate normalized text width in millimetres."""

    text = normalize_table_measurement_text(value)
    return sum(glyph_width_em(char) * font_size_pt * PT_TO_MM for char in text)


def estimate_table_width_mm(table_lines: Sequence[str]) -> float:
    """Estimate unwrapped table width in millimetres."""

    rows = table_rows_for_measurement(table_lines)
    if not rows:
        return 0.0

    column_count = max(len(row) for row in rows)
    column_widths = [MIN_TABLE_COLUMN_WIDTH_MM] * column_count
    for row in rows:
        for index, cell in enumerate(row):
            column_widths[index] = max(
                column_widths[index], estimate_text_width_mm(cell)
            )

    raw_width = sum(column_widths) + column_count * TABLE_CELL_PADDING_MM
    return raw_width * TABLE_WIDTH_SAFETY_FACTOR


def paper_for_columns(
    cols: int,
    rows: int | None = None,
    *,
    height_mm: int = 297,
    base_paper: PaperInfo | None = None,
    config: TablePaperStrategyConfig | Mapping[str, Any] | None = None,
) -> PaperInfo:
    """Return the historical paper choice based on column count."""

    base_info = base_paper or PaperInfo.default()
    min_width_mm = max(cols * COLUMN_WIDTH_MM, base_info.size_mm[0])
    required_height = 0
    if rows:
        height_mm = max(rows * COLUMN_HEIGHT_MM, base_info.size_mm[1])
        required_height = height_mm

    for candidate in iter_paper_candidates(base_info, config):
        width, height = candidate.size_mm
        if width >= min_width_mm and (
            required_height == 0 or height >= required_height
        ):
            return candidate

    logger.warning(
        "Table requires custom paper size (%smm x %smm); falling back to %s.",
        min_width_mm,
        required_height or base_info.size_mm[1],
        base_info.norm_name,
    )
    return base_info


def paper_for_table_width(
    min_width_mm: float,
    *,
    base_paper: PaperInfo | None = None,
    config: TablePaperStrategyConfig | Mapping[str, Any] | None = None,
) -> PaperInfo:
    """Return first paper whose usable width can hold ``min_width_mm``."""

    base_info = base_paper or PaperInfo.default()
    candidates = list(iter_paper_candidates(base_info, config))
    for candidate in candidates:
        if available_text_width_mm(candidate) >= min_width_mm:
            return candidate

    fallback = max(candidates, key=available_text_width_mm)
    logger.warning(
        "Table requires estimated text width %.1fmm; falling back to %s "
        "with %.1fmm usable width.",
        min_width_mm,
        fallback.norm_name,
        available_text_width_mm(fallback),
    )
    return fallback


def choose_table_paper(
    table_lines: Sequence[str],
    *,
    base_paper: PaperInfo | None = None,
    config: TablePaperStrategyConfig | Mapping[str, Any] | None = None,
    override: TableOverride | None = None,
) -> TableStrategyDecision:
    """Choose a paper using the editorial table layout score."""

    base_info = base_paper or PaperInfo.default()
    strategy = parse_table_strategy_config(config)
    cols = table_column_count(table_lines)
    paper_by_columns = paper_for_columns(
        cols=cols, base_paper=base_info, config=strategy
    )
    required_width = estimate_table_width_mm(table_lines)

    if override and override.paper:
        selected = get_valid_paper_measurements(override.paper)
        decision = TableStrategyDecision(
            selected_paper=selected,
            method="override",
            reason=override.reason or "explicit gbw-table source override",
            columns=cols,
            estimated_width_mm=required_width,
            paper_by_columns=paper_by_columns.norm_name,
            evaluations=(),
            override=override,
        )
        _log_and_report_decision(decision, strategy)
        return decision

    if not strategy.enabled:
        decision = TableStrategyDecision(
            selected_paper=paper_by_columns,
            method="disabled",
            reason="table paper strategy disabled; using column heuristic",
            columns=cols,
            estimated_width_mm=required_width,
            paper_by_columns=paper_by_columns.norm_name,
            evaluations=(),
        )
        _log_and_report_decision(decision, strategy)
        return decision

    candidates = list(iter_paper_candidates(base_info, strategy))
    max_candidate_width = max(
        available_text_width_mm(candidate) for candidate in candidates
    )
    if (
        required_width > max_candidate_width
        and strategy.oversize_policy == "preserve-column-heuristic"
    ):
        decision = TableStrategyDecision(
            selected_paper=paper_by_columns,
            method="oversize-preserve-column-heuristic",
            reason=(
                "estimated table width exceeds all configured candidate papers; "
                "editorial intervention or custom paper is required"
            ),
            columns=cols,
            estimated_width_mm=required_width,
            paper_by_columns=paper_by_columns.norm_name,
            evaluations=(),
        )
        logger.warning(
            "Table estimated text width %.1fmm exceeds configured candidate "
            "papers; keeping column heuristic paper %s. Consider splitting "
            "the table, shortening columns, enabling custom paper, or adding "
            "an explicit gbw-table override.",
            required_width,
            paper_by_columns.norm_name,
        )
        _log_and_report_decision(decision, strategy)
        return decision

    minimum_usable_width = available_text_width_mm(paper_by_columns)
    evaluations: list[tuple[PaperInfo, TableCandidateEvaluation]] = []
    for index, candidate in enumerate(candidates):
        if available_text_width_mm(candidate) + 0.01 < minimum_usable_width:
            continue
        evaluation = evaluate_candidate_layout(
            table_lines, candidate, strategy, candidate_index=index
        )
        evaluations.append((candidate, evaluation))

    if not evaluations:
        selected_paper = paper_by_columns
        method = "column-heuristic"
        reason = "no candidate survived the column heuristic lower bound"
        selected_evaluations: tuple[TableCandidateEvaluation, ...] = ()
    else:
        acceptable = [item for item in evaluations if item[1].acceptable]
        if acceptable:
            selected_paper, _ = acceptable[0]
            method = "editorial-best-fit"
            reason = "first candidate that satisfies editorial readability thresholds"
        else:
            selected_paper, _ = min(evaluations, key=lambda item: item[1].score)
            method = "lowest-score-fallback"
            reason = "no candidate fully satisfied thresholds; selected lowest score"
        selected_evaluations = tuple(evaluation for _, evaluation in evaluations)

    decision = TableStrategyDecision(
        selected_paper=selected_paper,
        method=method,
        reason=reason,
        columns=cols,
        estimated_width_mm=required_width,
        paper_by_columns=paper_by_columns.norm_name,
        evaluations=selected_evaluations,
    )
    _log_and_report_decision(decision, strategy)
    return decision


def paper_for_table(
    table_lines: Sequence[str],
    *,
    base_paper: PaperInfo | None = None,
    config: TablePaperStrategyConfig | Mapping[str, Any] | None = None,
    override: TableOverride | None = None,
) -> PaperInfo:
    """Return selected paper for a Markdown table."""

    return choose_table_paper(
        table_lines,
        base_paper=base_paper,
        config=config,
        override=override,
    ).selected_paper


def evaluate_candidate_layout(
    table_lines: Sequence[str],
    paper_info: PaperInfo,
    config: TablePaperStrategyConfig,
    *,
    candidate_index: int = 0,
) -> TableCandidateEvaluation:
    """Evaluate expected table readability on one paper candidate."""

    rows = table_rows_for_measurement(table_lines)
    profiles = _build_column_profiles(rows, config)
    usable_width = available_text_width_mm(paper_info)
    allocated_widths, overflow_mm = _allocate_column_widths(profiles, usable_width)
    max_cell_lines, max_header_lines, average_row_lines, unbreakable_overflow = (
        _estimate_line_metrics(rows, allocated_widths)
    )
    narrow_columns = sum(
        1
        for profile, allocated in zip(profiles, allocated_widths)
        if allocated + 0.01 < profile.min_readable_width_mm
    )

    reasons: list[str] = []
    if overflow_mm > 0:
        reasons.append(f"min-width-overflow={overflow_mm:.1f}mm")
    if max_cell_lines > config.max_cell_lines:
        reasons.append(f"max-cell-lines={max_cell_lines}")
    if max_header_lines > config.max_header_lines:
        reasons.append(f"max-header-lines={max_header_lines}")
    if average_row_lines > config.preferred_max_avg_row_lines:
        reasons.append(f"avg-row-lines={average_row_lines:.1f}")
    if unbreakable_overflow > config.unbreakable_overflow_tolerance_mm:
        reasons.append(f"unbreakable-overflow={unbreakable_overflow:.1f}mm")
    if narrow_columns:
        reasons.append(f"narrow-columns={narrow_columns}")

    acceptable = not reasons
    area = paper_info.size_mm[0] * paper_info.size_mm[1]
    a4_area = 210 * 297
    area_penalty = area / a4_area
    score = (
        candidate_index * 0.2
        + area_penalty * 1.2
        + max(0.0, overflow_mm) * 18.0
        + max(0, max_cell_lines - config.max_cell_lines) * 12.0
        + max(0, max_header_lines - config.max_header_lines) * 14.0
        + max(0.0, average_row_lines - config.preferred_max_avg_row_lines) * 7.0
        + max(0.0, unbreakable_overflow) * 5.0
        + narrow_columns * 4.0
    )
    return TableCandidateEvaluation(
        paper=paper_info.norm_name,
        size_mm=paper_info.size_mm,
        usable_width_mm=usable_width,
        score=round(score, 3),
        acceptable=acceptable,
        max_cell_lines=max_cell_lines,
        max_header_lines=max_header_lines,
        average_row_lines=round(average_row_lines, 3),
        narrow_columns=narrow_columns,
        overflow_mm=round(overflow_mm, 3),
        unbreakable_overflow_mm=round(unbreakable_overflow, 3),
        allocated_widths_mm=tuple(round(width, 3) for width in allocated_widths),
        reasons=tuple(reasons),
    )


def decision_to_dict(decision: TableStrategyDecision) -> dict[str, Any]:
    """Return a JSON-serializable decision record."""

    data = {
        "selected_paper": decision.selected_paper.norm_name,
        "selected_size_mm": decision.selected_paper.size_mm,
        "method": decision.method,
        "reason": decision.reason,
        "columns": decision.columns,
        "estimated_width_mm": round(decision.estimated_width_mm, 3),
        "paper_by_columns": decision.paper_by_columns,
        "evaluations": [asdict(evaluation) for evaluation in decision.evaluations],
    }
    if decision.override:
        data["override"] = asdict(decision.override)
    return data


def _build_column_profiles(
    rows: Sequence[Sequence[str]], config: TablePaperStrategyConfig
) -> tuple[ColumnProfile, ...]:
    column_count = max((len(row) for row in rows), default=0)
    profiles: list[ColumnProfile] = []
    for index in range(column_count):
        cells = [row[index] if index < len(row) else "" for row in rows]
        normalized = [normalize_table_measurement_text(cell) for cell in cells]
        widths = [estimate_text_width_mm(cell) for cell in cells]
        header_width = widths[0] if widths else 0.0
        max_width = max(widths, default=0.0)
        avg_width = sum(widths) / len(widths) if widths else 0.0
        longest_unbreakable = max(
            (_longest_unbreakable_width_mm(cell) for cell in normalized), default=0.0
        )
        kind, flags = _classify_column(normalized)
        min_width = max(
            config.min_readable_column_width_mm,
            _minimum_width_for_kind(kind),
        )
        if "cjk" in flags:
            min_width = max(min_width, 24.0)
        if "url" in flags or "code" in flags:
            min_width = max(min_width, 34.0)
        profiles.append(
            ColumnProfile(
                index=index,
                kind=kind,
                header_width_mm=header_width,
                max_text_width_mm=max_width,
                avg_text_width_mm=avg_width,
                longest_unbreakable_width_mm=longest_unbreakable,
                min_readable_width_mm=min_width,
                risk_flags=tuple(sorted(flags)),
            )
        )
    return tuple(profiles)


def _allocate_column_widths(
    profiles: Sequence[ColumnProfile], usable_width_mm: float
) -> tuple[tuple[float, ...], float]:
    if not profiles:
        return (), 0.0

    text_budget = max(0.0, usable_width_mm - len(profiles) * TABLE_CELL_PADDING_MM)
    min_widths = [profile.min_readable_width_mm for profile in profiles]
    targets = [
        max(profile.min_readable_width_mm, profile.max_text_width_mm)
        for profile in profiles
    ]
    min_sum = sum(min_widths)
    target_sum = sum(targets)
    overflow_mm = max(0.0, min_sum - text_budget)
    if text_budget <= 0:
        return tuple(1.0 for _ in profiles), overflow_mm
    if target_sum <= text_budget:
        return tuple(targets), 0.0
    if min_sum >= text_budget:
        equal_width = text_budget / len(profiles)
        return (
            tuple(max(1.0, min(width, equal_width)) for width in min_widths),
            overflow_mm,
        )

    extra_budget = text_budget - min_sum
    flex_demands = [target - minimum for target, minimum in zip(targets, min_widths)]
    flex_sum = sum(flex_demands)
    if flex_sum <= 0:
        return tuple(min_widths), 0.0
    allocated = [
        minimum + extra_budget * demand / flex_sum
        for minimum, demand in zip(min_widths, flex_demands)
    ]
    return tuple(allocated), 0.0


def _estimate_line_metrics(
    rows: Sequence[Sequence[str]], allocated_widths: Sequence[float]
) -> tuple[int, int, float, float]:
    if not rows or not allocated_widths:
        return 1, 1, 1.0, 0.0

    row_line_counts: list[int] = []
    max_cell_lines = 1
    max_header_lines = 1
    max_unbreakable_overflow = 0.0
    for row_index, row in enumerate(rows):
        cell_lines: list[int] = []
        for column_index, cell in enumerate(row):
            allocated = max(
                1.0,
                allocated_widths[min(column_index, len(allocated_widths) - 1)],
            )
            width = estimate_text_width_mm(cell)
            lines = max(1, int(math.ceil(width / allocated)))
            token_overflow = max(
                0.0,
                _longest_unbreakable_width_mm(cell) - allocated,
            )
            max_unbreakable_overflow = max(max_unbreakable_overflow, token_overflow)
            cell_lines.append(lines)
            max_cell_lines = max(max_cell_lines, lines)
            if row_index == 0:
                max_header_lines = max(max_header_lines, lines)
        row_line_counts.append(max(cell_lines or [1]))
    data_rows = row_line_counts[1:] or row_line_counts
    average_row_lines = sum(data_rows) / len(data_rows)
    return max_cell_lines, max_header_lines, average_row_lines, max_unbreakable_overflow


def _classify_column(values: Sequence[str]) -> tuple[str, set[str]]:
    header = values[0].lower() if values else ""
    data_values = [value for value in values[1:] if value]
    all_values = [value for value in values if value]
    flags: set[str] = set()
    if any(_URL_RE.search(value) for value in all_values):
        flags.add("url")
    if any("`" in value for value in all_values):
        flags.add("code")
    if any(_contains_cjk(value) for value in all_values):
        flags.add("cjk")

    numeric_count = sum(1 for value in data_values if _is_numericish(value))
    code_count = sum(1 for value in data_values if _is_codeish(value))
    avg_words = (
        sum(len(value.split()) for value in data_values) / len(data_values)
        if data_values
        else 0.0
    )
    if data_values and numeric_count / len(data_values) >= 0.7:
        return "numeric", flags
    if (
        "code" in flags
        or any(token in header for token in ("code", "id", "key", "nr", "nummer"))
        or (data_values and code_count / len(data_values) >= 0.7)
    ):
        flags.add("code")
        return "code", flags
    if any(
        token in header
        for token in ("comment", "kommentar", "reason", "begruend", "description")
    ):
        return "prose", flags
    if any(token in header for token in ("status", "level", "grad", "type", "typ")):
        return "status", flags
    if avg_words >= 4.0 or any(len(value) > 48 for value in data_values):
        return "prose", flags
    return "label", flags


def _minimum_width_for_kind(kind: str) -> float:
    return {
        "numeric": 10.0,
        "code": 16.0,
        "status": 20.0,
        "label": 18.0,
        "prose": 34.0,
    }.get(kind, 18.0)


def _longest_unbreakable_width_mm(value: str) -> float:
    text = normalize_table_measurement_text(value)
    current = 0.0
    longest = 0.0
    for char in text:
        width = glyph_width_em(char) * TABLE_FONT_SIZE_PT * PT_TO_MM
        if char.isspace() or char in "-/._,:;|()[]{}":
            longest = max(longest, current)
            current = 0.0
            continue
        if _is_cjk_breakable(char):
            longest = max(longest, width)
            current = 0.0
            continue
        current += width
    return max(longest, current)


def _is_cjk_breakable(char: str) -> bool:
    codepoint = ord(char)
    return (
        0x3040 <= codepoint <= 0x30FF
        or 0x3400 <= codepoint <= 0x9FFF
        or 0xAC00 <= codepoint <= 0xD7AF
    )


def is_table_script_breakable(char: str) -> bool:
    """Return whether a table cell may break after this script character."""

    return _is_cjk_breakable(char)


def _contains_cjk(value: str) -> bool:
    return any(_is_cjk_breakable(char) for char in value)


def _is_numericish(value: str) -> bool:
    stripped = value.strip()
    return bool(stripped) and bool(re.fullmatch(r"[-+0-9.,% /]+", stripped))


def _is_codeish(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return False
    if " " in stripped:
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9_.:/@#%+-]+", stripped))


def _strip_html_tags(value: str) -> str:
    if not value:
        return ""
    return _HTML_TAG.sub("", value).strip()


def _paper_from_candidate(raw: Any) -> PaperInfo:
    if isinstance(raw, PaperInfo):
        return raw
    if isinstance(raw, str):
        return get_valid_paper_measurements(raw)
    if isinstance(raw, Mapping):
        paper = str(raw.get("paper") or raw.get("name") or raw.get("code") or "custom")
        landscape = _as_bool(raw.get("landscape"), default=False)
        standard = _as_bool(raw.get("standard"), default="size_mm" not in raw)
        size_mm = _tuple_int(raw.get("size_mm"), length=2)
        margins_mm = _tuple_int(raw.get("margins_mm"), length=4) or (15, 15, 15, 15)
        return get_valid_paper_measurements(
            paper,
            standard=standard,
            landscape=landscape,
            size_mm=size_mm,
            margins_mm=margins_mm,
        )
    raise TypeError(f"Unsupported paper candidate: {raw!r}")


def _parse_override_body(body: str) -> dict[str, str]:
    cleaned = body.strip().lstrip(":").replace(",", " ")
    values: dict[str, str] = {}
    try:
        parts = shlex.split(cleaned)
    except ValueError:
        parts = cleaned.split()
    for part in parts:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        values[key.strip().lower()] = value.strip()
    return values


def _log_and_report_decision(
    decision: TableStrategyDecision, config: TablePaperStrategyConfig
) -> None:
    data = decision_to_dict(decision)
    logger.info(
        "Table strategy decision: selected=%s method=%s columns=%d "
        "estimated_width=%.1fmm reason=%s",
        decision.selected_paper.norm_name,
        decision.method,
        decision.columns,
        decision.estimated_width_mm,
        decision.reason,
    )
    if decision.evaluations:
        logger.info(
            "Table strategy candidate scores: %s",
            json.dumps(data["evaluations"], ensure_ascii=False),
        )
    if config.report_path:
        try:
            config.report_path.parent.mkdir(parents=True, exist_ok=True)
            with config.report_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(data, ensure_ascii=False) + "\n")
        except OSError as exc:
            logger.warning("Could not write table strategy report: %s", exc)


def _as_sequence(value: Any) -> Sequence[Any]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)):
        return (value,)
    if isinstance(value, Sequence):
        return value
    return (value,)


def _as_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _tuple_int(value: Any, *, length: int) -> tuple[int, ...] | None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return None
    if len(value) != length:
        return None
    try:
        return tuple(int(item) for item in value)
    except (TypeError, ValueError):
        return None
