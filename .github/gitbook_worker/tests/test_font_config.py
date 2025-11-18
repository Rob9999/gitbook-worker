#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for font configuration loading."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tools.publishing.font_config import (
    FontConfig,
    FontConfigLoader,
    get_font_config,
    reset_font_config,
)


@pytest.fixture
def sample_fonts_yml(tmp_path):
    """Create a sample fonts.yml file for testing."""
    fonts_yml = tmp_path / "fonts.yml"
    fonts_yml.write_text(
        """
version: 1.0.0
fonts:
  CJK:
    name: "ERDA CC-BY CJK"
    license: "CC BY 4.0"
    license_url: "https://creativecommons.org/licenses/by/4.0/"
    paths:
      - ".github/fonts/erda-ccby-cjk/true-type/erda-ccby-cjk.ttf"
      - ".github/fonts/erda-ccby-cjk.ttf"
      - ".github/gitbook_worker/tools/publishing/fonts/truetype/erdafont/erda-ccby-cjk.ttf"
  SERIF:
    name: "DejaVu Serif"
    license: "Custom (Bitstream Vera / DejaVu)"
    license_url: "https://dejavu-fonts.github.io/License.html"
    paths: []
  SANS:
    name: "DejaVu Sans"
    license: "Custom (Bitstream Vera / DejaVu)"
    license_url: "https://dejavu-fonts.github.io/License.html"
    paths: []
  MONO:
    name: "DejaVu Sans Mono"
    license: "Custom (Bitstream Vera / DejaVu)"
    license_url: "https://dejavu-fonts.github.io/License.html"
    paths: []
  EMOJI:
    name: "Twemoji Mozilla"
    license: "CC BY 4.0"
    license_url: "https://creativecommons.org/licenses/by/4.0/"
    paths: []
""",
        encoding="utf-8",
    )
    return fonts_yml


def test_font_config_dataclass():
    """Test FontConfig dataclass creation."""
    config = FontConfig(
        name="Test Font",
        paths=["/path/to/font.ttf"],
        license="MIT",
        license_url="https://example.com/license",
        source_url="https://example.com/source",
    )

    assert config.name == "Test Font"
    assert config.paths == ["/path/to/font.ttf"]
    assert config.license == "MIT"
    assert config.license_url == "https://example.com/license"
    assert config.source_url == "https://example.com/source"


def test_font_config_loader_init(sample_fonts_yml):
    """Test FontConfigLoader initialization."""
    loader = FontConfigLoader(config_path=sample_fonts_yml)
    assert loader._config_path == sample_fonts_yml
    assert len(loader._fonts) == 5  # CJK, SERIF, SANS, MONO, EMOJI
    assert loader.version == "1.0.0"


def test_get_font(sample_fonts_yml):
    """Test getting font configuration by key."""
    loader = FontConfigLoader(config_path=sample_fonts_yml)

    cjk = loader.get_font("CJK")
    assert cjk is not None
    assert cjk.name == "ERDA CC-BY CJK"
    assert len(cjk.paths) == 3
    assert cjk.license == "CC BY 4.0"

    serif = loader.get_font("SERIF")
    assert serif is not None
    assert serif.name == "DejaVu Serif"
    assert len(serif.paths) == 0


def test_get_font_case_insensitive(sample_fonts_yml):
    """Test that font keys are case-insensitive."""
    loader = FontConfigLoader(config_path=sample_fonts_yml)

    assert loader.get_font("cjk") is not None
    assert loader.get_font("CJK") is not None
    assert loader.get_font("Cjk") is not None


def test_get_font_name(sample_fonts_yml):
    """Test getting font name by key."""
    loader = FontConfigLoader(config_path=sample_fonts_yml)

    assert loader.get_font_name("CJK") == "ERDA CC-BY CJK"
    assert loader.get_font_name("SERIF") == "DejaVu Serif"
    assert loader.get_font_name("NONEXISTENT", "Default") == "Default"


def test_get_font_paths(sample_fonts_yml):
    """Test getting font paths by key."""
    loader = FontConfigLoader(config_path=sample_fonts_yml)

    cjk_paths = loader.get_font_paths("CJK")
    assert len(cjk_paths) == 3
    assert ".github/fonts/erda-ccby-cjk/true-type/erda-ccby-cjk.ttf" in cjk_paths

    serif_paths = loader.get_font_paths("SERIF")
    assert len(serif_paths) == 0

    unknown_paths = loader.get_font_paths("UNKNOWN")
    assert len(unknown_paths) == 0


def test_find_font_file(sample_fonts_yml, tmp_path):
    """Test finding existing font files."""
    # Create a test font file
    font_dir = tmp_path / ".github" / "fonts" / "erda-ccby-cjk" / "true-type"
    font_dir.mkdir(parents=True)
    font_file = font_dir / "erda-ccby-cjk.ttf"
    font_file.write_text("fake font data")

    # Update paths in config to use tmp_path
    loader = FontConfigLoader(config_path=sample_fonts_yml)
    loader._fonts["CJK"] = FontConfig(
        name="ERDA CC-BY CJK",
        paths=[str(font_file)],
        license="CC BY 4.0",
        license_url="https://creativecommons.org/licenses/by/4.0/",
    )

    found = loader.find_font_file("CJK")
    assert found == str(font_file)

    # Test non-existent font
    found = loader.find_font_file("SERIF")
    assert found is None


def test_get_all_font_keys(sample_fonts_yml):
    """Test getting all font configuration keys."""
    loader = FontConfigLoader(config_path=sample_fonts_yml)
    keys = loader.get_all_font_keys()

    assert "CJK" in keys
    assert "SERIF" in keys
    assert "SANS" in keys
    assert "MONO" in keys
    assert "EMOJI" in keys
    assert len(keys) == 5


def test_get_default_fonts(sample_fonts_yml):
    """Test getting default font mapping."""
    loader = FontConfigLoader(config_path=sample_fonts_yml)
    defaults = loader.get_default_fonts()

    assert defaults["serif"] == "DejaVu Serif"
    assert defaults["sans"] == "DejaVu Sans"
    assert defaults["mono"] == "DejaVu Sans Mono"
    assert defaults["emoji"] == "Twemoji Mozilla"
    assert defaults["cjk"] == "ERDA CC-BY CJK"


def test_singleton_pattern():
    """Test that get_font_config returns singleton instance."""
    reset_font_config()  # Reset to ensure clean state

    loader1 = get_font_config()
    loader2 = get_font_config()

    assert loader1 is loader2


def test_reset_font_config():
    """Test resetting the global font config."""
    reset_font_config()
    loader1 = get_font_config()

    reset_font_config()
    loader2 = get_font_config()

    # After reset, should get a new instance
    assert loader1 is not loader2


def test_missing_fonts_yml():
    """Test error handling when fonts.yml is missing."""
    with patch.object(FontConfigLoader, "_find_config_file") as mock_find:
        mock_find.side_effect = FileNotFoundError("fonts.yml not found")

        with pytest.raises(FileNotFoundError, match="fonts.yml not found"):
            FontConfigLoader()


def test_malformed_yaml(tmp_path):
    """Test error handling for malformed YAML."""
    bad_yml = tmp_path / "bad_fonts.yml"
    bad_yml.write_text("{ invalid yaml content: [ unclosed", encoding="utf-8")

    with pytest.raises(Exception):  # YAML parsing error
        FontConfigLoader(config_path=bad_yml)


def test_empty_fonts_section(tmp_path):
    """Test handling of empty fonts section."""
    empty_yml = tmp_path / "empty_fonts.yml"
    empty_yml.write_text("fonts: {}", encoding="utf-8")

    loader = FontConfigLoader(config_path=empty_yml)
    assert len(loader._fonts) == 0
    assert loader.get_font("CJK") is None


def test_filter_empty_paths(tmp_path):
    """Test that empty/None paths are filtered out."""
    yml = tmp_path / "fonts.yml"
    yml.write_text(
        """
fonts:
  TEST:
    name: "Test Font"
    license: "MIT"
    license_url: "https://example.com"
    paths:
      - "/valid/path.ttf"
      - null
      - ""
      - "/another/valid.ttf"
""",
        encoding="utf-8",
    )

    loader = FontConfigLoader(config_path=yml)
    paths = loader.get_font_paths("TEST")

    assert len(paths) == 2
    assert "/valid/path.ttf" in paths
    assert "/another/valid.ttf" in paths


def test_match_font_key(sample_fonts_yml):
    """Test font name to key matching."""
    loader = FontConfigLoader(config_path=sample_fonts_yml)

    # Exact match
    assert loader.match_font_key("ERDA CC-BY CJK") == "CJK"
    assert loader.match_font_key("DejaVu Serif") == "SERIF"
    assert loader.match_font_key("DejaVu Sans") == "SANS"
    assert loader.match_font_key("DejaVu Sans Mono") == "MONO"
    assert loader.match_font_key("Twemoji Mozilla") == "EMOJI"

    # Case-insensitive partial match
    assert loader.match_font_key("erda cc-by cjk") == "CJK"
    assert loader.match_font_key("dejavu serif") == "SERIF"

    # No match
    assert loader.match_font_key("Unknown Font") is None
    assert loader.match_font_key(None) is None
    assert loader.match_font_key("") is None


def test_merge_manifest_fonts_basic(sample_fonts_yml):
    """Test basic manifest font merging."""
    loader = FontConfigLoader(config_path=sample_fonts_yml)

    # Manifest overrides CJK font path
    manifest = [{"name": "ERDA CC-BY CJK", "path": "/custom/erda-font.ttf"}]

    merged = loader.merge_manifest_fonts(manifest)

    # CJK should have new path
    assert merged.get_font_paths("CJK") == ["/custom/erda-font.ttf"]

    # Other fonts unchanged
    assert merged.get_font_paths("SERIF") == []
    assert merged.get_font_name("SERIF") == "DejaVu Serif"


def test_merge_manifest_fonts_multiple(sample_fonts_yml):
    """Test merging multiple manifest fonts."""
    loader = FontConfigLoader(config_path=sample_fonts_yml)

    manifest = [
        {"name": "ERDA CC-BY CJK", "path": "/custom/cjk.ttf"},
        {"name": "DejaVu Sans", "path": "/custom/sans.ttf"},
    ]

    merged = loader.merge_manifest_fonts(manifest)

    assert merged.get_font_paths("CJK") == ["/custom/cjk.ttf"]
    assert merged.get_font_paths("SANS") == ["/custom/sans.ttf"]
    assert merged.get_font_paths("SERIF") == []  # Unchanged


def test_merge_manifest_fonts_preserves_metadata(sample_fonts_yml):
    """Test that manifest merge preserves license metadata."""
    loader = FontConfigLoader(config_path=sample_fonts_yml)

    manifest = [{"name": "ERDA CC-BY CJK", "path": "/custom/erda.ttf"}]

    merged = loader.merge_manifest_fonts(manifest)

    cjk = merged.get_font("CJK")
    assert cjk is not None
    assert cjk.name == "ERDA CC-BY CJK"
    assert cjk.license == "CC BY 4.0"
    assert cjk.license_url == "https://creativecommons.org/licenses/by/4.0/"
    assert cjk.paths == ["/custom/erda.ttf"]


def test_merge_manifest_fonts_unknown_font(sample_fonts_yml):
    """Test that unknown fonts in manifest are ignored."""
    loader = FontConfigLoader(config_path=sample_fonts_yml)

    manifest = [{"name": "Unknown Font", "path": "/unknown/font.ttf"}]

    merged = loader.merge_manifest_fonts(manifest)

    # Should not crash, just ignore unknown font
    assert merged.get_all_font_keys() == loader.get_all_font_keys()


def test_merge_manifest_fonts_invalid_entries(sample_fonts_yml):
    """Test that invalid manifest entries are skipped."""
    loader = FontConfigLoader(config_path=sample_fonts_yml)

    manifest = [
        {"name": "ERDA CC-BY CJK"},  # Missing path
        {"path": "/some/font.ttf"},  # Missing name
        "invalid string entry",  # Not a dict
        {"name": "DejaVu Sans", "path": "/valid/sans.ttf"},  # Valid
    ]

    merged = loader.merge_manifest_fonts(manifest)

    # Only valid entry should be applied
    assert merged.get_font_paths("SANS") == ["/valid/sans.ttf"]
    assert merged.get_font_paths("CJK") != []  # Should be unchanged


def test_merge_manifest_fonts_empty_list(sample_fonts_yml):
    """Test merging with empty manifest list."""
    loader = FontConfigLoader(config_path=sample_fonts_yml)

    merged = loader.merge_manifest_fonts([])

    # All fonts should be unchanged
    assert merged.get_font_paths("CJK") == loader.get_font_paths("CJK")
    assert merged.get_font_name("SERIF") == loader.get_font_name("SERIF")


def test_merge_manifest_fonts_creates_new_instance(sample_fonts_yml):
    """Test that merge creates a new loader instance."""
    loader = FontConfigLoader(config_path=sample_fonts_yml)

    manifest = [{"name": "ERDA CC-BY CJK", "path": "/custom/font.ttf"}]

    merged = loader.merge_manifest_fonts(manifest)

    # Should be different instances
    assert merged is not loader

    # Original should be unchanged
    assert loader.get_font_paths("CJK") != ["/custom/font.ttf"]

    # Merged should have override
    assert merged.get_font_paths("CJK") == ["/custom/font.ttf"]


def test_font_config_requires_semver(tmp_path):
    """fonts.yml must define a semantic version."""

    fonts_yml = tmp_path / "fonts.yml"
    fonts_yml.write_text("version: not-a-version\nfonts: {}\n", encoding="utf-8")

    with pytest.raises(ValueError):
        FontConfigLoader(config_path=fonts_yml)
