#!/usr/bin/env python3
"""Preprocess Markdown to handle wide tables and large images.

This script scans a Markdown file and wraps overly wide tables or images in
LaTeX snippets that switch the page orientation or size.  It aims to keep
content readable when converted to PDF via Pandoc.

- Tables with many columns are placed on landscape pages and, if required,
  larger paper formats (A3–A1).
- Images wider than the target page receive the same treatment.

The thresholds are heuristic and can be adjusted in the constants below.
"""

from __future__ import annotations

import argparse
import os
import re
from html import unescape
from pathlib import Path
from typing import Any, List, Mapping

from gitbook_worker.tools.logging_config import get_logger

from gitbook_worker.tools.utils.image_info import get_image_width


from gitbook_worker.tools.publishing.paper_info import (
    PaperInfo,
    get_valid_paper_measurements,
)
from gitbook_worker.tools.publishing.table_strategy import (
    COLUMN_HEIGHT_MM,
    COLUMN_WIDTH_MM,
    MIN_COLS_FOR_WRAP,
    MIN_TABLE_COLUMN_WIDTH_MM,
    PIXELS_PER_MM,
    PT_TO_MM,
    TABLE_CELL_PADDING_MM,
    TABLE_FONT_SIZE_PT,
    TABLE_WIDTH_SAFETY_FACTOR,
    TablePaperStrategyConfig,
    available_text_width_mm,
    evaluate_candidate_layout,
    estimate_table_width_mm,
    estimate_text_width_mm,
    glyph_width_em,
    is_table_separator_row,
    is_table_script_breakable,
    iter_paper_candidates,
    paper_for_columns,
    paper_for_table,
    paper_for_table_width,
    parse_table_override_from_context,
    parse_table_strategy_config,
    split_table_row,
    table_column_count,
)

_FIGURE_START = re.compile(r"<figure\b", re.IGNORECASE)
_FIGURE_END = re.compile(r"</figure>", re.IGNORECASE)
_IMG_TAG = re.compile(
    r"<img\b[^>]*src=[\"\'](?P<src>[^\"\']+)[\"\'][^>]*?"
    r"(?:alt=[\"\'](?P<alt>[^\"\']*)[\"\'][^>]*)?>",
    re.IGNORECASE | re.DOTALL,
)
_FIGCAPTION = re.compile(
    r"<figcaption\b[^>]*>(?P<caption>.*?)</figcaption>",
    re.IGNORECASE | re.DOTALL,
)
_HTML_TAG = re.compile(r"<[^>]+>")

logger = get_logger(__name__)


_MARKDOWN_LINK_RE = re.compile(r"(?<!\!)\[(?P<label>[^\]]+)\]\((?P<inner>[^)]+)\)")
_URL_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
_ANCHOR_CACHE: dict[Path, str] = {}
_ANCHOR_ROOT_HINTS = ("content",)
_TABLE_CONTEXT_MAX_PARAGRAPH_LINES = 3
_TABLE_CONTEXT_MAX_BLOCKQUOTE_LINES = 6
_TABLE_CONTEXT_MAX_LEGEND_TABLE_LINES = 12
_TABLE_PACKET_MAX_LEAD_LINES = 18
_TABLE_PACKET_MAX_EXTRA_TABLES = 1
_TABLE_PACKET_MAX_EXTRA_TABLE_LINES = 8
_TABLE_PACKET_MAX_REFERENCE_LINES = 6
_TABLE_PACKET_HEIGHT_SAFETY_FACTOR = 0.92
_TABLE_CONTEXT_LEGEND_RE = re.compile(
    r"\b(legende|legend|zeichenerkl[aä]rung)\b", re.IGNORECASE
)
_TABLE_CONTEXT_TRAILING_REFERENCE_RE = re.compile(
    r"\b(querverweise|quellen\s*(?:&|und)\s*verweise|references|"
    r"sources?\s*(?:&|and)\s*references|cross[-\s]?references|see also)\b",
    re.IGNORECASE,
)
_MARKDOWN_LIST_ITEM_RE = re.compile(r"^(?:[-*+]\s+|\d+[.)]\s+)")
_TABLE_STRONG_RE = re.compile(r"(?<!\\)\*\*(?P<text>.+?)(?<!\\)\*\*")


COLUMN_WIDTH_mm = COLUMN_WIDTH_MM
COLUMN_HEIGHT_mm = COLUMN_HEIGHT_MM
_paper_candidates = iter_paper_candidates
_split_table_row = split_table_row
_is_table_separator_row = is_table_separator_row
_table_column_count = table_column_count
_glyph_width_em = glyph_width_em

__all__ = [
    "COLUMN_WIDTH_mm",
    "COLUMN_HEIGHT_mm",
    "MIN_COLS_FOR_WRAP",
    "TABLE_FONT_SIZE_PT",
    "PT_TO_MM",
    "MIN_TABLE_COLUMN_WIDTH_MM",
    "TABLE_CELL_PADDING_MM",
    "TABLE_WIDTH_SAFETY_FACTOR",
    "available_text_width_mm",
    "estimate_text_width_mm",
    "estimate_table_width_mm",
    "paper_for_table_width",
    "paper_for_table",
    "paper_for_columns",
    "paper_for_width",
    "process",
]


def _strip_html_tags(value: str) -> str:
    if not value:
        return ""
    return unescape(_HTML_TAG.sub("", value)).strip()


def _convert_figure_block(block: str) -> List[str]:
    match = _IMG_TAG.search(block)
    if not match:
        return block.splitlines(keepends=True)
    src = (match.group("src") or "").strip()
    alt_raw = match.group("alt") or ""
    alt = unescape(alt_raw).strip()
    if not src:
        return block.splitlines(keepends=True)

    caption_match = _FIGCAPTION.search(block)
    caption = _strip_html_tags(caption_match.group("caption")) if caption_match else ""

    alt_text = caption or alt or "Image"
    safe_alt_text = alt_text.replace("[", r"\[").replace("]", r"\]")
    attrs = ""
    if alt and alt_text != alt:
        safe_alt = alt.replace('"', r"\"")
        attrs = f'{{fig-alt="{safe_alt}"}}'

    markdown_line = f"![{safe_alt_text}]({src}){attrs}\n"
    if caption and caption != alt_text:
        markdown_line += f"\n{caption}\n"
    return [markdown_line]


def _convert_html_figures(lines: List[str]) -> List[str]:
    if not lines:
        return []

    result: List[str] = []
    buffer: List[str] = []
    in_figure = False

    for line in lines:
        if in_figure:
            buffer.append(line)
            if _FIGURE_END.search(line):
                result.extend(_convert_figure_block("".join(buffer)))
                buffer = []
                in_figure = False
            continue

        if _FIGURE_START.search(line):
            buffer = [line]
            in_figure = True
            if _FIGURE_END.search(line):
                result.extend(_convert_figure_block("".join(buffer)))
                buffer = []
                in_figure = False
            continue

        result.append(line)

    if buffer:
        # Unclosed figures fall back to the original content
        result.extend(buffer)

    return result


def _split_link_destination(inner: str) -> tuple[str, str]:
    """Split Markdown link destination into URL and trailing suffix."""

    if not inner:
        return "", ""

    trimmed = inner.lstrip()
    leading = inner[: len(inner) - len(trimmed)]
    if not trimmed:
        return "", inner

    if trimmed.startswith("<"):
        end = trimmed.find(">")
        if end != -1:
            url = trimmed[1:end]
            rest = trimmed[end + 1 :]
            return url, leading + rest

    for idx, char in enumerate(trimmed):
        if char.isspace():
            return trimmed[:idx], leading + trimmed[idx:]

    return trimmed, leading


def _is_external_target(target: str) -> bool:
    target_strip = target.strip()
    if not target_strip:
        return True
    if target_strip.startswith(("#", "mailto:", "tel:")):
        return True
    if target_strip.startswith("//"):
        return True
    if _URL_SCHEME_RE.match(target_strip):
        return True
    return False


def _relative_parts(resolved: Path) -> list[str]:
    """Return path parts used for anchor generation."""

    try:
        normalized = resolved.resolve()
    except OSError:
        normalized = resolved

    without_suffix = normalized.with_suffix("")
    parts = [part for part in without_suffix.parts if part not in {os.sep, ""}]
    lowered = [part.lower() for part in parts]

    for hint in _ANCHOR_ROOT_HINTS:
        if hint in lowered:
            index = lowered.index(hint)
            tail = parts[index + 1 :]
            if tail:
                return tail

    if parts:
        return parts[-3:]

    stem = normalized.stem or normalized.name
    return [stem or "section"]


def _anchor_from_path(path: Path) -> str:
    """Return a deterministic anchor ID for *path*."""

    try:
        resolved = path.resolve()
    except OSError:
        resolved = path

    cached = _ANCHOR_CACHE.get(resolved)
    if cached:
        return cached

    parts = _relative_parts(resolved)
    slug_source = "-".join(parts)
    slug = re.sub(r"[^0-9a-z]+", "-", slug_source.lower()).strip("-")
    if not slug:
        slug = "section"
    anchor = f"md-{slug}"
    _ANCHOR_CACHE[resolved] = anchor
    return anchor


def _insert_anchor(body: str, anchor: str) -> str:
    """Insert the anchor *after* YAML front matter if present."""

    anchor_line = f'<a id="{anchor}"></a>\n\n'  # the second newline is very important for separating from a succeeding header (e.g. # Title), content would otherwise be corrupted while rendering the markdown (also for pdf)
    if not body.startswith("---"):
        return anchor_line + body

    lines = body.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return anchor_line + body

    closing_index: int | None = None
    for idx, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = idx
            break

    if closing_index is None:
        return anchor_line + body

    before = "".join(lines[: closing_index + 1])
    after = "".join(lines[closing_index + 1 :])
    return before + anchor_line + after


def _rewrite_link_target(target: str, *, base_dir: Path) -> str | None:
    if _is_external_target(target):
        return None

    path_part, _, fragment = target.partition("#")
    if not path_part.lower().endswith((".md", ".markdown")):
        return None

    candidate = Path(path_part.replace("\\", os.sep))
    try:
        resolved = (
            (base_dir / candidate).resolve()
            if not candidate.is_absolute()
            else candidate.resolve()
        )
    except OSError:
        resolved = (base_dir / candidate).absolute()

    if not resolved.exists():
        return None

    if fragment:
        return f"#{fragment}"

    anchor = _anchor_from_path(resolved)
    return f"#{anchor}"


def _rewrite_internal_links(lines: List[str], *, current_file: Path) -> List[str]:
    """Rewrite relative Markdown links to PDF-friendly anchors."""

    base_dir = current_file.parent
    rewritten: List[str] = []
    in_fence = False
    fence_marker = ""

    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif stripped.startswith(fence_marker):
                in_fence = False
                fence_marker = ""
            rewritten.append(line)
            continue

        if in_fence:
            rewritten.append(line)
            continue

        def _replace(match: re.Match[str]) -> str:
            label = match.group("label")
            inner = match.group("inner")
            url, suffix = _split_link_destination(inner)
            if not url:
                return match.group(0)
            new_target = _rewrite_link_target(url, base_dir=base_dir)
            if not new_target:
                return match.group(0)
            return f"[{label}]({new_target}{suffix})"

        rewritten.append(_MARKDOWN_LINK_RE.sub(_replace, line))

    return rewritten


def paper_for_width(px: int, *, base_paper: PaperInfo | None = None) -> PaperInfo:
    """Return required paper size for image width."""
    base_info = base_paper or PaperInfo.default()
    min_width_mm = max(px / PIXELS_PER_MM, base_info.size_mm[0])
    for candidate in _paper_candidates(base_info):
        if candidate.size_mm[0] >= min_width_mm:
            return candidate

    logger.warning(
        "Image requires custom paper width %.2fmm; falling back to %s.",
        min_width_mm,
        base_info.norm_name,
    )
    return base_info


def _escape_table_text(value: str) -> str:
    """Escape LaTeX specials in table cells without double-escaping.

    Keeps math segments ($...$) untouched to avoid breaking formulas.
    """

    parts = re.split(r"(\$[^$]*\$)", value)
    escaped: list[str] = []
    for part in parts:
        if part.startswith("$") and part.endswith("$"):
            escaped.append(part)
            continue
        escaped.append(re.sub(r"(?<!\\)([_&#%])", r"\\\1", part))
    return "".join(escaped)


def _escape_table_line(line: str) -> str:
    if "|" not in line:
        return line
    segments = line.split("|")
    escaped_segments = [segments[0]]
    for segment in segments[1:-1]:
        escaped_segments.append(_escape_table_text(segment))
    escaped_segments.append(segments[-1])
    return "|".join(escaped_segments)


def _add_table_script_break_hints(text: str) -> str:
    """Add LaTeX break hints for scripts that naturally break by character."""

    if not text:
        return text
    out: list[str] = []
    for index, char in enumerate(text):
        out.append(char)
        if not is_table_script_breakable(char):
            continue
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if next_char and not next_char.isspace():
            out.append(r"\allowbreak{}")
    return "".join(out)


def _table_markdown_inline_to_latex(text: str) -> str:
    return _TABLE_STRONG_RE.sub(
        lambda match: r"\textbf{" + match.group("text") + "}", text
    )


def _format_latex_table_cell(value: str) -> str:
    escaped = _escape_table_text(value.strip())
    formatted = _table_markdown_inline_to_latex(escaped)
    return _add_table_script_break_hints(formatted)


def _is_blank_line(line: str) -> bool:
    return not line.strip()


def _is_heading_line(line: str) -> bool:
    return line.lstrip().startswith("#")


def _heading_level(line: str) -> int:
    stripped = line.lstrip()
    if not stripped.startswith("#"):
        return 0
    return len(stripped) - len(stripped.lstrip("#"))


def _is_blockquote_line(line: str) -> bool:
    return line.lstrip().startswith(">")


def _is_thematic_break_line(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and bool(re.fullmatch(r"(?:[-*_]\s*){3,}", stripped))


def _is_table_row_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and "|" in stripped[1:]


def _is_table_start(lines: List[str], index: int) -> bool:
    return (
        index + 1 < len(lines)
        and "|" in lines[index]
        and _is_table_separator_row(lines[index + 1])
    )


def _is_paragraph_context_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if _is_thematic_break_line(line):
        return False
    if stripped.startswith(("#", ">", "|", "```", "~~~", "<!--")):
        return False
    if re.match(r"^(?:[-*+]\s+|\d+[.)]\s+)", stripped):
        return False
    return True


def _is_reference_context_line(line: str) -> bool:
    stripped = line.strip()
    return (
        _is_paragraph_context_line(line)
        or _is_blockquote_line(line)
        or bool(_MARKDOWN_LIST_ITEM_RE.match(stripped))
    )


def _is_trailing_reference_heading(line: str) -> bool:
    return _is_heading_line(line) and bool(
        _TABLE_CONTEXT_TRAILING_REFERENCE_RE.search(line)
    )


def _has_candidate_body(lines: List[str]) -> bool:
    seen_heading = False
    for line in lines:
        if not seen_heading:
            seen_heading = _is_heading_line(line)
            continue
        if _is_reference_context_line(line):
            return True
    return False


def _is_complete_short_trailing_section(lines: List[str], index: int) -> bool:
    if index >= len(lines):
        return True
    return _is_heading_line(lines[index]) or _is_thematic_break_line(lines[index])


def _read_short_trailing_reference_section(
    lines: List[str], index: int
) -> tuple[List[str], int]:
    start = index
    candidate: list[str] = []
    while index < len(lines) and _is_blank_line(lines[index]):
        candidate.append(lines[index])
        index += 1

    if index >= len(lines) or not _is_trailing_reference_heading(lines[index]):
        return [], start

    candidate.append(lines[index])
    index += 1
    while index < len(lines) and _is_blank_line(lines[index]):
        candidate.append(lines[index])
        index += 1

    body_lines = 0
    while index < len(lines) and _is_reference_context_line(lines[index]):
        if body_lines >= _TABLE_PACKET_MAX_REFERENCE_LINES:
            return [], start
        candidate.append(lines[index])
        index += 1
        body_lines += 1

    while index < len(lines) and _is_blank_line(lines[index]):
        candidate.append(lines[index])
        index += 1

    if body_lines == 0 or not _is_complete_short_trailing_section(lines, index):
        return [], start
    return candidate, index


def _pop_trailing_blanks(lines: List[str]) -> List[str]:
    popped: list[str] = []
    while lines and _is_blank_line(lines[-1]):
        popped.insert(0, lines.pop())
    return popped


def _pop_context_blockquotes(lines: List[str]) -> List[str]:
    end = len(lines)
    start = end
    while start > 0 and _is_blockquote_line(lines[start - 1]):
        start -= 1
    if start == end or end - start > _TABLE_CONTEXT_MAX_BLOCKQUOTE_LINES:
        return []
    block = lines[start:end]
    del lines[start:end]
    return block


def _pop_context_paragraph(lines: List[str]) -> List[str]:
    end = len(lines)
    start = end
    while start > 0 and _is_paragraph_context_line(lines[start - 1]):
        start -= 1
    if start == end or end - start > _TABLE_CONTEXT_MAX_PARAGRAPH_LINES:
        return []
    block = lines[start:end]
    del lines[start:end]
    return block


def _find_legend_context_start(lines: List[str], heading_index: int) -> int:
    context_start = heading_index
    probe = heading_index
    while probe > 0 and _is_blank_line(lines[probe - 1]):
        probe -= 1

    paragraph_end = probe
    paragraph_start = paragraph_end
    while paragraph_start > 0 and _is_paragraph_context_line(
        lines[paragraph_start - 1]
    ):
        paragraph_start -= 1
    if (
        paragraph_start < paragraph_end
        and paragraph_end - paragraph_start <= _TABLE_CONTEXT_MAX_PARAGRAPH_LINES
    ):
        context_start = paragraph_start

    probe = context_start
    while probe > 0 and _is_blank_line(lines[probe - 1]):
        probe -= 1
    if probe > 0 and _is_heading_line(lines[probe - 1]):
        context_start = probe - 1

    return context_start


def _pop_preceding_legend_table_context(lines: List[str]) -> List[str]:
    table_context_end = len(lines)
    table_end = table_context_end
    while table_end > 0 and _is_blank_line(lines[table_end - 1]):
        table_end -= 1
    if table_end <= 0 or not _is_table_row_line(lines[table_end - 1]):
        return []

    table_start = table_end
    while table_start > 0 and _is_table_row_line(lines[table_start - 1]):
        table_start -= 1

    table_line_count = table_end - table_start
    if table_line_count > _TABLE_CONTEXT_MAX_LEGEND_TABLE_LINES:
        return []
    if not any(is_table_separator_row(line) for line in lines[table_start:table_end]):
        return []

    heading_index = table_start
    while heading_index > 0 and _is_blank_line(lines[heading_index - 1]):
        heading_index -= 1
    if heading_index <= 0:
        return []

    heading_line_index = heading_index - 1
    heading_line = lines[heading_line_index]
    if not _is_heading_line(heading_line):
        return []
    if not _TABLE_CONTEXT_LEGEND_RE.search(heading_line):
        return []

    context_start = _find_legend_context_start(lines, heading_line_index)
    block = lines[context_start:table_context_end]
    del lines[context_start:table_context_end]
    return block


def _pop_table_context(lines: List[str]) -> List[str]:
    prefix: list[str] = []

    while True:
        prefix[0:0] = _pop_trailing_blanks(lines)

        blockquotes = _pop_context_blockquotes(lines)
        if blockquotes:
            prefix[0:0] = blockquotes
            continue

        paragraph = _pop_context_paragraph(lines)
        if paragraph:
            prefix[0:0] = paragraph
            continue

        if lines and _is_heading_line(lines[-1]):
            prefix.insert(0, lines.pop())
            legend_context = _pop_preceding_legend_table_context(lines)
            if legend_context:
                prefix[0:0] = legend_context
            break

        break

    return prefix


def _has_wrapped_or_table_content(lines: List[str]) -> bool:
    return any(
        _is_table_row_line(line)
        or "\\newgeometry" in line
        or "\\restoregeometry" in line
        or "\\begin{longtable}" in line
        for line in lines
    )


def _pop_section_packet_lead(lines: List[str]) -> List[str]:
    end = len(lines)
    while end > 0 and _is_blank_line(lines[end - 1]):
        end -= 1
    if end <= 0:
        return []

    start = end - 1
    while start >= 0:
        if _heading_level(lines[start]) == 1:
            break
        start -= 1
    if start < 0:
        return []

    block = lines[start:]
    content_block = lines[start:end]
    if len(content_block) > _TABLE_PACKET_MAX_LEAD_LINES:
        return []
    if _has_wrapped_or_table_content(content_block):
        return []

    del lines[start:]
    return block


def _read_table_block(lines: List[str], index: int) -> tuple[List[str], int]:
    table_lines = [lines[index], lines[index + 1]]
    index += 2
    while index < len(lines) and "|" in lines[index] and lines[index].strip():
        table_lines.append(lines[index])
        index += 1
    return table_lines, index


def _trim_trailing_blank_lines(lines: List[str]) -> None:
    while lines and _is_blank_line(lines[-1]):
        lines.pop()


def _collect_wrapped_packet_suffix(
    lines: List[str], index: int
) -> tuple[List[str], int]:
    suffix: list[str] = []
    extra_tables = 0

    while index < len(lines):
        pending_blanks: list[str] = []
        while index < len(lines) and _is_blank_line(lines[index]):
            pending_blanks.append(lines[index])
            index += 1

        if index >= len(lines):
            suffix.extend(pending_blanks)
            return suffix, index

        line = lines[index]
        if _is_thematic_break_line(line):
            separator = pending_blanks + [line]
            index += 1
            while index < len(lines) and _is_blank_line(lines[index]):
                separator.append(lines[index])
                index += 1

            trailing_reference, reference_index = (
                _read_short_trailing_reference_section(lines, index)
            )
            suffix.extend(separator)
            if trailing_reference:
                suffix.extend(trailing_reference)
                return suffix, reference_index
            return suffix, index

        if _is_heading_line(line):
            if extra_tables >= _TABLE_PACKET_MAX_EXTRA_TABLES:
                _trim_trailing_blank_lines(suffix)
                return suffix, index - len(pending_blanks)

            candidate_start = index
            candidate = pending_blanks + [line]
            index += 1
            while index < len(lines) and _is_blank_line(lines[index]):
                candidate.append(lines[index])
                index += 1

            paragraph_lines = 0
            while (
                index < len(lines)
                and _is_paragraph_context_line(lines[index])
                and paragraph_lines < _TABLE_CONTEXT_MAX_PARAGRAPH_LINES
            ):
                candidate.append(lines[index])
                index += 1
                paragraph_lines += 1
            while index < len(lines) and _is_blank_line(lines[index]):
                candidate.append(lines[index])
                index += 1

            if not _is_table_start(lines, index):
                if (
                    _is_trailing_reference_heading(line)
                    and _has_candidate_body(candidate)
                    and _is_complete_short_trailing_section(lines, index)
                ):
                    suffix.extend(candidate)
                    return suffix, index
                _trim_trailing_blank_lines(suffix)
                return suffix, candidate_start - len(pending_blanks)

            table_lines, index = _read_table_block(lines, index)
            if len(table_lines) > _TABLE_PACKET_MAX_EXTRA_TABLE_LINES:
                _trim_trailing_blank_lines(suffix)
                return suffix, candidate_start - len(pending_blanks)

            suffix.extend(candidate)
            suffix.extend(_escape_table_line(table_line) for table_line in table_lines)
            extra_tables += 1
            continue

        if _is_paragraph_context_line(line) or _is_blockquote_line(line):
            suffix.extend(pending_blanks)
            paragraph_lines = 0
            while index < len(lines) and (
                _is_paragraph_context_line(lines[index])
                or _is_blockquote_line(lines[index])
            ):
                suffix.append(lines[index])
                index += 1
                paragraph_lines += 1
                if paragraph_lines >= _TABLE_CONTEXT_MAX_PARAGRAPH_LINES:
                    break
            continue

        _trim_trailing_blank_lines(suffix)
        return suffix, index - len(pending_blanks)

    return suffix, index


def _collapse_trailing_newpage_before_wrap(lines: List[str]) -> None:
    if not lines:
        return
    marker = "\n\\newpage\n"
    if lines[-1].endswith(marker):
        lines[-1] = lines[-1][: -len(marker)] + "\n"


def _usable_height_mm(paper_info: PaperInfo) -> float:
    _, top, _, bottom = paper_info.margins_mm
    return max(1.0, paper_info.size_mm[1] - top - bottom)


def _standard_paper_candidates_for_height(base_paper: PaperInfo) -> list[PaperInfo]:
    codes = ["a4", "a3", "a2", "a1"]
    candidates: list[PaperInfo] = []
    for code in codes:
        candidate_code = f"{code}-landscape" if base_paper.rotated else code
        candidate = get_valid_paper_measurements(candidate_code)
        if (
            candidate.size_mm[0] >= base_paper.size_mm[0]
            and candidate.size_mm[1] >= base_paper.size_mm[1]
        ):
            candidates.append(candidate)
    return candidates or [base_paper]


def _estimate_text_block_height_mm(line: str, paper_info: PaperInfo) -> float:
    stripped = line.strip()
    if not stripped:
        return 2.0
    if _is_thematic_break_line(line):
        return 4.0
    level = _heading_level(line)
    if level == 1:
        return 14.0
    if level == 2:
        return 11.0
    if level >= 3:
        return 9.0

    usable_width = available_text_width_mm(paper_info)
    estimated_lines = max(1, int(estimate_text_width_mm(stripped) / usable_width) + 1)
    return estimated_lines * 5.0


def _estimate_table_block_height_mm(
    table_lines: List[str],
    paper_info: PaperInfo,
    table_strategy_config: TablePaperStrategyConfig,
) -> float:
    evaluation = evaluate_candidate_layout(
        table_lines, paper_info, table_strategy_config
    )
    data_rows = max(0, len(table_lines) - 2)
    header_height = max(6.0, evaluation.max_header_lines * 4.4) + 5.0
    row_height = max(5.2, evaluation.average_row_lines * 4.4 + 1.6)
    return header_height + data_rows * row_height + 7.0


def _estimate_wrapped_block_height_mm(
    lines: List[str],
    paper_info: PaperInfo,
    table_strategy_config: TablePaperStrategyConfig,
) -> float:
    height = 0.0
    index = 0
    while index < len(lines):
        if _is_table_start(lines, index):
            table_lines, index = _read_table_block(lines, index)
            height += _estimate_table_block_height_mm(
                table_lines, paper_info, table_strategy_config
            )
            continue
        height += _estimate_text_block_height_mm(lines[index], paper_info)
        index += 1
    return height


def _paper_for_wrapped_block_height(
    lines: List[str],
    paper_info: PaperInfo,
    table_strategy_config: TablePaperStrategyConfig,
) -> PaperInfo:
    if not paper_info.rotated:
        return paper_info

    for candidate in _standard_paper_candidates_for_height(paper_info):
        estimated_height = _estimate_wrapped_block_height_mm(
            lines, candidate, table_strategy_config
        )
        if (
            estimated_height
            <= _usable_height_mm(candidate) * _TABLE_PACKET_HEIGHT_SAFETY_FACTOR
        ):
            return candidate
    return _standard_paper_candidates_for_height(paper_info)[-1]


def wrap_block(
    lines: List[str],
    paper_info: PaperInfo,
    current_paper_info: PaperInfo = PaperInfo.default(),
    table_strategy_config: TablePaperStrategyConfig | None = None,
) -> List[str]:
    """Wrap ``lines`` with LaTeX to switch to ``paper_info``.

    Landscape mode is optional. Paper sizes are specified explicitly in
    millimetres rather than by name to ensure consistent behaviour across
    LaTeX engines. Using names like ``a3paper`` occasionally resulted in PDFs
    not respecting the intended page size, particularly when switching
    between formats mid-document.
    """

    layout_config = table_strategy_config or parse_table_strategy_config(None)

    def _legacy_column_preamble(alignments: List[str]) -> str:
        column_specs: list[str] = []
        for align in alignments:
            if align.startswith(":") and align.endswith(":"):
                column_specs.append("c")
            elif align.endswith(":"):
                column_specs.append("r")
            else:
                column_specs.append("l")
        return "@{}" + "".join(column_specs) + "@{}"

    def _paragraph_alignment(align: str) -> str:
        if align.startswith(":") and align.endswith(":"):
            return r"\centering"
        if align.endswith(":"):
            return r"\raggedleft"
        return r"\raggedright"

    def _paragraph_column_preamble(
        alignments: List[str], table_lines: List[str]
    ) -> str:
        if not layout_config.enabled:
            return _legacy_column_preamble(alignments)

        evaluation = evaluate_candidate_layout(table_lines, paper_info, layout_config)
        widths = evaluation.allocated_widths_mm
        if len(widths) != len(alignments):
            return _legacy_column_preamble(alignments)

        usable_width = available_text_width_mm(paper_info)
        gap_count = max(0, len(widths) - 1)
        gap_mm = 0.0
        if gap_count:
            gap_budget = max(0.0, usable_width - sum(widths))
            gap_mm = min(TABLE_CELL_PADDING_MM, gap_budget / gap_count)

        parts: list[str] = ["@{}"]
        for index, (align, width) in enumerate(zip(alignments, widths)):
            if index:
                parts.append(f"@{{\\hspace{{{gap_mm:.2f}mm}}}}")
            alignment = _paragraph_alignment(align.strip())
            parts.append(
                f">{{{alignment}\\arraybackslash}}p{{{max(1.0, width):.2f}mm}}"
            )
        parts.append("@{}")
        return "".join(parts)

    def convert_table_to_latex(lines: List[str]) -> List[str]:
        """Convert Markdown pipe tables in ``text`` to LaTeX ``longtable`` blocks."""

        out_lines: list[str] = []
        i = 0

        while i < len(lines):
            line = lines[i]
            if (
                "|" in line
                and i + 1 < len(lines)
                and _is_table_separator_row(lines[i + 1])
            ):
                table_lines = [line, lines[i + 1]]
                i += 2
                while i < len(lines) and "|" in lines[i] and lines[i].strip():
                    table_lines.append(lines[i])
                    i += 1

                header = [
                    _format_latex_table_cell(x)
                    for x in _split_table_row(table_lines[0])
                ]
                alignments = _split_table_row(table_lines[1])
                column_preamble = _paragraph_column_preamble(alignments, table_lines)
                out_lines.append(f"\\begin{{longtable}}{{{column_preamble}}}")
                out_lines.append("\\toprule ")
                out_lines.append(f"{' & '.join(header)} \\\\")
                out_lines.append("\\midrule ")
                out_lines.append("\\endhead ")
                for table_line in table_lines[2:]:
                    row = [
                        _format_latex_table_cell(x)
                        for x in _split_table_row(table_line)
                    ]
                    out_lines.append(f"{' & '.join(row)} \\\\")
                out_lines.append("\\bottomrule ")
                out_lines.append("\\end{longtable}")
            else:
                out_lines.append(line)
                i += 1

        return out_lines

    logger.info("Wrapping block with paper info: %s", paper_info)
    width, height = paper_info.size_mm
    margin_left, margin_top, margin_right, margin_bottom = (
        paper_info.margins_mm
    )  # left. top, right bottom margin

    current_width, current_height = current_paper_info.size_mm

    before = "\n" + "\\newpage\n"
    before += (
        f"\\newgeometry{{paperwidth={width}mm, paperheight={height}mm,"
        f" left={margin_left}mm, right={margin_right}mm,"
        f" top={margin_top}mm, bottom={margin_bottom}mm}}\n\n"
    )
    before += "\n" + f"\\pagewidth={width}mm" + "\n" + f"\\pageheight={height}mm\n\n"
    logger.info("Using paper size: %smm x %smm", width, height)
    after = "\n" + "\\restoregeometry"
    after += (
        "\n"
        + f"\\pagewidth={current_width}mm"
        + "\n"
        + f"\\pageheight={current_height}mm"
    )
    after += "\n" + "\\newpage\n"

    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    return [before] + convert_table_to_latex(lines) + [after]


def process(
    path: str,
    paper_format: str = "a4",
    table_strategy: Mapping[str, Any] | TablePaperStrategyConfig | None = None,
) -> str:
    """Process ``path`` and return transformed Markdown content."""
    # Use utf-8-sig to transparently strip a UTF-8 BOM (\ufeff) if present.
    # BOMs can break Pandoc block parsing and lead to missing TOC/bookmarks.
    with open(path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    lines = _convert_html_figures(lines)
    current_file = Path(path).resolve()
    lines = _rewrite_internal_links(lines, current_file=current_file)

    out: List[str] = []
    i = 0
    base_dir = os.path.dirname(os.path.abspath(path))
    current_paper_info = get_valid_paper_measurements(paper_format)
    table_strategy_config = parse_table_strategy_config(table_strategy)
    while i < len(lines):
        line = lines[i]

        # Detect GitHub-style tables
        if "|" in line and i + 1 < len(lines) and _is_table_separator_row(lines[i + 1]):
            table_lines = [line, lines[i + 1]]
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                table_lines.append(lines[i])
                i += 1
            cols = _table_column_count(table_lines)
            table_override = parse_table_override_from_context(out)
            paper_info = paper_for_table(
                table_lines,
                base_paper=current_paper_info,
                config=table_strategy_config,
                override=table_override,
            )
            escaped_lines = [_escape_table_line(l) for l in table_lines]
            logger.info(
                "In document '%s': Detected table with %d columns, paper: %s",
                path,
                cols,
                paper_info,
            )
            should_wrap = paper_info != current_paper_info or cols >= MIN_COLS_FOR_WRAP
            if should_wrap:
                prefix = _pop_table_context(out)
                section_lead = _pop_section_packet_lead(out)
                suffix, i = _collect_wrapped_packet_suffix(lines, i)
                wrapped_lines = section_lead + prefix + escaped_lines + suffix
                paper_info = _paper_for_wrapped_block_height(
                    wrapped_lines,
                    paper_info,
                    table_strategy_config,
                )
                _collapse_trailing_newpage_before_wrap(out)
                out.extend(
                    wrap_block(
                        wrapped_lines,
                        paper_info=paper_info,
                        current_paper_info=current_paper_info,
                        table_strategy_config=table_strategy_config,
                    )
                )
            else:
                out.extend(escaped_lines)
            continue

        # Detect images ![alt](path)
        m = re.match(r"!\[[^\]]*\]\(([^)]+)\)", line.strip())
        if m:
            img = m.group(1).split()[0]
            abs_img = os.path.join(base_dir, img)

            width = get_image_width(Path(abs_img))
            paper_info = paper_for_width(width, base_paper=current_paper_info)
            if paper_info != current_paper_info:
                _collapse_trailing_newpage_before_wrap(out)
                out.extend(
                    wrap_block(
                        [line],
                        paper_info=paper_info,
                        current_paper_info=current_paper_info,
                    )
                )
            else:
                out.append(line)
            i += 1
            continue

        out.append(line)
        i += 1

    body = "".join(out)
    anchor = _anchor_from_path(current_file)
    return _insert_anchor(body, anchor)


def main() -> None:
    # fmt: off
    description_text = (
        "Preprocess Markdown for publishing by adjusting page "
        "size/orientation"
    )
    # fmt: on
    parser = argparse.ArgumentParser(description=description_text)
    parser.add_argument("input", help="Input Markdown file")
    parser.add_argument("output", help="Output Markdown file")
    parser.add_argument(
        "--paper-format",
        help="Enable landscape orientation for wide content",
        default="a4",
    )
    args = parser.parse_args()

    processed = process(args.input, paper_format=args.paper_format)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(processed)


if __name__ == "__main__":
    main()
