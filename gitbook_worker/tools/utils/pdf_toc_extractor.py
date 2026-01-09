"""Extract a PDF table of contents (outlines) for inspection/debugging.

Provides a CLI:
    python -m gitbook_worker.tools.utils.pdf_toc_extractor --pdf path.pdf [--format text|json]

Uses pypdf to read outline entries, returns a flat list of title/page/level.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from pypdf import PdfReader


@dataclass
class TocEntry:
    title: str
    page: int
    level: int


def _flatten_outline(
    outline: Iterable, reader: PdfReader, level: int = 1
) -> List[TocEntry]:
    entries: List[TocEntry] = []
    for item in outline:
        if isinstance(item, list):
            entries.extend(_flatten_outline(item, reader, level=level + 1))
            continue

        title = getattr(item, "title", None) or str(item)
        try:
            page_index = reader.get_destination_page_number(item)
            page_num = page_index + 1
        except Exception:
            page_num = -1
        entries.append(TocEntry(title=title.strip(), page=page_num, level=level))
    return entries


def extract_pdf_toc(pdf_path: Path) -> List[TocEntry]:
    reader = PdfReader(str(pdf_path))
    outline = getattr(reader, "outline", None) or getattr(reader, "outlines", None)
    if not outline:
        return []
    return _flatten_outline(outline, reader)


def _format_text(entries: List[TocEntry]) -> str:
    lines: List[str] = []
    for entry in entries:
        indent = "  " * (entry.level - 1)
        page = "?" if entry.page < 1 else str(entry.page)
        lines.append(f"{indent}- {entry.title} .... {page}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract PDF outlines/TOC")
    parser.add_argument("--pdf", required=True, type=Path, help="Path to PDF file")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    args = parser.parse_args()

    entries = extract_pdf_toc(args.pdf)
    if args.format == "json":
        payload = [entry.__dict__ for entry in entries]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(_format_text(entries))


if __name__ == "__main__":
    main()
