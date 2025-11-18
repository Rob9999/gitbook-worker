#!/usr/bin/env python3
"""Test if characters are in HANZI_KANJI dictionary."""

import sys
from pathlib import Path

# Add parent directory to path to import build script
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from generator.build_ccby_cjk_font import HANZI_KANJI

test_chars = ["語", "以", "下"]

print("Checking HANZI_KANJI dictionary:")
print("=" * 40)
for c in test_chars:
    status = "✓" if c in HANZI_KANJI else "✗"
    print(f"{c} (U+{ord(c):04X}): {status}")
    if c in HANZI_KANJI:
        print(f"  Bitmap: {len(HANZI_KANJI[c])} rows")

print(f"\nTotal characters in HANZI_KANJI: {len(HANZI_KANJI)}")
