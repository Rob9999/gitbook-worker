"""Utility helpers for emoji handling across build scripts."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import unicodedata
from typing import Iterable, List

import emoji


@dataclass(frozen=True)
class EmojiRecord:
    """Aggregated information about a single emoji sequence."""

    glyph: str
    name: str
    codepoints: str
    asset_slug: str
    count: int


def iter_emoji_sequences(text: str) -> Iterable[str]:
    """Yield emoji sequences discovered in ``text`` preserving order."""

    for entry in emoji.emoji_list(text):
        yield entry["emoji"]


def emoji_to_display_codepoints(glyph: str) -> str:
    """Return space-separated ``U+XXXX`` values for ``glyph``."""

    return " ".join(f"U+{ord(char):04X}" for char in glyph)


def emoji_to_slug(glyph: str) -> str:
    """Return the hyphen-separated lowercase hex slug used by asset CDNs."""

    return "-".join(f"{ord(char):x}" for char in glyph)


def emoji_cldr_name(glyph: str) -> str:
    """Return the CLDR short name for ``glyph`` in English."""

    data = emoji.EMOJI_DATA.get(glyph)
    if data:
        name = data.get("en") or data.get("name") or data.get("status")
        if name:
            return name.strip(":").replace("_", " ")
    # Fallback to demojize for sequences that are not stored directly
    demojized = emoji.demojize(glyph, language="en")
    stripped = demojized.strip(":")
    if stripped:
        return stripped.replace("_", " ")
    return unicodedata.name(glyph) if len(glyph) == 1 else "unknown emoji"


def summarize_emojis(glyphs: Iterable[str]) -> List[EmojiRecord]:
    """Aggregate ``glyphs`` into :class:`EmojiRecord` entries."""

    counter = Counter(glyphs)
    records: List[EmojiRecord] = []
    for glyph, count in counter.most_common():
        records.append(
            EmojiRecord(
                glyph=glyph,
                name=emoji_cldr_name(glyph),
                codepoints=emoji_to_display_codepoints(glyph),
                asset_slug=emoji_to_slug(glyph),
                count=count,
            )
        )
    return records
