"""Check which CJK characters from test files are missing in the ERDA CJK font.

This script compares the CJK characters used in gitbook_worker test files
against the characters currently defined in the font modules.
"""

import sys
from pathlib import Path

# Add generator directory to path to import font modules
generator_path = Path(__file__).parent.parent / "generator"
sys.path.insert(0, str(generator_path))

from hanzi import HANZI_KANJI
from hiragana import HIRAGANA
from katakana import (
    KATAKANA_BASE,
    SMALL_KATAKANA,
    DAKUTEN_COMBOS,
    HANDAKUTEN_COMBOS,
)
from hangul import L_PATTERNS, V_PATTERNS, T_PATTERNS

# Combine all Katakana variants
# Katakana with dakuten/handakuten are algorithmically generated
KATAKANA_ALL_CHARS = (
    set(KATAKANA_BASE.keys())
    | set(SMALL_KATAKANA.keys())
    | set(DAKUTEN_COMBOS.keys())
    | set(HANDAKUTEN_COMBOS.keys())
)

# Import extraction functions from the other script
from extract_test_cjk_chars import extract_cjk_chars, CJK_RANGES


def is_cjk_char(char: str) -> bool:
    """Check if character is in CJK range."""
    code_point = ord(char)
    for start, end in CJK_RANGES:
        if start <= code_point <= end:
            return True
    return False


def main():
    # Get all test CJK characters
    script_path = Path(__file__).resolve()
    base_path = script_path.parent.parent.parent.parent.parent

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

    all_test_chars = set()
    for test_file in test_files:
        if test_file.exists():
            with open(test_file, "r", encoding="utf-8") as f:
                all_test_chars.update(extract_cjk_chars(f.read()))

    # Categorize test characters
    test_hanzi = {c for c in all_test_chars if 0x4E00 <= ord(c) <= 0x9FFF}
    test_hiragana = {c for c in all_test_chars if 0x3040 <= ord(c) <= 0x309F}
    test_katakana = {c for c in all_test_chars if 0x30A0 <= ord(c) <= 0x30FF}
    test_hangul = {c for c in all_test_chars if 0xAC00 <= ord(c) <= 0xD7AF}

    # Check coverage
    hanzi_keys = set(HANZI_KANJI.keys())
    hiragana_keys = set(HIRAGANA.keys())
    katakana_keys = KATAKANA_ALL_CHARS

    # Check Hangul (algorithmically generated - all modern syllables are covered)
    # Modern Hangul syllables range from U+AC00 to U+D7A3 (11,172 syllables)
    hangul_covered = (
        test_hangul  # All modern Hangul syllables are algorithmically generated
    )
    hangul_missing = set()

    # Find missing characters
    missing_hanzi = test_hanzi - hanzi_keys
    missing_hiragana = test_hiragana - hiragana_keys
    missing_katakana = test_katakana - katakana_keys

    # Report
    print("=" * 70)
    print("🧪 Test File CJK Coverage Report")
    print("=" * 70)
    print()

    print(f"📊 Total test CJK characters: {len(all_test_chars)}")
    print()

    # Hanzi/Kanji
    print(f"🇨🇳 Hanzi/Kanji: {len(test_hanzi)} characters")
    print(f"   ✅ Covered: {len(test_hanzi - missing_hanzi)}")
    print(f"   ❌ Missing: {len(missing_hanzi)}")
    if missing_hanzi:
        print(f"   Missing chars: {''.join(sorted(missing_hanzi))}")
    print()

    # Hiragana
    print(f"🇯🇵 Hiragana: {len(test_hiragana)} characters")
    print(f"   ✅ Covered: {len(test_hiragana - missing_hiragana)}")
    print(f"   ❌ Missing: {len(missing_hiragana)}")
    if missing_hiragana:
        print(f"   Missing chars: {''.join(sorted(missing_hiragana))}")
    print()

    # Katakana
    print(f"🇯🇵 Katakana: {len(test_katakana)} characters")
    print(f"   ✅ Covered: {len(test_katakana - missing_katakana)}")
    print(f"   ❌ Missing: {len(missing_katakana)}")
    if missing_katakana:
        print(f"   Missing chars: {''.join(sorted(missing_katakana))}")
    print()

    # Hangul
    print(f"🇰🇷 Hangul: {len(test_hangul)} characters")
    print(f"   ✅ Covered: {len(hangul_covered)} (algorithmic)")
    print(f"   ❌ Missing: {len(hangul_missing)}")
    if hangul_missing:
        print(f"   Missing chars: {''.join(sorted(hangul_missing))}")
    print()

    print("=" * 70)
    total_missing = (
        len(missing_hanzi)
        + len(missing_hiragana)
        + len(missing_katakana)
        + len(hangul_missing)
    )
    if total_missing == 0:
        print("✅ All test CJK characters are covered by the font!")
    else:
        print(f"⚠️  Total missing characters: {total_missing}")
        print(f"   Action needed: Add missing characters to font modules")
    print("=" * 70)


if __name__ == "__main__":
    main()
