"""Tests for the extended pdf_options passthrough and related aliases.

Covers:
- _parse_pdf_options: all new keys (documentclass, fontsize, geometry, toc,
  toc-depth, numbersections, colorlinks, linkcolor, urlcolor, citecolor,
  lang, header-includes, Pandoc-native font keys)
- _build_variable_overrides: passthrough mapping
- get_publish_list: 'format' alias for 'out_format'
- _resolve_project_metadata: 'author' (singular) alias for 'authors'
- _PDF_OPTIONS_PASSTHROUGH_VARS constant

v1.0.0  2026-02-08  initial
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import pytest

from gitbook_worker.tools.publishing.publisher import (
    _PDF_OPTIONS_PASSTHROUGH_VARS,
    _build_variable_overrides,
    _parse_pdf_options,
    _resolve_project_metadata,
)

# ──────────────────────────────────────────────────────────────────────────── #
#  _parse_pdf_options
# ──────────────────────────────────────────────────────────────────────────── #


class TestParsePdfOptions:
    """Verify extended _parse_pdf_options parsing."""

    def test_documentclass(self) -> None:
        result = _parse_pdf_options({"documentclass": "report"})
        assert result["documentclass"] == "report"

    def test_fontsize(self) -> None:
        result = _parse_pdf_options({"fontsize": "11pt"})
        assert result["fontsize"] == "11pt"

    def test_geometry(self) -> None:
        result = _parse_pdf_options({"geometry": "a4paper,margin=2.5cm"})
        assert result["geometry"] == "a4paper,margin=2.5cm"

    def test_numbersections_bool(self) -> None:
        result = _parse_pdf_options({"numbersections": True})
        assert result["numbersections"] == "true"

    def test_colorlinks_bool(self) -> None:
        result = _parse_pdf_options({"colorlinks": True})
        assert result["colorlinks"] == "true"

    def test_link_colors(self) -> None:
        raw = {
            "linkcolor": "NavyBlue",
            "urlcolor": "NavyBlue",
            "citecolor": "OliveGreen",
        }
        result = _parse_pdf_options(raw)
        assert result["linkcolor"] == "NavyBlue"
        assert result["urlcolor"] == "NavyBlue"
        assert result["citecolor"] == "OliveGreen"

    def test_toc_true(self) -> None:
        result = _parse_pdf_options({"toc": True})
        assert result["toc"] is True

    def test_toc_false(self) -> None:
        result = _parse_pdf_options({"toc": False})
        assert result["toc"] is False

    def test_toc_depth_hyphenated(self) -> None:
        result = _parse_pdf_options({"toc-depth": 3})
        assert result["toc_depth"] == 3

    def test_toc_depth_underscored(self) -> None:
        result = _parse_pdf_options({"toc_depth": 2})
        assert result["toc_depth"] == 2

    def test_toc_depth_invalid(self) -> None:
        # Should not crash; key should be absent.
        result = _parse_pdf_options({"toc-depth": "abc"})
        assert "toc_depth" not in result

    def test_lang(self) -> None:
        result = _parse_pdf_options({"lang": "en-GB"})
        assert result["lang"] == "en-GB"

    def test_header_includes_string(self) -> None:
        hi = "\\usepackage{booktabs}\n\\usepackage{longtable}"
        result = _parse_pdf_options({"header-includes": hi})
        assert result["header_includes"] == hi

    def test_header_includes_list(self) -> None:
        hi = ["\\usepackage{booktabs}", "\\usepackage{longtable}"]
        result = _parse_pdf_options({"header-includes": hi})
        assert "\\usepackage{booktabs}" in result["header_includes"]
        assert "\\usepackage{longtable}" in result["header_includes"]

    def test_pandoc_native_font_keys(self) -> None:
        """mainfont / sansfont / monofont (without underscore) are accepted."""
        raw = {
            "mainfont": "DejaVu Serif",
            "sansfont": "DejaVu Sans",
            "monofont": "DejaVu Sans Mono",
        }
        result = _parse_pdf_options(raw)
        assert result["mainfont"] == "DejaVu Serif"
        assert result["sansfont"] == "DejaVu Sans"
        assert result["monofont"] == "DejaVu Sans Mono"

    def test_empty_mapping(self) -> None:
        assert _parse_pdf_options({}) == {
            "abort_if_missing_glyph": True,
            "code_block_wrap": True,
        }

    def test_code_block_wrap_can_be_disabled(self) -> None:
        result = _parse_pdf_options({"code_block_wrap": False})
        assert result["code_block_wrap"] is False

    def test_code_block_wrap_accepts_hyphen_alias(self) -> None:
        result = _parse_pdf_options({"code-block-wrap": "no"})
        assert result["code_block_wrap"] is False

    def test_non_mapping(self) -> None:
        assert _parse_pdf_options("not a dict") == {}

    def test_full_customer_pdf_options(self) -> None:
        """Simulate the Mars Book customer pdf_options block."""
        raw = {
            "documentclass": "report",
            "mainfont": "DejaVu Serif",
            "sansfont": "DejaVu Sans",
            "monofont": "DejaVu Sans Mono",
            "fontsize": "11pt",
            "geometry": "a4paper,margin=2.5cm",
            "toc": True,
            "toc-depth": 3,
            "numbersections": True,
            "colorlinks": True,
            "linkcolor": "NavyBlue",
            "urlcolor": "NavyBlue",
            "citecolor": "NavyBlue",
            "lang": "en-GB",
            "header-includes": "\\usepackage{booktabs}\n\\usepackage{longtable}\n\\usepackage{graphicx}",
            "code_block_wrap": True,
        }
        result = _parse_pdf_options(raw)
        assert result["documentclass"] == "report"
        assert result["fontsize"] == "11pt"
        assert result["geometry"] == "a4paper,margin=2.5cm"
        assert result["toc"] is True
        assert result["toc_depth"] == 3
        assert result["numbersections"] == "true"
        assert result["colorlinks"] == "true"
        assert result["linkcolor"] == "NavyBlue"
        assert result["lang"] == "en-GB"
        assert "booktabs" in result["header_includes"]
        assert result["mainfont"] == "DejaVu Serif"
        assert result["code_block_wrap"] is True


# ──────────────────────────────────────────────────────────────────────────── #
#  _build_variable_overrides
# ──────────────────────────────────────────────────────────────────────────── #


class TestBuildVariableOverrides:
    """Verify _build_variable_overrides maps all passthrough keys."""

    def test_legacy_font_keys(self) -> None:
        overrides = _build_variable_overrides({"main_font": "Foo", "sans_font": "Bar"})
        assert overrides["mainfont"] == "Foo"
        assert overrides["sansfont"] == "Bar"

    def test_pandoc_native_font_keys_override_legacy(self) -> None:
        overrides = _build_variable_overrides(
            {
                "main_font": "Legacy",
                "mainfont": "Modern",
            }
        )
        # Pandoc-native key wins (applied after legacy).
        assert overrides["mainfont"] == "Modern"

    def test_passthrough_vars(self) -> None:
        pdf_opts: Dict[str, Any] = {
            "documentclass": "report",
            "fontsize": "12pt",
            "geometry": "a4paper,margin=3cm",
            "numbersections": "true",
            "colorlinks": "true",
            "linkcolor": "NavyBlue",
        }
        overrides = _build_variable_overrides(pdf_opts)
        assert overrides["documentclass"] == "report"
        assert overrides["fontsize"] == "12pt"
        assert overrides["geometry"] == "a4paper,margin=3cm"
        assert overrides["numbersections"] == "true"
        assert overrides["linkcolor"] == "NavyBlue"

    def test_passthrough_constant_completeness(self) -> None:
        """All keys listed in _PDF_OPTIONS_PASSTHROUGH_VARS should be forwarded."""
        # Build a dict with all keys present.
        pdf_opts = {key: f"val_{key}" for key in _PDF_OPTIONS_PASSTHROUGH_VARS}
        overrides = _build_variable_overrides(pdf_opts)
        for key in _PDF_OPTIONS_PASSTHROUGH_VARS:
            assert key in overrides, f"Key {key!r} not forwarded"


# ──────────────────────────────────────────────────────────────────────────── #
#  get_publish_list – 'format' alias
# ──────────────────────────────────────────────────────────────────────────── #


class TestGetPublishListFormatAlias:
    """Verify 'format' is accepted as alias for 'out_format'."""

    def test_format_alias_produces_out_format(self, tmp_path: Path) -> None:
        from gitbook_worker.tools.publishing.publisher import get_publish_list

        manifest = tmp_path / "publish.yml"
        manifest.write_text(
            textwrap.dedent("""\
                version: 0.1.0
                publish:
                  - build: true
                    path: content/
                    out: publish/test.pdf
                    format: pdf
            """),
            encoding="utf-8",
        )
        (tmp_path / "content").mkdir()
        entries = get_publish_list(str(manifest))
        assert len(entries) == 1
        assert entries[0]["out_format"] == "pdf"

    def test_target_format_alias(self, tmp_path: Path) -> None:
        from gitbook_worker.tools.publishing.publisher import get_publish_list

        manifest = tmp_path / "publish.yml"
        manifest.write_text(
            textwrap.dedent("""\
                version: 0.1.0
                publish:
                  - build: true
                    path: content/
                    out: publish/test.pdf
                    target_format: pdf
            """),
            encoding="utf-8",
        )
        (tmp_path / "content").mkdir()
        entries = get_publish_list(str(manifest))
        assert len(entries) == 1
        assert entries[0]["out_format"] == "pdf"


# ──────────────────────────────────────────────────────────────────────────── #
#  _resolve_project_metadata – 'author' singular alias
# ──────────────────────────────────────────────────────────────────────────── #


class TestAuthorSingularAlias:
    """Verify 'project.author' (singular) is accepted."""

    def test_author_singular_string(self, tmp_path: Path) -> None:
        manifest = tmp_path / "publish.yml"
        manifest.write_text(
            textwrap.dedent("""\
                version: 0.1.0
                project:
                  name: Test Book
                  license: "CC BY 4.0"
                  author: "Alice Wonderland"
                publish: []
            """),
            encoding="utf-8",
        )
        meta = _resolve_project_metadata(manifest)
        assert "Alice Wonderland" in meta.authors

    def test_authors_plural_still_works(self, tmp_path: Path) -> None:
        manifest = tmp_path / "publish.yml"
        manifest.write_text(
            textwrap.dedent("""\
                version: 0.1.0
                project:
                  name: Test Book
                  license: "CC BY 4.0"
                  authors:
                    - Alice
                    - Bob
                publish: []
            """),
            encoding="utf-8",
        )
        meta = _resolve_project_metadata(manifest)
        assert "Alice" in meta.authors
        assert "Bob" in meta.authors

    def test_authors_plural_takes_precedence(self, tmp_path: Path) -> None:
        """When both author and authors are set, authors wins."""
        manifest = tmp_path / "publish.yml"
        manifest.write_text(
            textwrap.dedent("""\
                version: 0.1.0
                project:
                  name: Test Book
                  license: "CC BY 4.0"
                  authors:
                    - From-Authors
                  author: From-Author
                publish: []
            """),
            encoding="utf-8",
        )
        meta = _resolve_project_metadata(manifest)
        assert "From-Authors" in meta.authors
        assert "From-Author" not in meta.authors


# ──────────────────────────────────────────────────────────────────────────── #
#  Constant sanity
# ──────────────────────────────────────────────────────────────────────────── #


class TestPassthroughConstant:
    """Verify the _PDF_OPTIONS_PASSTHROUGH_VARS constant itself."""

    def test_is_non_empty_tuple(self) -> None:
        assert isinstance(_PDF_OPTIONS_PASSTHROUGH_VARS, tuple)
        assert len(_PDF_OPTIONS_PASSTHROUGH_VARS) >= 10

    def test_contains_core_keys(self) -> None:
        for key in ("documentclass", "fontsize", "geometry", "colorlinks", "linkcolor"):
            assert key in _PDF_OPTIONS_PASSTHROUGH_VARS
