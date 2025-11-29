#!/usr/bin/env python3
"""Build ERDA CC BY Indic fallback font (Devanagari/Hindi)."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from devanagari import DEVANAGARI, DEVANAGARI_EXTENDED
from font_family_builder import build_bitmap_font, resolve_bitmap
from font_logger import FontBuildLogger

ROOT = Path(__file__).parent
DATASET_DIR = ROOT.parent / "dataset"
OUTPUT_PATH = ROOT.parent / "true-type" / "erda-ccby-indic.ttf"


def collect_devanagari_chars() -> list[str]:
    required: set[str] = set()
    for md in DATASET_DIR.glob("*.md"):
        text = md.read_text(encoding="utf-8")
        for ch in text:
            code = ord(ch)
            if 0x0900 <= code <= 0x097F:
                required.add(ch)
    required.update(DEVANAGARI.keys())
    required.update(DEVANAGARI_EXTENDED.keys())
    return sorted(required)


def build(output: Path) -> None:
    logger = FontBuildLogger()
    chars = collect_devanagari_chars()
    build_bitmap_font("ERDA CC-BY Indic", output, chars, resolve_bitmap, logger)


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
