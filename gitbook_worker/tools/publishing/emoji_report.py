"""Emoji usage analysis helpers for the publishing toolchain."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Tuple
import logging
import re

EMOJI_BLOCKS = [
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


def emoji_report(md_file: str) -> Tuple[Dict[str, int], str]:
    """Return emoji usage counts and a Markdown table for ``md_file``.

    The helper scans the Markdown document for any characters outside of the
    ASCII and Latin-1 ranges and then groups them into Unicode blocks using the
    table above.  The resulting mapping contains a count per block and the
    returned Markdown table can be written to disk directly.
    """

    try:
        with open(md_file, "r", encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:  # pragma: no cover - filesystem issues bubble up
        logging.error("Failed to read %s: %s", md_file, exc)
        raise

    emoji_pattern = re.compile(r"[^\u0000-\u007F\u00A0-\u024F]+")
    emojis = [char for group in emoji_pattern.findall(text) for char in group]

    counts: Dict[str, int] = defaultdict(int)
    for char in emojis:
        codepoint = ord(char)
        block = "Unknown"
        for name, start, end in EMOJI_BLOCKS:
            if start <= codepoint <= end:
                block = name
                break
        counts[block] += 1

    rows = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    lines = ["| Unicode Block | Count |", "| --- | --- |"]
    for name, count in rows:
        lines.append(f"| {name} | {count} |")
    table_md = "\n".join(lines)

    return dict(counts), table_md
