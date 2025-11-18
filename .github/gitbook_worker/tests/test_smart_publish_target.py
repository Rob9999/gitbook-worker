"""Tests for smart_publish_target module.

Tests cover:
- Load publish targets from manifest
- Book.json binding to targets
- Target filtering (build=true)
- Content root resolution
- Default value filling
- Edge cases (missing fields, invalid manifest, etc.)
"""

import json
from pathlib import Path

import pytest
import yaml

from tools.utils.smart_publish_target import (
    PublishTarget,
    find_target_by_path,
    get_buildable_targets,
    get_target_content_root,
    load_publish_targets,
)


@pytest.fixture
def temp_manifest(tmp_path):
    """Create temporary publish.yml manifest."""
    manifest = tmp_path / "publish.yml"
    data = {
        "publish": [
            {
                "path": ".",
                "out": "book.pdf",
                "source_type": "folder",
                "use_book_json": True,
                "use_summary": True,
                "build": True,
            },
            {
                "path": "docs/",
                "out": "docs.pdf",
                "source_type": "folder",
                "build": False,
            },
            {
                "path": "README.md",
                "out": "readme.pdf",
                "source_type": "file",
                "build": True,
            },
        ]
    }
    with open(manifest, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)
    return manifest


@pytest.fixture
def temp_gitbook_manifest(tmp_path):
    """Create manifest with GitBook project."""
    # Create book.json
    project = tmp_path
    book_json = project / "book.json"
    book_json.write_text(
        json.dumps(
            {
                "root": "./content",
                "structure": {"summary": "SUMMARY.md"},
                "title": "Test Book",
            }
        )
    )

    # Create content directory
    content = project / "content"
    content.mkdir()

    # Create manifest
    manifest = project / "publish.yml"
    data = {
        "publish": [
            {
                "path": ".",
                "out": "book.pdf",
                "use_book_json": True,
                "build": True,
            }
        ]
    }
    with open(manifest, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

    return manifest


class TestLoadPublishTargets:
    """Tests for load_publish_targets function."""

    def test_load_all_targets(self, temp_manifest):
        """Should load all targets from manifest."""
        targets = load_publish_targets(temp_manifest, only_build=False)

        assert len(targets) == 3
        assert all(isinstance(t, PublishTarget) for t in targets)

    def test_load_only_buildable(self, temp_manifest):
        """Should filter targets by build=True."""
        targets = load_publish_targets(temp_manifest, only_build=True)

        assert len(targets) == 2
        assert all(t.build is True for t in targets)
        assert targets[0].out == "book.pdf"
        assert targets[1].out == "readme.pdf"

    def test_target_indices(self, temp_manifest):
        """Should assign correct indices."""
        targets = load_publish_targets(temp_manifest, only_build=False)

        assert targets[0].index == 0
        assert targets[1].index == 1
        assert targets[2].index == 2

    def test_target_paths_resolved(self, temp_manifest):
        """Should resolve paths to Path objects."""
        targets = load_publish_targets(temp_manifest, only_build=False)

        assert isinstance(targets[0].path, Path)
        assert isinstance(targets[0].out_dir, Path)

    def test_target_defaults(self, temp_manifest):
        """Should fill default values."""
        targets = load_publish_targets(temp_manifest, only_build=False)

        # Check defaults
        assert targets[0].out_format == "pdf"
        assert targets[0].source_format == "markdown"
        # out_dir is resolved relative to manifest path
        assert targets[0].out_dir.name == "publish"
        assert targets[0].keep_combined is False


class TestBookJsonBinding:
    """Tests for book.json configuration binding."""

    def test_bind_book_config(self, temp_gitbook_manifest):
        """Should discover and bind book.json."""
        targets = load_publish_targets(temp_gitbook_manifest, only_build=False)

        assert len(targets) == 1
        target = targets[0]

        # Should have book_config bound
        assert target.book_config is not None
        assert target.book_config.title == "Test Book"
        assert target.book_config.content_root.name == "content"

    def test_no_binding_when_disabled(self, tmp_path):
        """Should not bind book.json when use_book_json=False."""
        # Create book.json (should be ignored)
        book_json = tmp_path / "book.json"
        book_json.write_text(json.dumps({"root": "./content"}))

        # Create manifest without use_book_json
        manifest = tmp_path / "publish.yml"
        data = {
            "publish": [
                {
                    "path": ".",
                    "out": "book.pdf",
                    "use_book_json": False,
                    "build": True,
                }
            ]
        }
        with open(manifest, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f)

        targets = load_publish_targets(manifest, only_build=False)

        # Should not have book_config
        assert targets[0].book_config is None

    def test_graceful_missing_book_json(self, tmp_path):
        """Should handle missing book.json gracefully."""
        manifest = tmp_path / "publish.yml"
        data = {
            "publish": [
                {
                    "path": ".",
                    "out": "book.pdf",
                    "use_book_json": True,  # Requested but not found
                    "build": True,
                }
            ]
        }
        with open(manifest, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f)

        targets = load_publish_targets(manifest, only_build=False)

        # Should succeed without book_config
        assert len(targets) == 1
        # book_config might be None or have fallback values


class TestGetBuildableTargets:
    """Tests for get_buildable_targets convenience function."""

    def test_get_buildable(self, temp_manifest):
        """Should return only buildable targets."""
        targets = get_buildable_targets(temp_manifest)

        assert len(targets) == 2
        assert all(t.build is True for t in targets)


class TestFindTargetByPath:
    """Tests for find_target_by_path function."""

    def test_find_existing_target(self, temp_manifest):
        """Should find target by path."""
        targets = load_publish_targets(temp_manifest, only_build=False)

        # Need to use full resolved path
        readme_path = temp_manifest.parent / "README.md"
        target = find_target_by_path(targets, readme_path)

        assert target is not None
        assert target.out == "readme.pdf"

    def test_find_with_path_object(self, temp_manifest):
        """Should accept Path object."""
        targets = load_publish_targets(temp_manifest, only_build=False)

        # Need to use full resolved path
        readme_path = temp_manifest.parent / "README.md"
        target = find_target_by_path(targets, readme_path)

        assert target is not None
        assert target.out == "readme.pdf"

    def test_find_nonexistent(self, temp_manifest):
        """Should return None for nonexistent path."""
        targets = load_publish_targets(temp_manifest, only_build=False)

        target = find_target_by_path(targets, "nonexistent.md")

        assert target is None


class TestGetTargetContentRoot:
    """Tests for get_target_content_root function."""

    def test_content_root_from_book_json(self, temp_gitbook_manifest):
        """Should get content root from book.json."""
        targets = load_publish_targets(temp_gitbook_manifest, only_build=False)

        content_root = get_target_content_root(targets[0])

        assert content_root.name == "content"

    def test_content_root_fallback(self, temp_manifest):
        """Should fallback to target path when no book.json."""
        targets = load_publish_targets(temp_manifest, only_build=False)

        # Target without book.json
        content_root = get_target_content_root(targets[1])

        # Should use target path
        assert "docs" in str(content_root)


class TestPublishTargetDataclass:
    """Tests for PublishTarget dataclass."""

    def test_target_immutable(self, temp_manifest):
        """Should be immutable (frozen)."""
        targets = load_publish_targets(temp_manifest, only_build=False)

        with pytest.raises(AttributeError):
            targets[0].build = False

    def test_target_has_all_fields(self, temp_manifest):
        """Should have all expected fields."""
        targets = load_publish_targets(temp_manifest, only_build=False)
        target = targets[0]

        # Check key fields exist
        assert hasattr(target, "index")
        assert hasattr(target, "path")
        assert hasattr(target, "out")
        assert hasattr(target, "source_type")
        assert hasattr(target, "use_book_json")
        assert hasattr(target, "build")
        assert hasattr(target, "book_config")
        assert hasattr(target, "assets")
        assert hasattr(target, "pdf_options")
        assert hasattr(target, "raw_entry")


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_manifest(self, tmp_path):
        """Should handle empty publish list."""
        manifest = tmp_path / "publish.yml"
        data = {"publish": []}
        with open(manifest, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f)

        targets = load_publish_targets(manifest, only_build=False)

        assert targets == []

    def test_minimal_entry(self, tmp_path):
        """Should handle minimal manifest entry."""
        manifest = tmp_path / "publish.yml"
        data = {
            "publish": [
                {
                    "path": ".",
                    "out": "minimal.pdf",
                }
            ]
        }
        with open(manifest, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f)

        targets = load_publish_targets(manifest, only_build=False)

        assert len(targets) == 1
        # Should fill defaults
        assert targets[0].source_type in ["file", "folder"]
        assert targets[0].build is False  # Default

    def test_malformed_yaml(self, tmp_path):
        """Should handle malformed YAML gracefully."""
        manifest = tmp_path / "publish.yml"
        manifest.write_text("{ malformed yaml }")

        # Current implementation logs warning and returns empty list
        targets = load_publish_targets(manifest, only_build=False)
        assert targets == []

    def test_missing_required_fields(self, tmp_path):
        """Should handle missing required fields."""
        manifest = tmp_path / "publish.yml"
        data = {
            "publish": [
                {
                    "path": ".",
                    # Missing "out" field
                }
            ]
        }
        with open(manifest, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f)

        # Should either raise error or provide default
        try:
            targets = load_publish_targets(manifest, only_build=False)
            # If it succeeds, check it has some out value
            if targets:
                assert targets[0].out is not None
        except (KeyError, ValueError):
            # Expected if "out" is truly required
            pass


class TestAssetsAndPdfOptions:
    """Tests for assets and PDF options handling."""

    def test_load_assets(self, tmp_path):
        """Should load assets configuration."""
        manifest = tmp_path / "publish.yml"
        data = {
            "publish": [
                {
                    "path": ".",
                    "out": "book.pdf",
                    "assets": [
                        {"type": "css", "path": "style.css"},
                        {"type": "logo", "path": "logo.png"},
                    ],
                }
            ]
        }
        with open(manifest, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f)

        targets = load_publish_targets(manifest, only_build=False)

        assert len(targets[0].assets) == 2
        assert targets[0].assets[0]["type"] == "css"

    def test_load_pdf_options(self, tmp_path):
        """Should load PDF-specific options."""
        manifest = tmp_path / "publish.yml"
        data = {
            "publish": [
                {
                    "path": ".",
                    "out": "book.pdf",
                    "pdf_options": {
                        "paper_format": "A4",
                        "geometry": "margin=2cm",
                        "emoji_color": False,
                    },
                }
            ]
        }
        with open(manifest, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f)

        targets = load_publish_targets(manifest, only_build=False)

        assert targets[0].pdf_options["paper_format"] == "A4"
        assert targets[0].pdf_options["geometry"] == "margin=2cm"
        assert targets[0].pdf_options["emoji_color"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
