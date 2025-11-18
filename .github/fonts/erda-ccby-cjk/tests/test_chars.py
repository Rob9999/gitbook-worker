#!/usr/bin/env python3
"""Test if new characters are in the font."""

from fontTools.ttLib import TTFont
from pathlib import Path

# Font is one directory up
font_path = Path(__file__).parent.parent / "erda-ccby-cjk.ttf"
f = TTFont(font_path)
cmap = f.getBestCmap()

# Test Japanese characters
jp_chars = [
    "利",
    "従",
    "派",
    "生",
    "含",
    "改",
    "変",
    "引",
    "別",
    "掲",
    "載",
    "続",
    "語",
    "以",
    "下",
    "同",
    "条",
    "件",
    "共",
    "有",
]

print("Testing Japanese Kanji:")
print("=" * 40)
for c in jp_chars:
    status = "✓" if ord(c) in cmap else "✗"
    print(f"{c} (U+{ord(c):04X}): {status}")

print(
    f"\n{sum(1 for c in jp_chars if ord(c) in cmap)}/{len(jp_chars)} characters present"
)
