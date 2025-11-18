#!/usr/bin/env python3
"""Debug why characters are not being added to font."""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from generator.build_ccby_cjk_font import HANZI_KANJI

test_chars = ["語", "以", "下", "利"]  # 利 works, others don't

print("Debug character lookup:")
print("=" * 60)
for c in test_chars:
    code = ord(c)
    in_dict = c in HANZI_KANJI
    in_cjk_range = 0x4E00 <= code <= 0x9FFF

    print(f"\n{c} (U+{code:04X}):")
    print(f"  In HANZI_KANJI dict: {in_dict}")
    print(f"  In CJK range (U+4E00-U+9FFF): {in_cjk_range}")
    if in_dict:
        print(f"  Bitmap rows: {len(HANZI_KANJI[c])}")
        print(f"  First row: {HANZI_KANJI[c][0]}")
