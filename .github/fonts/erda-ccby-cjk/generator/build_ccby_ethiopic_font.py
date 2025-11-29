#!/usr/bin/env python3
"""Build ERDA CC BY Ethiopic mini fallback font."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from ethiopic import ETHIOPIC
from font_family_builder import build_bitmap_font, resolve_bitmap
from font_logger import FontBuildLogger

ROOT = Path(__file__).parent
DATASET_DIR = ROOT.parent / "dataset"
OUTPUT_PATH = ROOT.parent / "true-type" / "erda-ccby-ethiopic.ttf"


def collect_ethiopic_chars() -> list[str]:
    required: set[str] = set(ETHIOPIC.keys())
    for md in DATASET_DIR.glob("*.md"):
        text = md.read_text(encoding="utf-8")
        for ch in text:
            code = ord(ch)
            if 0x1200 <= code <= 0x137F:
                required.add(ch)
    return sorted(required)


def build(output: Path) -> None:
    logger = FontBuildLogger()
    chars = collect_ethiopic_chars()
    build_bitmap_font("ERDA CC-BY Ethiopic", output, chars, resolve_bitmap, logger)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="Output path for generated TTF",
    )
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="Kompatibilitäts-Flag; wird ignoriert, erlaubt Weitergabe durch build_all",
    )
    args, _ = parser.parse_known_args(argv)
    return args


if __name__ == "__main__":
    args = parse_args()
    build(args.output)
