"""Guards for font fallback setup to avoid broken TeX headers."""

import pytest

from gitbook_worker.tools.publishing import publisher

_BASE_ARGS = dict(
    main_font="Serif",
    sans_font="Sans",
    mono_font="Mono",
    emoji_font=None,
    include_mainfont=True,
    needs_harfbuzz=False,
    manual_fallback_spec="FooFallback;BarFallback",
    abort_if_missing_glyph=False,
)


def test_raises_when_lua_cache_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(publisher, "_check_luaotfload_has_font", lambda name: False)
    monkeypatch.setattr(publisher, "_font_available", lambda name: True)

    with pytest.raises(RuntimeError) as excinfo:
        publisher._build_font_header(**_BASE_ARGS)

    message = str(excinfo.value)
    assert "LuaTeX" in message
    assert "FooFallback" in message or "BarFallback" in message


def test_uses_fallback_when_lua_cache_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(publisher, "_check_luaotfload_has_font", lambda name: True)
    monkeypatch.setattr(publisher, "_font_available", lambda name: True)

    header = publisher._build_font_header(**_BASE_ARGS)

    assert "luaotfload.add_fallback" in header
    assert "FooFallback" in header
    assert "fallbackfeature" in header
