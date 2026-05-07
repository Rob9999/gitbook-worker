"""Regression checks for ERDA generated fallback font coverage."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATOR_DIR = REPO_ROOT / ".github" / "fonts" / "erda-ccby-cjk" / "generator"
TRUE_TYPE_DIR = GENERATOR_DIR.parent / "true-type"

sys.path.insert(0, str(GENERATOR_DIR))

from coverage_targets import (  # noqa: E402
    CJK_HAN_TARGET,
    CJK_HANGUL_TARGET,
    TARGET_REQUIREMENTS,
    target_cjk_long_section_chars,
    target_cjk_long_sample_chars,
    target_devanagari_chars,
    target_ethiopic_chars,
)
from font_version import ERDA_FONT_VERSION  # noqa: E402
from font_stats import inspect_font  # noqa: E402
from synthetic_bitmap import codepoint_marker_bitmap  # noqa: E402


@pytest.mark.parametrize("font_name", sorted(TARGET_REQUIREMENTS))
def test_erda_fonts_meet_release_coverage_targets(font_name: str) -> None:
    stats = inspect_font(TRUE_TYPE_DIR / font_name)
    failed_targets = [result for result in stats.target_results if not result.passed]

    assert stats.maxp_num_glyphs == stats.glyph_order_count
    assert stats.version is not None
    assert stats.version.startswith(f"Version {ERDA_FONT_VERSION}+")
    assert not failed_targets, failed_targets


def test_release_targets_do_not_claim_impossible_indic_or_ethiopic_counts() -> None:
    assert CJK_HAN_TARGET == 3000
    assert CJK_HANGUL_TARGET == 3000
    assert len(target_cjk_long_sample_chars()) > 0
    assert len(target_cjk_long_section_chars()) > len(target_cjk_long_sample_chars())
    assert len(target_devanagari_chars()) < 3000
    assert len(target_ethiopic_chars()) < 3000


def test_generated_marker_glyphs_are_not_filled_rectangles() -> None:
    bitmap = codepoint_marker_bitmap("檢")
    rows_with_full_width = [row for row in bitmap if row == "########"]
    filled_cells = sum(row.count("#") for row in bitmap)

    assert not rows_with_full_width
    assert filled_cells <= 22
    assert max(row.count("#") for row in bitmap) <= 4
