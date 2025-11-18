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
from typing import Iterable, List

from tools.logging_config import get_logger


from tools.publishing.paper_info import PaperInfo, get_valid_paper_measurements


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

try:
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover - Pillow optional
    Image = None  # type: ignore

logger = get_logger(__name__)


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
        safe_alt = alt.replace("\"", r"\"")
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
        if width >= min_width_mm and (required_height == 0 or height >= required_height):
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

def _escape_ampersands(value: str) -> str:
    return re.sub(r"(?<!\\)&", r"\\&", value)


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
                    _escape_ampersands(x.strip())
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
                        _escape_ampersands(x.strip())
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
            escaped_lines = [_escape_ampersands(l) for l in table_lines]
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
            width = 0
            if Image and os.path.exists(abs_img):
                try:
                    with Image.open(abs_img) as im:
                        width = im.width
                except Exception:  # pragma: no cover - best effort
                    logger.warning("Could not open image %s to get size.", abs_img)
                    width = 0
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

    return "".join(out)


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
