"""Coverage targets for ERDA CC-BY generated fallback fonts."""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable
from pathlib import Path

CodepointRange = tuple[int, int]

CJK_HAN_TARGET = 3000
CJK_HANGUL_TARGET = 3000

CJK_UNIFIED_RANGES: tuple[CodepointRange, ...] = ((0x4E00, 0x9FFF),)
HIRAGANA_RANGES: tuple[CodepointRange, ...] = ((0x3040, 0x309F),)
KATAKANA_RANGES: tuple[CodepointRange, ...] = ((0x30A0, 0x30FF),)
CJK_PUNCTUATION_RANGES: tuple[CodepointRange, ...] = ((0x3000, 0x303F),)
FULLWIDTH_RANGES: tuple[CodepointRange, ...] = ((0xFF00, 0xFFEF),)
HANGUL_SYLLABLE_RANGES: tuple[CodepointRange, ...] = ((0xAC00, 0xD7A3),)
CJK_TARGET_RANGES: tuple[CodepointRange, ...] = (
    *CJK_UNIFIED_RANGES,
    *HIRAGANA_RANGES,
    *KATAKANA_RANGES,
    *CJK_PUNCTUATION_RANGES,
    *FULLWIDTH_RANGES,
    *HANGUL_SYLLABLE_RANGES,
)
CJK_LONG_SAMPLE_MARKERS: tuple[str, ...] = ("ZH-HANT", "JA", "KO")
CJK_LONG_SAMPLE_CONTENT_PATHS: tuple[Path, ...] = (
    Path("de/content/examples/language-samples-100.md"),
    Path("en/content/examples/language-samples-100.md"),
)
CJK_LONG_SAMPLE_SECTION_HEADINGS: tuple[str, ...] = (
    "## Sehr lange Texte - mindestens 3000 Zeichen je Sprache",
    "## Very Long Texts - At Least 3000 Characters per Language",
)

DEVANAGARI_MAIN_RANGES: tuple[CodepointRange, ...] = ((0x0900, 0x097F),)
DEVANAGARI_EXTENDED_RANGES: tuple[CodepointRange, ...] = ((0xA8E0, 0xA8FF),)
DEVANAGARI_RANGES: tuple[CodepointRange, ...] = (
    *DEVANAGARI_MAIN_RANGES,
    *DEVANAGARI_EXTENDED_RANGES,
)

ETHIOPIC_MAIN_RANGES: tuple[CodepointRange, ...] = ((0x1200, 0x137F),)
ETHIOPIC_SUPPLEMENT_RANGES: tuple[CodepointRange, ...] = ((0x1380, 0x139F),)
ETHIOPIC_EXTENDED_RANGES: tuple[CodepointRange, ...] = ((0x2D80, 0x2DDF),)
ETHIOPIC_EXTENDED_A_RANGES: tuple[CodepointRange, ...] = ((0xAB00, 0xAB2F),)
ETHIOPIC_EXTENDED_B_RANGES: tuple[CodepointRange, ...] = ((0x1E7E0, 0x1E7FF),)
ETHIOPIC_RANGES: tuple[CodepointRange, ...] = (
    *ETHIOPIC_MAIN_RANGES,
    *ETHIOPIC_SUPPLEMENT_RANGES,
    *ETHIOPIC_EXTENDED_RANGES,
    *ETHIOPIC_EXTENDED_A_RANGES,
    *ETHIOPIC_EXTENDED_B_RANGES,
)


def iter_codepoints(ranges: Iterable[CodepointRange]) -> Iterable[int]:
    for range_start, range_end in ranges:
        yield from range(range_start, range_end + 1)


def is_assigned(codepoint: int) -> bool:
    return unicodedata.name(chr(codepoint), None) is not None


def assigned_chars(ranges: Iterable[CodepointRange]) -> list[str]:
    return [
        chr(codepoint)
        for codepoint in iter_codepoints(ranges)
        if is_assigned(codepoint)
    ]


def first_assigned_chars(ranges: Iterable[CodepointRange], limit: int) -> list[str]:
    chars: list[str] = []
    for codepoint in iter_codepoints(ranges):
        if is_assigned(codepoint):
            chars.append(chr(codepoint))
        if len(chars) >= limit:
            break
    return chars


def chars_in_ranges(text: str, ranges: Iterable[CodepointRange]) -> list[str]:
    """Return unique characters from text whose codepoints fall in ranges."""

    return sorted(
        {
            char
            for char in text
            if any(start <= ord(char) <= end for start, end in ranges)
        }
    )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _marked_block(text: str, marker: str) -> str:
    start = f"<!-- ERDA-LONG-SAMPLE: {marker} START -->"
    end = f"<!-- ERDA-LONG-SAMPLE: {marker} END -->"
    if start not in text or end not in text:
        return ""
    return text.split(start, 1)[1].split(end, 1)[0]


def _section_after_heading(text: str, headings: Iterable[str]) -> str:
    start_positions = [text.find(heading) for heading in headings]
    start_positions = [position for position in start_positions if position >= 0]
    if not start_positions:
        return ""

    start = min(start_positions)
    next_heading = text.find("\n## ", start + 1)
    if next_heading < 0:
        return text[start:]
    return text[start:next_heading]


def target_cjk_long_sample_chars() -> list[str]:
    """Return CJK-family chars used by the 3000-character sample blocks."""

    root = _repo_root()
    target: set[str] = set()
    for relative_path in CJK_LONG_SAMPLE_CONTENT_PATHS:
        path = root / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in CJK_LONG_SAMPLE_MARKERS:
            target.update(
                chars_in_ranges(_marked_block(text, marker), CJK_TARGET_RANGES)
            )
    return sorted(target)


def target_cjk_long_section_chars() -> list[str]:
    """Return CJK-family chars used by the complete long-text section."""

    root = _repo_root()
    target: set[str] = set()
    for relative_path in CJK_LONG_SAMPLE_CONTENT_PATHS:
        path = root / relative_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        target.update(
            chars_in_ranges(
                _section_after_heading(text, CJK_LONG_SAMPLE_SECTION_HEADINGS),
                CJK_TARGET_RANGES,
            )
        )
    return sorted(target)


def target_cjk_chars() -> list[str]:
    """Return staged 2.5.0 CJK-family target characters.

    The target intentionally combines broad CJK/Hangul coverage with complete
    Kana and common punctuation blocks. It is a fallback coverage target, not a
    frequency-ranked quality font replacement.
    """

    target: set[str] = set()
    target.update(first_assigned_chars(CJK_UNIFIED_RANGES, CJK_HAN_TARGET))
    target.update(first_assigned_chars(HANGUL_SYLLABLE_RANGES, CJK_HANGUL_TARGET))
    target.update(assigned_chars(HIRAGANA_RANGES))
    target.update(assigned_chars(KATAKANA_RANGES))
    target.update(assigned_chars(CJK_PUNCTUATION_RANGES))
    target.update(assigned_chars(FULLWIDTH_RANGES))
    target.update(target_cjk_long_sample_chars())
    target.update(target_cjk_long_section_chars())
    return sorted(target)


def target_devanagari_chars() -> list[str]:
    """Return every assigned Devanagari codepoint in supported blocks."""

    return sorted(set(assigned_chars(DEVANAGARI_RANGES)))


def target_ethiopic_chars() -> list[str]:
    """Return every assigned Ethiopic codepoint in supported blocks."""

    return sorted(set(assigned_chars(ETHIOPIC_RANGES)))


STAT_RANGES: dict[str, tuple[CodepointRange, ...]] = {
    "cjk_unified_ideographs": CJK_UNIFIED_RANGES,
    "hiragana": HIRAGANA_RANGES,
    "katakana": KATAKANA_RANGES,
    "cjk_punctuation": CJK_PUNCTUATION_RANGES,
    "fullwidth": FULLWIDTH_RANGES,
    "hangul_syllables": HANGUL_SYLLABLE_RANGES,
    "devanagari_main": DEVANAGARI_MAIN_RANGES,
    "devanagari_extended": DEVANAGARI_EXTENDED_RANGES,
    "ethiopic_main": ETHIOPIC_MAIN_RANGES,
    "ethiopic_supplement": ETHIOPIC_SUPPLEMENT_RANGES,
    "ethiopic_extended": ETHIOPIC_EXTENDED_RANGES,
    "ethiopic_extended_a": ETHIOPIC_EXTENDED_A_RANGES,
    "ethiopic_extended_b": ETHIOPIC_EXTENDED_B_RANGES,
}


TARGET_REQUIREMENTS: dict[str, dict[str, int]] = {
    "erda-ccby-cjk.ttf": {
        "cjk_unified_ideographs": CJK_HAN_TARGET,
        "hangul_syllables": CJK_HANGUL_TARGET,
        "hiragana": len(assigned_chars(HIRAGANA_RANGES)),
        "katakana": len(assigned_chars(KATAKANA_RANGES)),
    },
    "erda-ccby-indic.ttf": {
        "devanagari_main": len(assigned_chars(DEVANAGARI_MAIN_RANGES)),
        "devanagari_extended": len(assigned_chars(DEVANAGARI_EXTENDED_RANGES)),
    },
    "erda-ccby-ethiopic.ttf": {
        "ethiopic_main": len(assigned_chars(ETHIOPIC_MAIN_RANGES)),
        "ethiopic_supplement": len(assigned_chars(ETHIOPIC_SUPPLEMENT_RANGES)),
        "ethiopic_extended": len(assigned_chars(ETHIOPIC_EXTENDED_RANGES)),
        "ethiopic_extended_a": len(assigned_chars(ETHIOPIC_EXTENDED_A_RANGES)),
        "ethiopic_extended_b": len(assigned_chars(ETHIOPIC_EXTENDED_B_RANGES)),
    },
}
