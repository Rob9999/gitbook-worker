"""
Character Index System for fast O(1) character lookup.

This module provides a pre-computed index for all character dictionaries,
eliminating the need for repeated linear searches through multiple dictionaries
during font generation.

Performance Impact:
- Before: O(n) lookup with 15+ dictionary checks per character
- After: O(1) lookup with single hash table access
- Expected speedup: ~50% reduction in build time

License: MIT (code), CC BY 4.0 (font glyphs)
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Import character modules
from katakana import (
    KATAKANA_BASE,
    SMALL_KATAKANA,
    DAKUTEN_COMBOS,
    HANDAKUTEN_COMBOS,
)
from hiragana import HIRAGANA
from hanzi import HANZI_KANJI
from punctuation import PUNCTUATION
from devanagari import DEVANAGARI, DEVANAGARI_EXTENDED


@dataclass
class CharacterInfo:
    """Information about a character's bitmap and source."""

    char: str
    bitmap: List[int]
    source: (
        str  # "katakana", "hiragana", "hanzi", "punctuation", "hangul", "devanagari"
    )
    sub_source: Optional[str] = (
        None  # e.g., "dakuten", "handakuten", "small", "extended"
    )


class CharacterIndex:
    """Fast O(1) lookup index for all available characters.

    This class builds a complete index of all character bitmaps at initialization,
    allowing instant lookups instead of iterating through multiple dictionaries.

    Usage:
        >>> index = CharacterIndex()
        >>> info = index.lookup('あ')
        >>> if info:
        ...     print(f"Found: {info.char} from {info.source}")
    """

    def __init__(self):
        """Initialize the character index by pre-computing all lookups."""
        self._index: Dict[str, CharacterInfo] = {}
        self._build_index()

    def _build_index(self):
        """Build the complete character index from all sources."""
        # Index Hiragana
        for char, bitmap in HIRAGANA.items():
            self._index[char] = CharacterInfo(
                char=char, bitmap=bitmap, source="hiragana"
            )

        # Index Katakana base
        for char, bitmap in KATAKANA_BASE.items():
            self._index[char] = CharacterInfo(
                char=char, bitmap=bitmap, source="katakana", sub_source="base"
            )

        # Index small Katakana
        for char, bitmap in SMALL_KATAKANA.items():
            self._index[char] = CharacterInfo(
                char=char, bitmap=bitmap, source="katakana", sub_source="small"
            )

        # Pre-compute and index Dakuten combinations
        for char, bitmap in DAKUTEN_COMBOS.items():
            self._index[char] = CharacterInfo(
                char=char, bitmap=bitmap, source="katakana", sub_source="dakuten"
            )

        # Pre-compute and index Handakuten combinations
        for char, bitmap in HANDAKUTEN_COMBOS.items():
            self._index[char] = CharacterInfo(
                char=char, bitmap=bitmap, source="katakana", sub_source="handakuten"
            )

        # Index Hanzi/Kanji
        for char, bitmap in HANZI_KANJI.items():
            self._index[char] = CharacterInfo(char=char, bitmap=bitmap, source="hanzi")

        # Index Punctuation
        for char, bitmap in PUNCTUATION.items():
            self._index[char] = CharacterInfo(
                char=char, bitmap=bitmap, source="punctuation"
            )

        # Index Devanagari (base)
        for char, bitmap in DEVANAGARI.items():
            self._index[char] = CharacterInfo(
                char=char, bitmap=bitmap, source="devanagari"
            )

        # Index Devanagari (extended)
        for char, bitmap in DEVANAGARI_EXTENDED.items():
            self._index[char] = CharacterInfo(
                char=char, bitmap=bitmap, source="devanagari", sub_source="extended"
            )

    def lookup(self, char: str) -> Optional[CharacterInfo]:
        """Look up a character in the index.

        Args:
            char: The character to look up

        Returns:
            CharacterInfo if found, None otherwise
        """
        return self._index.get(char)

    def has_character(self, char: str) -> bool:
        """Check if a character exists in the index.

        Args:
            char: The character to check

        Returns:
            True if character exists, False otherwise
        """
        return char in self._index

    def get_bitmap(self, char: str) -> Optional[List[int]]:
        """Get just the bitmap for a character.

        Args:
            char: The character to get bitmap for

        Returns:
            Bitmap list if found, None otherwise
        """
        info = self._index.get(char)
        return info.bitmap if info else None

    def stats(self) -> Dict[str, int]:
        """Get statistics about indexed characters.

        Returns:
            Dictionary with counts per source
        """
        from collections import Counter

        source_counts = Counter(info.source for info in self._index.values())

        return {"total": len(self._index), **dict(source_counts)}

    def list_characters(self, source: Optional[str] = None) -> List[str]:
        """List all characters from a specific source.

        Args:
            source: Filter by source ("katakana", "hiragana", "hanzi", "punctuation")
                   If None, returns all characters

        Returns:
            Sorted list of characters
        """
        if source is None:
            chars = list(self._index.keys())
        else:
            chars = [
                char for char, info in self._index.items() if info.source == source
            ]

        return sorted(chars)


# Global singleton instance for efficient reuse
_global_index: Optional[CharacterIndex] = None


def get_character_index() -> CharacterIndex:
    """Get the global CharacterIndex singleton.

    This function ensures only one index is created and reused across
    the entire font build process.

    Returns:
        The global CharacterIndex instance
    """
    global _global_index

    if _global_index is None:
        _global_index = CharacterIndex()

    return _global_index


def lookup_character(char: str) -> Optional[CharacterInfo]:
    """Convenience function to look up a character.

    Args:
        char: The character to look up

    Returns:
        CharacterInfo if found, None otherwise
    """
    return get_character_index().lookup(char)


def get_character_bitmap(char: str) -> Optional[List[int]]:
    """Convenience function to get a character's bitmap.

    Args:
        char: The character to get bitmap for

    Returns:
        Bitmap list if found, None otherwise
    """
    return get_character_index().get_bitmap(char)


if __name__ == "__main__":
    # Test the index
    print("Building Character Index...")
    index = get_character_index()

    stats = index.stats()
    print(f"\nCharacter Index Statistics:")
    print(f"  Total characters: {stats['total']}")
    print(f"  Hiragana:        {stats.get('hiragana', 0)}")
    print(f"  Katakana:        {stats.get('katakana', 0)}")
    print(f"  Hanzi/Kanji:     {stats.get('hanzi', 0)}")
    print(f"  Punctuation:     {stats.get('punctuation', 0)}")
    print(f"  Devanagari:      {stats.get('devanagari', 0)}")

    # Test lookups
    print("\nTesting lookups:")
    test_chars = ["あ", "ア", "人", "。", "X"]

    for char in test_chars:
        info = index.lookup(char)
        if info:
            print(
                f"  '{char}' → Found in {info.source}"
                + (f" ({info.sub_source})" if info.sub_source else "")
            )
        else:
            print(f"  '{char}' → Not found")
