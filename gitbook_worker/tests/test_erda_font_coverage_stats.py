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
    target_devanagari_chars,
    target_ethiopic_chars,
)
from font_stats import inspect_font  # noqa: E402


@pytest.mark.parametrize("font_name", sorted(TARGET_REQUIREMENTS))
def test_erda_fonts_meet_release_coverage_targets(font_name: str) -> None:
    stats = inspect_font(TRUE_TYPE_DIR / font_name)
    failed_targets = [result for result in stats.target_results if not result.passed]

    assert stats.maxp_num_glyphs == stats.glyph_order_count
    assert not failed_targets, failed_targets


def test_release_targets_do_not_claim_impossible_indic_or_ethiopic_counts() -> None:
    assert CJK_HAN_TARGET == 3000
    assert CJK_HANGUL_TARGET == 3000
    assert len(target_devanagari_chars()) < 3000
    assert len(target_ethiopic_chars()) < 3000
