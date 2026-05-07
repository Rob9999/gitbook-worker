"""Regression checks for long multilingual visual-inspection samples."""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
MIN_SCRIPT_CHARACTERS = 3000

SAMPLE_FILES = [
    REPO_ROOT / "de" / "content" / "examples" / "language-samples-100.md",
    REPO_ROOT / "en" / "content" / "examples" / "language-samples-100.md",
]

SCRIPT_RANGES = {
    "ZH-HANT": (
        (0x3400, 0x4DBF),
        (0x4E00, 0x9FFF),
        (0xF900, 0xFAFF),
    ),
    "JA": (
        (0x3040, 0x309F),
        (0x30A0, 0x30FF),
        (0x3400, 0x4DBF),
        (0x4E00, 0x9FFF),
        (0xF900, 0xFAFF),
    ),
    "KO": ((0xAC00, 0xD7AF),),
    "HI-DEVA": ((0x0900, 0x097F),),
    "AM": ((0x1200, 0x137F),),
    "TI": ((0x1200, 0x137F),),
}


def _extract_marked_block(sample_text: str, block_id: str) -> str:
    block_pattern = re.compile(
        rf"<!-- ERDA-LONG-SAMPLE: {re.escape(block_id)} START -->(.*?)"
        rf"<!-- ERDA-LONG-SAMPLE: {re.escape(block_id)} END -->",
        flags=re.DOTALL,
    )
    matches = block_pattern.findall(sample_text)
    assert len(matches) == 1, f"Expected exactly one marked block for {block_id}"
    return matches[0]


def _count_script_characters(sample_text: str, unicode_ranges: tuple[tuple[int, int], ...]) -> int:
    return sum(
        1
        for character in sample_text
        if any(range_start <= ord(character) <= range_end for range_start, range_end in unicode_ranges)
    )


@pytest.mark.parametrize("sample_path", SAMPLE_FILES, ids=lambda sample_path: sample_path.parent.parent.name)
@pytest.mark.parametrize("block_id, unicode_ranges", SCRIPT_RANGES.items())
def test_language_samples_keep_long_erda_font_blocks(
    sample_path: Path,
    block_id: str,
    unicode_ranges: tuple[tuple[int, int], ...],
) -> None:
    sample_text = sample_path.read_text(encoding="utf-8")
    marked_block = _extract_marked_block(sample_text, block_id)
    script_characters = _count_script_characters(marked_block, unicode_ranges)

    assert script_characters >= MIN_SCRIPT_CHARACTERS, (
        f"{sample_path.relative_to(REPO_ROOT)} block {block_id} has "
        f"{script_characters} script characters; expected at least {MIN_SCRIPT_CHARACTERS}"
    )