#!/usr/bin/env python3
"""
Remove duplicate character definitions from hanzi.py.

This script identifies duplicate dictionary keys and keeps only the LAST occurrence
(which is what Python uses anyway, but having duplicates is confusing and error-prone).
"""

import re
import sys
from pathlib import Path
from collections import defaultdict


def find_duplicates(filepath: Path):
    """Find all duplicate character definitions in a Python file.

    Returns:
        dict: Mapping of character -> list of (line_number, line_content) tuples
    """
    pattern = re.compile(r'^(\s*)"(.+?)"\s*:\s*\[')

    char_occurrences = defaultdict(list)

    with open(filepath, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            match = pattern.match(line)
            if match:
                indent = match.group(1)
                char = match.group(2)
                char_occurrences[char].append((line_no, line.rstrip(), indent))

    # Filter to only duplicates
    duplicates = {
        char: occs for char, occs in char_occurrences.items() if len(occs) > 1
    }

    return duplicates


def remove_duplicates(filepath: Path, dry_run=True):
    """Remove duplicate character definitions, keeping only the last occurrence.

    Args:
        filepath: Path to the Python file
        dry_run: If True, only report changes without modifying the file
    """
    duplicates = find_duplicates(filepath)

    if not duplicates:
        print(f"✅ No duplicates found in {filepath.name}")
        return 0

    print(f"\n{'='*70}")
    print(f"Found {len(duplicates)} duplicate character(s) in {filepath.name}")
    print(f"{'='*70}\n")

    # Determine which lines to remove (all but the last occurrence)
    lines_to_remove = set()

    for char, occurrences in sorted(duplicates.items()):
        print(
            f"Character: '{char}' (U+{ord(char):04X}) - {len(occurrences)} occurrences"
        )

        # Keep last occurrence, remove earlier ones
        for line_no, line_content, indent in occurrences[:-1]:
            print(f"  ❌ REMOVE line {line_no}: {line_content[:60]}")
            lines_to_remove.add(line_no)

        last_line, last_content, _ = occurrences[-1]
        print(f"  ✅ KEEP   line {last_line}: {last_content[:60]}\n")

    print(f"\n{'='*70}")
    print(
        f"Total: {len(duplicates)} duplicates, {len(lines_to_remove)} lines to remove"
    )
    print(f"{'='*70}\n")

    if dry_run:
        print("⚠️  DRY RUN - No changes made")
        print("   Run with --fix to actually remove duplicates\n")
        return 1

    # Actually remove the lines
    print("🔧 Removing duplicate definitions...")

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Track bracket depth to remove complete entries
    lines_to_delete = set()

    for line_no in lines_to_remove:
        # Start from this line
        idx = line_no - 1
        lines_to_delete.add(idx)

        # Find matching closing bracket
        bracket_depth = 0
        started = False

        for i in range(idx, len(lines)):
            line = lines[i]

            if "[" in line:
                bracket_depth += line.count("[")
                started = True
            if "]" in line:
                bracket_depth -= line.count("]")

            if started:
                lines_to_delete.add(i)

                if bracket_depth == 0 and "]," in line:
                    # Found end of this entry
                    break

    # Write back without deleted lines
    new_lines = [line for i, line in enumerate(lines) if i not in lines_to_delete]

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"✅ Removed {len(lines_to_delete)} lines from {filepath.name}")
    print(f"   Original: {len(lines)} lines")
    print(f"   New:      {len(new_lines)} lines")
    print(f"   Saved:    {len(lines) - len(new_lines)} lines\n")

    return 0


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Remove duplicate character definitions"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Actually remove duplicates (default: dry-run)",
    )
    args = parser.parse_args()

    # Find hanzi.py
    generator_dir = Path(__file__).parent.parent / "generator"
    hanzi_file = generator_dir / "hanzi.py"

    if not hanzi_file.exists():
        print(f"❌ ERROR: Could not find {hanzi_file}")
        return 1

    # Process
    return remove_duplicates(hanzi_file, dry_run=not args.fix)


if __name__ == "__main__":
    sys.exit(main())
