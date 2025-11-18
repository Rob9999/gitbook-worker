#!/usr/bin/env python3
"""Combine multiple Markdown files into a single document.

Each input file is preprocessed using ``preprocess_md.py`` before being
normalized and concatenated with a page break.
"""
from __future__ import annotations

import argparse
import re
import sys
from typing import List

from tools.logging_config import get_logger
from tools.publishing import preprocess_md
from tools.publishing.geometry_package_injector import add_geometry_package

logger = get_logger(__name__)

_SUBS = {
    "₀": "0",
    "₁": "1",
    "₂": "2",
    "₃": "3",
    "₄": "4",
    "₅": "5",
    "₆": "6",
    "₇": "7",
    "₈": "8",
    "₉": "9",
}


_BRACKET_ESCAPE_RE = re.compile(r"\\\[([^\n\\]*?)\]")


def normalize_md(text: str) -> str:
    """Apply simple substitutions to ``text`` to normalise Markdown."""
    text = _BRACKET_ESCAPE_RE.sub(r"[\1]", text)
    out: List[str] = []
    in_math = False
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "$":
            if i + 1 < len(text) and text[i + 1] == "$":
                in_math = not in_math
                out.append("$$")
                i += 2
                continue
            in_math = not in_math
            out.append("$")
        elif ch in _SUBS:
            digit = _SUBS[ch]
            if in_math:
                out.append(f"_{{{digit}}}")
            else:
                out.append(f"$_{digit}$")
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def combine_markdown(files: List[str], paper_format: str = "a4") -> str:
    """Return a single Markdown string combining ``files``.

    Each file is processed by :mod:`preprocess_md` before normalisation.
    Missing files are skipped with a warning.
    """
    parts: List[str] = []
    for p in files:
        try:
            processed = preprocess_md.process(p, paper_format=paper_format)
            parts.append(normalize_md(processed))
        except Exception as e:  # pragma: no cover - best effort
            logger.warning("Konnte %s nicht lesen: %s", p, e)
    return "\n\n\\newpage\n\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Combine Markdown files with preprocessing"
    )
    parser.add_argument("files", nargs="+", help="Markdown files to combine in order")
    parser.add_argument("-o", "--output", help="Path to output combined Markdown file")
    parser.add_argument(
        "--paper-format",
        help="Enable landscape orientation for wide content",
        default="a4",
    )
    args = parser.parse_args()

    combined = add_geometry_package(
        combine_markdown(args.files, paper_format=args.paper_format),
        paper_format=args.paper_format,
    )
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(combined)
    else:
        sys.stdout.write(combined)


if __name__ == "__main__":
    main()
