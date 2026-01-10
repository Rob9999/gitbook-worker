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
from typing import Iterable, List

from gitbook_worker.tools.logging_config import get_logger

from gitbook_worker.tools.utils.image_info import get_image_width


from gitbook_worker.tools.publishing.paper_info import (
    PaperInfo,
    get_valid_paper_measurements,
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


COLUMN_WIDTH_mm = 25  # Annahme: 25mm pro Spalte (inkl. Abstand)
COLUMN_HEIGHT_mm = 10  # Annahme: 10mm pro Spalte (inkl. Abstand)
PIXELS_PER_MM = 11.81  # bei 300 dpi (1 inch = 25.4 mm, 300/25.4 ≈ 11.81)
MIN_COLS_FOR_WRAP = 10


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


def _paper_candidates(base: PaperInfo) -> Iterable[PaperInfo]:
    """Yield candidate papers starting with ``base`` orientation."""

    candidate_codes = [
        "a4",
        "a4-landscape",
        "a3",
        "a3-landscape",
        "a2",
        "a2-landscape",
        "a1",
        "a1-landscape",
    ]

    seen: set[tuple[str, tuple[int, int], tuple[int, int, int, int]]] = set()

    def register(info: PaperInfo) -> Iterable[PaperInfo]:
        key = (info.norm_name, info.size_mm, info.margins_mm)
        if key in seen:
            return []
        seen.add(key)
        return [info]

    for initial in register(base):
        yield initial

    if base.norm_name in candidate_codes:
        start_index = candidate_codes.index(base.norm_name) + 1
    else:
        start_index = 0

    ordered = candidate_codes[start_index:] + candidate_codes[:start_index]
    for code in ordered:
        info = get_valid_paper_measurements(code)
        for item in register(info):
            yield item


def paper_for_columns(
    cols: int,
    rows: int = None,
    *,
    height_mm: int = 297,
    base_paper: PaperInfo | None = None,
) -> PaperInfo:
    """Return required paper info."""
    base_info = base_paper or PaperInfo.default()
    min_width_mm = max(cols * COLUMN_WIDTH_mm, base_info.size_mm[0])
    required_height = 0
    if rows:
        height_mm = max(rows * COLUMN_HEIGHT_mm, base_info.size_mm[1])
        required_height = height_mm

    for candidate in _paper_candidates(base_info):
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


def wrap_block(
    lines: List[str],
    paper_info: PaperInfo,
    current_paper_info: PaperInfo = PaperInfo.default(),
) -> List[str]:
    """Wrap ``lines`` with LaTeX to switch to ``paper_info``.

    Landscape mode is optional. Paper sizes are specified explicitly in
    millimetres rather than by name to ensure consistent behaviour across
    LaTeX engines. Using names like ``a3paper`` occasionally resulted in PDFs
    not respecting the intended page size, particularly when switching
    between formats mid-document.
    """

    def convert_table_to_latex(lines: List[str]) -> str:
        """Convert Markdown pipe tables in ``text`` to LaTeX ``longtable`` blocks."""

        out_lines: list[str] = []
        i = 0

        while i < len(lines):
            line = lines[i]
            if (
                "|" in line
                and i + 1 < len(lines)
                and re.match(r"^\s*\|?\s*:?-+", lines[i + 1])
            ):
                header = [
                    _escape_table_text(x.strip())
                    for x in line.strip().strip("|").split("|")
                ]
                alignments = [
                    x.strip() for x in lines[i + 1].strip().strip("|").split("|")
                ]
                column_specs: list[str] = []
                for align in alignments:
                    if align.startswith(":") and align.endswith(":"):
                        column_specs.append("c")
                    elif align.endswith(":"):
                        column_specs.append("r")
                    else:
                        column_specs.append("l")
                out_lines.append(
                    "\\begin{longtable}{@{}" + "".join(column_specs) + "@{}}"
                )
                out_lines.append("\\toprule ")
                out_lines.append(f"{' & '.join(header)} \\\\")
                out_lines.append("\\midrule ")
                out_lines.append("\\endhead ")
                i += 2
                while i < len(lines) and "|" in lines[i] and lines[i].strip():
                    row = [
                        _escape_table_text(x.strip())
                        for x in lines[i].strip().strip("|").split("|")
                    ]
                    out_lines.append(f"{' & '.join(row)} \\\\")
                    i += 1
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
    before += "\n" + f"\\pagewidth={width}mm" + "\n" + f"\\pageheight={height}mm"
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


def process(path: str, paper_format: str = "a4") -> str:
    """Process ``path`` and return transformed Markdown content."""
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    lines = _convert_html_figures(lines)
    current_file = Path(path).resolve()
    lines = _rewrite_internal_links(lines, current_file=current_file)

    out: List[str] = []
    i = 0
    base_dir = os.path.dirname(os.path.abspath(path))
    current_paper_info = get_valid_paper_measurements(paper_format)
    while i < len(lines):
        line = lines[i]

        # Detect GitHub-style tables
        if (
            "|" in line
            and i + 1 < len(lines)
            and re.match(r"^\s*\|?\s*:?[-]+", lines[i + 1])
        ):
            table_lines = [line, lines[i + 1]]
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                table_lines.append(lines[i])
                i += 1
            cols = table_lines[0].count("|") - 1
            paper_info = paper_for_columns(cols=cols, base_paper=current_paper_info)
            escaped_lines = [_escape_table_line(l) for l in table_lines]
            logger.info(
                "In document '%s': Detected table with %d columns, paper: %s",
                path,
                cols,
                paper_info,
            )
            should_wrap = paper_info != current_paper_info or cols >= MIN_COLS_FOR_WRAP
            if should_wrap:
                prefix: List[str] = []
                # include heading, note and blank lines before the table
                while out and (
                    out[-1].strip() == ""
                    or out[-1].lstrip().startswith("#")
                    or out[-1].lstrip().startswith(">")
                ):
                    prefix.insert(0, out.pop())
                out.extend(
                    wrap_block(
                        prefix + escaped_lines,
                        paper_info=paper_info,
                        current_paper_info=current_paper_info,
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
    setup_logging()
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
