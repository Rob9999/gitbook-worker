#!/usr/bin/env python3
"""Check if title characters are in dataset."""

from pathlib import Path


def check_dataset():
    dataset_path = Path(__file__).parent.parent / "dataset" / "korean.md"
    text = dataset_path.read_text(encoding="utf-8")

    needed = ["국", "어", "대", "민"]

    print("Checking dataset for Korean title characters:")
    print("=" * 50)

    for c in needed:
        present = c in text
        status = "✓" if present else "✗"
        result = "Present" if present else "MISSING"
        print(f"{status} {c} (U+{ord(c):04X}): {result}")

    print("=" * 50)


if __name__ == "__main__":
    check_dataset()
