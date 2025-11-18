from pathlib import Path

import sys

import pytest

from tools.emoji import inline_emojis


class DummyFetcher(inline_emojis.EmojiAssetFetcher):
    def __init__(self, kind="svg"):
        super().__init__(prefer="twemoji")
        self.kind = kind

    def fetch(self, emoji: str):  # type: ignore[override]
        if emoji == "❌":
            return None
        if self.kind == "svg":
            return inline_emojis.EmojiAsset(
                kind="svg",
                content="<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 10'><circle cx='5' cy='5' r='5' fill='red'/></svg>",
                source="dummy",
            )
        return inline_emojis.EmojiAsset(
            kind="png",
            content="",  # base64 empty for test
            source="dummy",
        )


def test_inline_basic(tmp_path):
    html = "<html><head></head><body>Hallo 🙂!</body></html>"
    input_path = tmp_path / "input.html"
    output_path = tmp_path / "output.html"
    css_path = tmp_path / "emoji.css"
    css_path.write_text(".emoji{display:inline-block;}", encoding="utf-8")
    input_path.write_text(html, encoding="utf-8")

    coverage = inline_emojis.inline_file(
        input_path,
        output_path,
        css_path=str(css_path),
        asset_fetcher=DummyFetcher(),
    )

    result = output_path.read_text(encoding="utf-8")
    assert "<span class=\"emoji\"" in result
    assert coverage["total"] == 1
    assert coverage["replaced"] == 1
    assert coverage["ratio"] == 1.0


def test_inline_respects_flag(tmp_path, monkeypatch):
    html = "<html><body>Test 🙂</body></html>"
    input_path = tmp_path / "input.html"
    output_path = tmp_path / "output.html"
    css_path = tmp_path / "emoji.css"
    css_path.write_text(".emoji{display:inline-block;}", encoding="utf-8")
    input_path.write_text(html, encoding="utf-8")
    monkeypatch.setenv("EMOJI_INLINING", "off")

    coverage = inline_emojis.inline_file(
        input_path,
        output_path,
        css_path=str(css_path),
        asset_fetcher=DummyFetcher(),
    )
    monkeypatch.delenv("EMOJI_INLINING", raising=False)

    result = output_path.read_text(encoding="utf-8")
    assert coverage["disabled"] is True
    assert coverage["ratio"] == 0.0
    assert "<span class=\"emoji\"" not in result
    assert "Test 🙂" in result


def test_inline_missing_asset(tmp_path):
    html = "<html><body>Oops ❌</body></html>"
    input_path = tmp_path / "input.html"
    output_path = tmp_path / "output.html"
    css_path = tmp_path / "emoji.css"
    css_path.write_text(".emoji{display:inline-block;}", encoding="utf-8")
    input_path.write_text(html, encoding="utf-8")

    coverage = inline_emojis.inline_file(
        input_path,
        output_path,
        css_path=str(css_path),
        asset_fetcher=DummyFetcher(),
    )
    assert coverage["missing"]
    assert "❌" in coverage["missing"]


def test_inline_adds_head_when_missing(tmp_path):
    html = "<div>🙂</div>"
    input_path = tmp_path / "input.html"
    output_path = tmp_path / "output.html"
    css_path = tmp_path / "emoji.css"
    css_path.write_text(".emoji{display:inline-block;}", encoding="utf-8")
    input_path.write_text(html, encoding="utf-8")

    inline_emojis.inline_file(
        input_path,
        output_path,
        css_path=str(css_path),
        asset_fetcher=DummyFetcher(),
    )
    result = output_path.read_text(encoding="utf-8")
    assert "<head>" in result
    assert "<span class=\"emoji\"" in result


def test_fetcher_slug_variants(monkeypatch):
    fetcher = inline_emojis.EmojiAssetFetcher()
    calls = []

    def fake_download(url, slug, *, suffix, kind, source):
        calls.append((url, slug, suffix, kind, source))
        if slug == "26a0":
            return inline_emojis.EmojiAsset(
                kind="svg",
                content="<svg xmlns='http://www.w3.org/2000/svg'></svg>",
                source=source,
            )
        return None

    monkeypatch.setattr(fetcher, "_download_asset", fake_download)
    asset = fetcher._fetch_twemoji_svg("26a0-fe0f")
    assert asset is not None
    tried_slugs = [call[1] for call in calls]
    assert "26a0-fe0f" in tried_slugs
    assert "26a0" in tried_slugs


def test_fetcher_png_and_openmoji(monkeypatch):
    fetcher = inline_emojis.EmojiAssetFetcher()

    def fake_download(url, slug, *, suffix, kind, source):
        if source == "twemoji_png" and slug == "1f3db":
            return inline_emojis.EmojiAsset(kind="png", content="YWJj", source=source)
        if source == "openmoji" and slug == "1f9d0":
            return inline_emojis.EmojiAsset(
                kind="svg",
                content="<svg xmlns='http://www.w3.org/2000/svg'></svg>",
                source=source,
            )
        return None

    monkeypatch.setattr(fetcher, "_download_asset", fake_download)
    png_asset = fetcher._fetch_twemoji_png("1f3db-fe0f")
    assert png_asset and png_asset.kind == "png"
    svg_asset = fetcher._fetch_openmoji("1f9d0-fe0f")
    assert svg_asset and svg_asset.kind == "svg"


def test_fetcher_caching(monkeypatch):
    fetcher = inline_emojis.EmojiAssetFetcher()
    slugs = []

    def fake_download(url, slug, *, suffix, kind, source):
        slugs.append(slug)
        return inline_emojis.EmojiAsset(
            kind="svg",
            content="<svg xmlns='http://www.w3.org/2000/svg'></svg>",
            source=source,
        )

    monkeypatch.setattr(fetcher, "_download_asset", fake_download)
    asset_one = fetcher.fetch("🙂")
    asset_two = fetcher.fetch("🙂")
    assert asset_one is asset_two
    assert slugs.count("1f642") == 1


def test_fetcher_fallback_to_openmoji(monkeypatch):
    fetcher = inline_emojis.EmojiAssetFetcher()

    def fake_download(url, slug, *, suffix, kind, source):
        if source.startswith("twemoji"):
            return None
        return inline_emojis.EmojiAsset(
            kind="svg",
            content="<svg xmlns='http://www.w3.org/2000/svg'></svg>",
            source=source,
        )

    monkeypatch.setattr(fetcher, "_download_asset", fake_download)
    asset = fetcher.fetch("🙂")
    assert asset is not None
    assert asset.source == "openmoji"


def test_inline_skips_code_blocks(tmp_path):
    html = "<html><body><code>🙂</code>Visible 🙂</body></html>"
    input_path = tmp_path / "input.html"
    output_path = tmp_path / "output.html"
    css_path = tmp_path / "emoji.css"
    css_path.write_text(".emoji{display:inline-block;}", encoding="utf-8")
    input_path.write_text(html, encoding="utf-8")

    inline_emojis.inline_file(
        input_path,
        output_path,
        css_path=str(css_path),
        asset_fetcher=DummyFetcher(),
    )
    result = output_path.read_text(encoding="utf-8")
    assert "<code>🙂</code>" in result
    assert result.count("class=\"emoji\"") == 1


def test_inline_missing_css(tmp_path):
    html = "<html><body>🙂</body></html>"
    input_path = tmp_path / "input.html"
    output_path = tmp_path / "output.html"
    input_path.write_text(html, encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        inline_emojis.inline_file(
            input_path,
            output_path,
            css_path=str(tmp_path / "missing.css"),
            asset_fetcher=DummyFetcher(),
        )


def test_download_asset_cache_hit(tmp_path, monkeypatch):
    monkeypatch.setattr(inline_emojis, "CACHE_DIR", tmp_path)
    cache_file = tmp_path / "twemoji_svg_test.svg"
    cache_file.write_text("<svg xmlns='http://www.w3.org/2000/svg'></svg>", encoding="utf-8")
    fetcher = inline_emojis.EmojiAssetFetcher()
    asset = fetcher._download_asset(
        "http://example.com/test.svg",
        "test",
        suffix=".svg",
        kind="svg",
        source="twemoji_svg",
    )
    assert asset and asset.kind == "svg"


def test_download_asset_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(inline_emojis, "CACHE_DIR", tmp_path)

    class DummyResponse:
        status_code = 404
        content = b""

    monkeypatch.setattr(inline_emojis.requests, "get", lambda url, timeout=10: DummyResponse())
    fetcher = inline_emojis.EmojiAssetFetcher()
    asset = fetcher._download_asset(
        "http://example.com/missing.svg",
        "missing",
        suffix=".svg",
        kind="svg",
        source="twemoji_svg",
    )
    assert asset is None


def test_fetcher_records_missing(monkeypatch):
    fetcher = inline_emojis.EmojiAssetFetcher()
    monkeypatch.setattr(fetcher, "_fetch_twemoji_svg", lambda slug: None)
    monkeypatch.setattr(fetcher, "_fetch_twemoji_png", lambda slug: None)
    monkeypatch.setattr(fetcher, "_fetch_openmoji", lambda slug: None)
    asset = fetcher.fetch("🙂")
    assert asset is None
    assert fetcher.cache["🙂"] is None


def test_cli_main(monkeypatch, tmp_path, capsys):
    html_path = tmp_path / "input.html"
    html_path.write_text("<html><body>🙂</body></html>", encoding="utf-8")
    output_path = tmp_path / "out.html"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "inline_emojis.py",
            "--in",
            str(html_path),
            "--out",
            str(output_path),
            "--css",
            str(tmp_path / "style.css"),
            "--coverage",
            str(tmp_path / "cov.json"),
        ],
    )

    def fake_inline_file(input_path, output_path, **kwargs):
        output_path.write_text("<html></html>", encoding="utf-8")
        return {"total": 0, "replaced": 0, "ratio": 0.0}

    monkeypatch.setattr(inline_emojis, "inline_file", fake_inline_file)
    inline_emojis.main()
    captured = capsys.readouterr()
    assert "Inline-Coverage" in captured.out
    assert output_path.exists()
