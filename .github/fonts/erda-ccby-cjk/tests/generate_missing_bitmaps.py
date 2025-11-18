"""Auto-generate minimalist 8x8 bitmaps for missing CJK characters.

This script generates simple placeholder bitmaps for missing characters
found in test files. These can be manually refined later if needed.
"""

import sys
from pathlib import Path

# Add generator directory to path
generator_path = Path(__file__).parent.parent / "generator"
sys.path.insert(0, str(generator_path))

from generator.hanzi import HANZI_KANJI
from generator.hiragana import HIRAGANA
from generator.katakana import KATAKANA_BASE
from extract_test_cjk_chars import extract_cjk_chars


def create_simple_box_bitmap():
    """Create a simple box bitmap as placeholder."""
    return [
        "########",
        "#......#",
        "#......#",
        "#......#",
        "#......#",
        "#......#",
        "#......#",
        "########",
    ]


def create_diagonal_bitmap():
    """Create a diagonal line bitmap as placeholder."""
    return [
        "#.......",
        ".#......",
        "..#.....",
        "...#....",
        "....#...",
        ".....#..",
        "......#.",
        ".......#",
    ]


def create_cross_bitmap():
    """Create a cross/plus bitmap as placeholder."""
    return [
        "...##...",
        "...##...",
        "########",
        "########",
        "...##...",
        "...##...",
        "...##...",
        "...##...",
    ]


def generate_hanzi_bitmaps(missing_chars):
    """Generate Python code for missing Hanzi characters."""
    print('"""Additional Hanzi/Kanji characters for test coverage."""\n')
    print("# Add these to HANZI_KANJI dictionary in hanzi.py:\n")
    print("HANZI_TEST_ADDITIONS = {")

    patterns = [create_simple_box_bitmap, create_diagonal_bitmap, create_cross_bitmap]

    for i, char in enumerate(sorted(missing_chars)):
        pattern_func = patterns[i % len(patterns)]
        bitmap = pattern_func()

        print(f'    "{char}": [  # U+{ord(char):04X}')
        for line in bitmap:
            print(f'        "{line}",')
        print("    ],")

    print("}\n")


def generate_hiragana_bitmaps(missing_chars):
    """Generate Python code for missing Hiragana characters."""
    print('"""Additional Hiragana characters for test coverage."""\n')
    print("# Add these to HIRAGANA dictionary in hiragana.py:\n")
    print("HIRAGANA_TEST_ADDITIONS = {")

    for char in sorted(missing_chars):
        bitmap = create_simple_box_bitmap()

        print(f'    "{char}": [  # U+{ord(char):04X}')
        for line in bitmap:
            print(f'        "{line}",')
        print("    ],")

    print("}\n")


def generate_katakana_bitmaps(missing_chars):
    """Generate Python code for missing Katakana characters."""
    print('"""Additional Katakana characters for test coverage."""\n')
    print("# Add these to KATAKANA_BASE dictionary in katakana.py:\n")
    print("KATAKANA_TEST_ADDITIONS = {")

    for char in sorted(missing_chars):
        bitmap = create_simple_box_bitmap()

        print(f'    "{char}": [  # U+{ord(char):04X}')
        for line in bitmap:
            print(f'        "{line}",')
        print("    ],")

    print("}\n")


def main():
    # Get test characters
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

    # Categorize
    test_hanzi = {c for c in all_test_chars if 0x4E00 <= ord(c) <= 0x9FFF}
    test_hiragana = {c for c in all_test_chars if 0x3040 <= ord(c) <= 0x309F}
    test_katakana = {c for c in all_test_chars if 0x30A0 <= ord(c) <= 0x30FF}

    # Find missing
    missing_hanzi = test_hanzi - set(HANZI_KANJI.keys())
    missing_hiragana = test_hiragana - set(HIRAGANA.keys())
    missing_katakana = test_katakana - set(KATAKANA_BASE.keys())

    print("=" * 70)
    print("🎨 Auto-Generated CJK Bitmaps for Missing Characters")
    print("=" * 70)
    print()
    print(f"Missing Hanzi: {len(missing_hanzi)}")
    print(f"Missing Hiragana: {len(missing_hiragana)}")
    print(f"Missing Katakana: {len(missing_katakana)}")
    print()
    print("=" * 70)
    print()

    if missing_hanzi:
        generate_hanzi_bitmaps(missing_hanzi)

    if missing_hiragana:
        generate_hiragana_bitmaps(missing_hiragana)

    if missing_katakana:
        generate_katakana_bitmaps(missing_katakana)


if __name__ == "__main__":
    main()
