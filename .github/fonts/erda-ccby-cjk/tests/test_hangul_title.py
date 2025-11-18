#!/usr/bin/env python3
"""Test Korean title characters in font."""

from pathlib import Path
from fontTools.ttLib import TTFont

# Test characters from "한국어 (대한민국)"
TEST_CHARS = ["한", "국", "어", "대", "민"]


def test_hangul_title():
    """Test that all Korean title characters are in the font."""
    font_path = Path(__file__).parent.parent / "true-type" / "erda-ccby-cjk.ttf"

    print(f"Loading font: {font_path}")
    font = TTFont(str(font_path))
    cmap = font.getBestCmap()

    print(f"\nTesting Korean title: 한국어 (대한민국)")
    print("=" * 50)

    all_found = True
    for char in TEST_CHARS:
        code = ord(char)
        has_glyph = code in cmap
        status = "✓" if has_glyph else "✗"
        result = "Found" if has_glyph else "MISSING"
        print(f"{status} {char} (U+{code:04X}): {result}")

        if not has_glyph:
            all_found = False

    print("=" * 50)
    if all_found:
        print("✓ All characters found!")
        return 0
    else:
        print("✗ Some characters are missing!")
        return 1


if __name__ == "__main__":
    exit(test_hangul_title())
