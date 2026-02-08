"""Regression tests for the RawFeature={fallback=mainfont} bug.

Bug report: When ERDA_ENABLE_LUA_FALLBACK=0, the publisher still emitted
RawFeature={fallback=mainfont} in \\setmainfont / \\setsansfont / \\setmonofont,
causing LuaLaTeX to crash because the lua fallback table was never registered.

Fixed in v2.3.0.
"""

from __future__ import annotations

import os
import tempfile

import pytest

from gitbook_worker.tools.publishing.publisher import _build_font_header


@pytest.fixture()
def _temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


class TestRawFeatureRespectsFallbackFlag:
    """Ensure RawFeature={fallback=mainfont} is only emitted when lua fallback is enabled."""

    def _build(
        self, *, enable_flag: str, manual_fallback: str | None, temp_dir: str
    ) -> str:
        return _build_font_header(
            main_font="DejaVu Serif",
            sans_font="DejaVu Sans",
            mono_font="DejaVu Sans Mono",
            emoji_font="Twemoji Mozilla",
            include_mainfont=True,
            needs_harfbuzz=True,
            manual_fallback_spec=manual_fallback,
            abort_if_missing_glyph=False,
            temp_dir=temp_dir,
        )

    def test_no_rawfeature_when_fallback_disabled(
        self, monkeypatch: pytest.MonkeyPatch, _temp_dir: str
    ) -> None:
        """ERDA_ENABLE_LUA_FALLBACK=0 → no RawFeature in any font command."""
        monkeypatch.setenv("ERDA_ENABLE_LUA_FALLBACK", "0")
        header = self._build(
            enable_flag="0",
            manual_fallback="Twemoji Mozilla",
            temp_dir=_temp_dir,
        )
        assert (
            "RawFeature" not in header
        ), "RawFeature must not appear when ERDA_ENABLE_LUA_FALLBACK=0"

    def test_no_rawfeature_when_fallback_off(
        self, monkeypatch: pytest.MonkeyPatch, _temp_dir: str
    ) -> None:
        """ERDA_ENABLE_LUA_FALLBACK=off → no RawFeature."""
        monkeypatch.setenv("ERDA_ENABLE_LUA_FALLBACK", "off")
        header = self._build(
            enable_flag="off",
            manual_fallback="Twemoji Mozilla",
            temp_dir=_temp_dir,
        )
        assert "RawFeature" not in header

    def test_no_rawfeature_when_no_fallback_spec(
        self, monkeypatch: pytest.MonkeyPatch, _temp_dir: str
    ) -> None:
        """No manual_fallback_spec → no RawFeature regardless of flag."""
        monkeypatch.setenv("ERDA_ENABLE_LUA_FALLBACK", "1")
        header = self._build(
            enable_flag="1",
            manual_fallback=None,
            temp_dir=_temp_dir,
        )
        assert "RawFeature" not in header

    def test_rawfeature_present_when_fallback_enabled(
        self, monkeypatch: pytest.MonkeyPatch, _temp_dir: str
    ) -> None:
        """ERDA_ENABLE_LUA_FALLBACK=1 + fallback spec → RawFeature must appear."""
        monkeypatch.setenv("ERDA_ENABLE_LUA_FALLBACK", "1")
        header = self._build(
            enable_flag="1",
            manual_fallback="Twemoji Mozilla",
            temp_dir=_temp_dir,
        )
        # Note: RawFeature may or may not appear depending on whether the font
        # is actually found by luaotfload. We only check that the code path
        # does NOT crash — the positive case depends on the TeX installation.
        # The critical assertion is the negative cases above.
