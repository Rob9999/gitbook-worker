"""Extract unique CJK characters from test markdown files.

This script analyzes test files to identify which CJK characters are actually used
and compares them against the current ERDA CJK font coverage.
"""

import re
from pathlib import Path
from typing import Set
import os

# CJK Unicode ranges
CJK_RANGES = [
    (0x4E00, 0x9FFF),  # CJK Unified Ideographs
    (0x3040, 0x309F),  # Hiragana
    (0x30A0, 0x30FF),  # Katakana
    (0xAC00, 0xD7AF),  # Hangul Syllables
]


def is_cjk_char(char: str) -> bool:
    """Check if character is in CJK range."""
    code_point = ord(char)
    for start, end in CJK_RANGES:
        if start <= code_point <= end:
            return True
    return False


def extract_cjk_chars(text: str) -> Set[str]:
    """Extract all unique CJK characters from text."""
    return {char for char in text if is_cjk_char(char)}


def main():
    # Debug path resolution
    script_path = Path(__file__).resolve()
    print(f"📍 Script location: {script_path}")

    # Calculate base path: tests/ -> erda-ccby-cjk/ -> fonts/ -> .github/ -> ERDA/
    base_path = script_path.parent.parent.parent.parent.parent
    print(f"📍 Base path (ERDA root): {base_path}")
    print()

    # Test file paths
    test_files = [
        base_path
        / ".github"
        / "gitbook_worker"
        / "tests"
        / "data"
        / "scenario-3-single-file"
        / "complex-doc_with-special&chars@2024!.md",
        base_path
        / ".github"
        / "gitbook_worker"
        / "tests"
        / "data"
        / "scenario-4-folder-without-gitbook"
        / "docs"
        / "README.md",
        base_path
        / ".github"
        / "gitbook_worker"
        / "tests"
        / "data"
        / "scenario-4-folder-without-gitbook"
        / "docs"
        / "01-getting-started.md",
        base_path
        / ".github"
        / "gitbook_worker"
        / "tests"
        / "data"
        / "scenario-4-folder-without-gitbook"
        / "docs"
        / "02-api-reference.md",
        base_path
        / ".github"
        / "gitbook_worker"
        / "tests"
        / "data"
        / "scenario-4-folder-without-gitbook"
        / "docs"
        / "03-advanced-topics.md",
    ]

    all_cjk_chars: Set[str] = set()

    for test_file in test_files:
        if not test_file.exists():
            print(f"⚠️  File not found: {test_file}")
            continue

        print(f"\n📄 Processing: {test_file.name}")

        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()
            chars = extract_cjk_chars(content)
            all_cjk_chars.update(chars)
            print(f"   Found {len(chars)} unique CJK characters")

    print(f"\n{'='*70}")
    print(f"📊 Total unique CJK characters across all test files: {len(all_cjk_chars)}")
    print(f"{'='*70}\n")

    # Categorize by Unicode range
    hanzi = [c for c in all_cjk_chars if 0x4E00 <= ord(c) <= 0x9FFF]
    hiragana = [c for c in all_cjk_chars if 0x3040 <= ord(c) <= 0x309F]
    katakana = [c for c in all_cjk_chars if 0x30A0 <= ord(c) <= 0x30FF]
    hangul = [c for c in all_cjk_chars if 0xAC00 <= ord(c) <= 0xD7AF]

    print("📋 Character Breakdown by Script:\n")

    if hanzi:
        print(f"🇨🇳 Hanzi/Kanji ({len(hanzi)} characters):")
        print("   " + "".join(sorted(hanzi)))
        print()

    if hiragana:
        print(f"🇯🇵 Hiragana ({len(hiragana)} characters):")
        print("   " + "".join(sorted(hiragana)))
        print()

    if katakana:
        print(f"🇯🇵 Katakana ({len(katakana)} characters):")
        print("   " + "".join(sorted(katakana)))
        print()

    if hangul:
        print(f"🇰🇷 Hangul ({len(hangul)} characters):")
        print("   " + "".join(sorted(hangul)))
        print()

    # Generate Python dictionary format for easy addition to hanzi.py
    print(f"\n{'='*70}")
    print("📝 Characters to add to hanzi.py (if missing):")
    print(f"{'='*70}\n")

    for char in sorted(hanzi):
        print(f'    "{char}": [  # TODO: Add 8x8 bitmap')
        print(f'        "........",')
        print(f'        "........",')
        print(f'        "........",')
        print(f'        "........",')
        print(f'        "........",')
        print(f'        "........",')
        print(f'        "........",')
        print(f'        "........",')
        print(f"    ],")

    print(f"\n{'='*70}")
    print("✅ Extraction complete!")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
