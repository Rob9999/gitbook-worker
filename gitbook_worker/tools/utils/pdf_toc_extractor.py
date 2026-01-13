"""Extract a PDF table of contents (outlines) for inspection/debugging.

Provides a CLI:
    python -m gitbook_worker.tools.utils.pdf_toc_extractor --pdf path.pdf [--format text|json]

Implementation note:
    This CLI is a thin adapter that delegates extraction to the core
    application use-case (Ports & Adapters / Hexagonal Architecture).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from gitbook_worker.core.application.pdf_toc import extract_pdf_toc
from gitbook_worker.core.ports.pdf_toc import PdfTocEntry


def _format_text(entries: list[PdfTocEntry]) -> str:
    lines: list[str] = []
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

    # Windows default code pages (e.g. cp1252) can choke on TOC titles containing
    # emoji or other unicode characters. Keep the active encoding (so PowerShell
    # doesn't mis-decode output), but make writes resilient.
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass

    entries = extract_pdf_toc(args.pdf)
    if args.format == "json":
        payload = [entry.__dict__ for entry in entries]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(_format_text(entries))


if __name__ == "__main__":
    main()
