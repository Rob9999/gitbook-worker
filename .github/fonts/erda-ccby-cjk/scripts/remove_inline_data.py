"""Remove inline character data from build script."""

import re
from pathlib import Path

# Read the file
file_path = Path("generator/build_ccby_cjk_font.py")
with open(file_path, "r", encoding="utf-8-sig") as f:
    lines = f.readlines()

# Find line numbers for blocks to remove
in_block = False
block_start = None
blocks_to_remove = []

for i, line in enumerate(lines):
    # Detect block starts
    if any(
        marker in line
        for marker in [
            "KATAKANA_BASE:",
            "SMALL_KATAKANA:",
            "DAKUTEN = [",
            "HANDAKUTEN = [",
            "PUNCTUATION = {",
            "HANZI_KANJI:",
            "L_PATTERNS = {",
            "V_PATTERNS = {",
            "T_PATTERNS = {",
            "L_LIST = [",
            "V_LIST = [",
            "T_LIST = [",
        ]
    ):
        in_block = True
        block_start = i

    # Detect block ends
    if in_block and (line.strip() == "}" or line.strip() == "]"):
        blocks_to_remove.append((block_start, i + 1))
        in_block = False

    # Remove SBASE line
    if line.strip() == "SBASE = 0xAC00":
        blocks_to_remove.append((i, i + 1))

# Remove blocks in reverse order
for start, end in reversed(blocks_to_remove):
    del lines[start:end]

# Write back
with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(lines)

print(f"✓ Removed {len(blocks_to_remove)} data blocks")
