"""Generate emoji usage summaries for Markdown content."""

from __future__ import annotations

import argparse
import json
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

LOGGER = logging.getLogger(__name__)

EMOJI_BLOCKS: List[Tuple[str, int, int]] = [
    ("Emoticons", 0x1F600, 0x1F64F),
    ("Transport and Map Symbols", 0x1F680, 0x1F6FF),
    ("Misc Symbols and Pictographs", 0x1F300, 0x1F5FF),
    ("Supplemental Symbols and Pictographs", 0x1F900, 0x1F9FF),
    ("Symbols and Pictographs Extended-A", 0x1FA70, 0x1FAFF),
    ("Miscellaneous Symbols", 0x2600, 0x26FF),
    ("Dingbats", 0x2700, 0x27BF),
    ("Flags", 0x1F1E6, 0x1F1FF),
    ("Alchemical Symbols", 0x1F700, 0x1F77F),
    ("Enclosed Alphanumeric Supplement", 0x1F100, 0x1F1FF),
]

EMOJI_PATTERN = re.compile(r"[^\u0000-\u007F\u00A0-\u024F]+")


def iter_emoji_chars(text: str) -> Iterable[str]:
    """Yield every emoji-like character encountered in ``text``."""

    for group in EMOJI_PATTERN.findall(text):
        for char in group:
            yield char


def classify_char(char: str) -> str:
    """Return the Unicode block name for ``char`` or ``"Unknown"``."""

    codepoint = ord(char)
    for name, start, end in EMOJI_BLOCKS:
        if start <= codepoint <= end:
            return name
    return "Unknown"


def count_blocks(text: str) -> Dict[str, int]:
    """Return a mapping of Unicode block names to usage counts."""

    counts: Dict[str, int] = defaultdict(int)
    for char in iter_emoji_chars(text):
        counts[classify_char(char)] += 1
    return dict(counts)


def render_table(counts: Dict[str, int]) -> str:
    """Render ``counts`` into a Markdown table sorted by frequency."""

    rows = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    lines = ["| Unicode Block | Count |", "| --- | --- |"]
    for name, total in rows:
        lines.append(f"| {name} | {total} |")
    if len(lines) == 2:
        lines.append("| (keine) | 0 |")
    return "\n".join(lines)


def emoji_report(path: Path | str) -> Tuple[Dict[str, int], str]:
    """Return emoji usage statistics and a Markdown table for ``path``."""

    source = Path(path)
    try:
        text = source.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover - defensive, unlikely in tests
        LOGGER.error("Failed to read %s: %s", source, exc)
        raise
    counts = count_blocks(text)
    return counts, render_table(counts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyse emoji usage in Markdown files")
    parser.add_argument("input", help="Markdown file to analyse")
    parser.add_argument(
        "--json",
        help="Optional JSON report output path. Prints to stdout when omitted.",
    )
    parser.add_argument(
        "--table",
        help="Optional Markdown table output path (otherwise printed to stdout).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    counts, table = emoji_report(args.input)
    result = {
        "input": args.input,
        "counts": counts,
        "table": table,
    }

    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=2), encoding="utf-8")
    else:
        print(json.dumps(result, indent=2))

    if args.table:
        Path(args.table).write_text(table, encoding="utf-8")
    else:
        print(table)


if __name__ == "__main__":  # pragma: no cover - CLI convenience
    main()
