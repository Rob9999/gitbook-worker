"""Tests for config-completeness backlog items (v2.2.0 „Lückenlos").

Covers:
- book.json:language → Pandoc lang metadata
- book.json:schema_version validation
- fonts.yml:copyright → ATTRIBUTION.md
- docker_config.yml version validation
- ProjectMetadata.language field
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from gitbook_worker.tools.publishing import publisher
from gitbook_worker.tools.publishing.font_attribution import (
    FontAttributionEntry,
    generate_font_attribution_files,
)
from gitbook_worker.tools.utils.semver import is_semver


# ── Helpers ──────────────────────────────────────────────────────────────────


def _write_manifest(base: Path, data: dict) -> Path:
    manifest = base / "publish.yml"
    manifest.write_text(yaml.safe_dump(data), encoding="utf-8")
    return manifest


# ── book.json:language → Pandoc lang ─────────────────────────────────────────


class TestBookJsonLanguage:
    """Test that book.json language is read and flows to Pandoc metadata."""

    def test_load_book_json_reads_language(self, tmp_path: Path) -> None:
        (tmp_path / "book.json").write_text(
            json.dumps(
                {"title": "T", "author": "A", "language": "de", "license": "CC0"}
            ),
            encoding="utf-8",
        )
        title, authors, lic, date, version, language = publisher._load_book_json(
            tmp_path
        )
        assert language == "de"

    def test_load_book_json_language_none_when_absent(self, tmp_path: Path) -> None:
        (tmp_path / "book.json").write_text(
            json.dumps({"title": "T", "author": "A"}),
            encoding="utf-8",
        )
        *_, language = publisher._load_book_json(tmp_path)
        assert language is None

    def test_load_book_json_returns_six_tuple_when_missing(
        self, tmp_path: Path
    ) -> None:
        """When no book.json exists, all six values are None/empty."""
        result = publisher._load_book_json(tmp_path)
        assert len(result) == 6
        assert result == (None, (), None, None, None, None)

    def test_project_metadata_language_from_book_json(self, tmp_path: Path) -> None:
        repo = tmp_path / "repo"
        repo.mkdir()
        _write_manifest(
            repo,
            {
                "version": "0.1.0",
                "publish": [],
                "project": {"license": "CC BY 4.0"},
            },
        )
        (repo / "book.json").write_text(
            json.dumps({"title": "B", "author": "A", "language": "en"}),
            encoding="utf-8",
        )

        meta = publisher._resolve_project_metadata(repo / "publish.yml")
        assert meta.language == "en"

    def test_project_metadata_language_none_when_absent(self, tmp_path: Path) -> None:
        repo = tmp_path / "repo"
        repo.mkdir()
        _write_manifest(
            repo,
            {
                "version": "0.1.0",
                "publish": [],
                "project": {"license": "CC BY 4.0"},
            },
        )

        meta = publisher._resolve_project_metadata(repo / "publish.yml")
        assert meta.language is None

    def test_pandoc_metadata_includes_lang(self) -> None:
        meta = publisher.ProjectMetadata(
            name="P",
            authors=("A",),
            license="MIT",
            language="de",
        )
        md = meta.as_pandoc_metadata()
        assert md["lang"] == ["de"]

    def test_pandoc_metadata_excludes_lang_when_none(self) -> None:
        meta = publisher.ProjectMetadata(
            name="P",
            authors=("A",),
            license="MIT",
            language=None,
        )
        md = meta.as_pandoc_metadata()
        assert "lang" not in md


# ── book.json:schema_version validation ──────────────────────────────────────


class TestBookJsonSchemaVersion:
    """Test that schema_version in book.json is validated."""

    def test_valid_schema_version_no_warning(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        (tmp_path / "book.json").write_text(
            json.dumps(
                {
                    "schema_version": "1.0.0",
                    "title": "T",
                    "author": "A",
                }
            ),
            encoding="utf-8",
        )
        publisher._load_book_json(tmp_path)
        assert "kein gültiges SemVer" not in caplog.text

    def test_invalid_schema_version_warns(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        (tmp_path / "book.json").write_text(
            json.dumps(
                {
                    "schema_version": "not-a-version",
                    "title": "T",
                    "author": "A",
                }
            ),
            encoding="utf-8",
        )
        with caplog.at_level("WARNING"):
            publisher._load_book_json(tmp_path)
        assert "kein gültiges SemVer" in caplog.text


# ── fonts.yml:copyright → ATTRIBUTION ────────────────────────────────────────


@pytest.fixture()
def license_fonts_stub(tmp_path: Path) -> Path:
    path = tmp_path / "LICENSE-FONTS"
    path.write_text(
        "Header\n\n"
        "Creative Commons Attribution 4.0 International\n"
        "CC-BY TEXT\n\n"
        "Bitstream Vera License\n"
        "BITSTREAM TEXT\n",
        encoding="utf-8",
    )
    return path


class TestFontAttributionCopyright:
    """Test that fonts.yml copyright field appears in ATTRIBUTION.md."""

    def test_copyright_column_in_attribution(
        self, tmp_path: Path, license_fonts_stub: Path
    ) -> None:
        fonts_yml = tmp_path / "fonts.yml"
        fonts_yml.write_text(
            yaml.safe_dump(
                {
                    "version": "1.0.0",
                    "fonts": {
                        "SERIF": {
                            "name": "DejaVu Serif",
                            "paths": [],
                            "license": "Bitstream Vera License + Public Domain",
                            "license_url": "https://dejavu-fonts.github.io/License.html",
                            "source_url": "https://dejavu-fonts.github.io/",
                            "version": "2.37",
                            "copyright": "© 2003 Bitstream, Inc.",
                            "usage_note": "Embedding unrestricted.",
                        }
                    },
                }
            ),
            encoding="utf-8",
        )

        out_dir = tmp_path / "out"
        result = generate_font_attribution_files(
            out_dir=out_dir,
            fonts_config_path=fonts_yml,
            license_fonts_path=license_fonts_stub,
        )

        text = result.attribution_path.read_text(encoding="utf-8")
        # Table header must have Copyright column
        assert "| Copyright |" in text
        # Copyright value must be rendered
        assert "© 2003 Bitstream, Inc." in text

    def test_missing_copyright_renders_empty_cell(
        self, tmp_path: Path, license_fonts_stub: Path
    ) -> None:
        fonts_yml = tmp_path / "fonts.yml"
        fonts_yml.write_text(
            yaml.safe_dump(
                {
                    "version": "1.0.0",
                    "fonts": {
                        "EMOJI": {
                            "name": "Twemoji Mozilla",
                            "paths": ["/tmp/t.ttf"],
                            "license": "CC BY 4.0",
                            "license_url": "https://creativecommons.org/licenses/by/4.0/",
                            "source_url": "https://example.com",
                            "version": "0.7.0",
                        }
                    },
                }
            ),
            encoding="utf-8",
        )

        out_dir = tmp_path / "out"
        result = generate_font_attribution_files(
            out_dir=out_dir,
            fonts_config_path=fonts_yml,
            license_fonts_path=license_fonts_stub,
        )

        text = result.attribution_path.read_text(encoding="utf-8")
        assert "| Copyright |" in text
        # The EMOJI row should have an empty copyright cell
        lines = [l for l in text.splitlines() if "Twemoji" in l]
        assert len(lines) == 1
        # 6 separators → 7 columns (Asset|Version|License|Copyright|Source|Notes)
        assert lines[0].count("|") >= 7

    def test_font_attribution_entry_has_copyright(self) -> None:
        entry = FontAttributionEntry(
            key="SERIF",
            name="DejaVu",
            version="2.37",
            license="MIT",
            license_url="http://example.com",
            source_url=None,
            usage_note=None,
            copyright="© Bitstream",
        )
        assert entry.copyright == "© Bitstream"

    def test_font_attribution_entry_copyright_none(self) -> None:
        entry = FontAttributionEntry(
            key="SERIF",
            name="DejaVu",
            version="2.37",
            license="MIT",
            license_url="http://example.com",
            source_url=None,
            usage_note=None,
            copyright=None,
        )
        assert entry.copyright is None


# ── docker_config.yml version ────────────────────────────────────────────────


class TestDockerConfigVersion:
    """Test that docker_config.yml has a valid version field."""

    def test_defaults_docker_config_has_version(self) -> None:
        """The shipped defaults file must have a version field."""
        config_path = (
            Path(__file__).resolve().parents[1] / "defaults" / "docker_config.yml"
        )
        assert config_path.exists(), f"Missing: {config_path}"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert "version" in data
        assert is_semver(data["version"])

    def test_smart_merge_validates_version(self, tmp_path: Path) -> None:
        """smart_merge warns when version is missing (non-fatal)."""
        from gitbook_worker.tools.docker.smart_merge import _validate_config_version

        import io
        import contextlib

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _validate_config_version({}, "test.yml")
        assert "no 'version' field" in buf.getvalue()

    def test_smart_merge_validates_bad_version(self, tmp_path: Path) -> None:
        from gitbook_worker.tools.docker.smart_merge import _validate_config_version

        import io
        import contextlib

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _validate_config_version({"version": "abc"}, "test.yml")
        assert "not valid SemVer" in buf.getvalue()

    def test_smart_merge_accepts_good_version(self, tmp_path: Path) -> None:
        from gitbook_worker.tools.docker.smart_merge import _validate_config_version

        import io
        import contextlib

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _validate_config_version({"version": "1.0.0"}, "test.yml")
        assert buf.getvalue() == ""


# ── Config versioning: all defaults have version ─────────────────────────────


class TestAllDefaultsHaveVersion:
    """Every defaults YAML must have a valid SemVer version field (AGENTS §29)."""

    @pytest.mark.parametrize(
        "filename",
        [
            "fonts.yml",
            "frontmatter.yml",
            "readme.yml",
            "smart.yml",
            "docker_config.yml",
        ],
    )
    def test_defaults_yaml_has_semver(self, filename: str) -> None:
        defaults_dir = Path(__file__).resolve().parents[1] / "defaults"
        path = defaults_dir / filename
        assert path.exists(), f"Missing defaults/{filename}"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert "version" in data, f"{filename} has no 'version' field"
        assert is_semver(
            data["version"]
        ), f"{filename} version {data['version']!r} is not valid SemVer"


# ── book.json fallback integration ──────────────────────────────────────────


class TestBookJsonFallbacks:
    """Integration tests for book.json → publish.yml fallback chain."""

    def test_all_fields_from_book_json_fallback(self, tmp_path: Path) -> None:
        """When publish.yml has no project section, all fields come from book.json."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _write_manifest(
            repo,
            {
                "version": "0.1.0",
                "publish": [],
                "project": {"license": "CC BY 4.0", "attribution_policy": "warn"},
            },
        )
        (repo / "book.json").write_text(
            json.dumps(
                {
                    "title": "Fallback Title",
                    "author": "Fallback Author",
                    "date": "2025-12-01",
                    "version": "0.9.0",
                    "language": "fr",
                }
            ),
            encoding="utf-8",
        )

        meta = publisher._resolve_project_metadata(repo / "publish.yml")

        assert meta.name == "Fallback Title"
        assert meta.authors == ("Fallback Author",)
        assert meta.date == "2025-12-01"
        assert meta.version == "0.9.0"
        assert meta.language == "fr"

    def test_full_pandoc_metadata_from_fallback(self, tmp_path: Path) -> None:
        """Pandoc metadata dict includes lang from book.json fallback."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _write_manifest(
            repo,
            {
                "version": "0.1.0",
                "publish": [],
                "project": {"license": "CC BY 4.0", "attribution_policy": "warn"},
            },
        )
        (repo / "book.json").write_text(
            json.dumps(
                {
                    "title": "Book",
                    "author": "Author",
                    "language": "de",
                    "date": "2026-01-01",
                    "version": "1.0.0",
                }
            ),
            encoding="utf-8",
        )

        meta = publisher._resolve_project_metadata(repo / "publish.yml")
        pandoc_md = meta.as_pandoc_metadata()

        assert pandoc_md["lang"] == ["de"]
        assert pandoc_md["author"] == ["Author"]
        assert "2026-01-01" in pandoc_md["date"][0]
        assert "Version 1.0.0" in pandoc_md["date"][0]
