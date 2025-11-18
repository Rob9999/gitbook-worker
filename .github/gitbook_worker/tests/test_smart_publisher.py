"""Tests for smart_publisher module.

Tests cover:
- SmartPublisher initialization
- Target loading (lazy + caching)
- Environment preparation
- build_target() with various configurations
- build_all() workflow
- BuildResult dataclass
- publish_from_manifest() convenience function
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from tools.utils.smart_publisher import (
    BuildResult,
    SmartPublisher,
    publish_from_manifest,
)


@pytest.fixture
def temp_manifest(tmp_path):
    """Create temporary manifest with multiple targets."""
    manifest = tmp_path / "publish.yml"
    data = {
        "publish": [
            {
                "path": ".",
                "out": "book.pdf",
                "source_type": "folder",
                "use_book_json": True,
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


@pytest.fixture
def mock_legacy_publisher():
    """Mock legacy publisher module."""
    with patch("tools.utils.smart_publisher.legacy_publisher") as mock:
        # Setup default successful behavior
        mock.prepare_publishing.return_value = None
        mock.build_pdf.return_value = (True, None)
        yield mock


class TestSmartPublisherInit:
    """Tests for SmartPublisher initialization."""

    def test_init_with_path_string(self, temp_manifest):
        """Should accept string path."""
        publisher = SmartPublisher(str(temp_manifest))

        assert publisher.manifest_path == temp_manifest.resolve()
        assert publisher.only_build is True  # Default

    def test_init_with_path_object(self, temp_manifest):
        """Should accept Path object."""
        publisher = SmartPublisher(temp_manifest)

        assert publisher.manifest_path == temp_manifest.resolve()

    def test_init_with_options(self, temp_manifest):
        """Should accept only_build and no_apt options."""
        publisher = SmartPublisher(temp_manifest, only_build=False, no_apt=True)

        assert publisher.only_build is False
        assert publisher.no_apt is True

    def test_targets_lazy_loading(self, temp_manifest):
        """Should not load targets until accessed."""
        publisher = SmartPublisher(temp_manifest)

        # Should not be loaded yet
        assert publisher._targets is None

        # Access should trigger loading
        targets = publisher.targets

        assert publisher._targets is not None
        assert len(targets) > 0

    def test_targets_caching(self, temp_manifest):
        """Should cache loaded targets."""
        publisher = SmartPublisher(temp_manifest)

        # Load twice
        targets1 = publisher.targets
        targets2 = publisher.targets

        # Should be same object (cached)
        assert targets1 is targets2


class TestLoadTargets:
    """Tests for target loading."""

    def test_load_only_buildable(self, temp_manifest):
        """Should load only buildable targets by default."""
        publisher = SmartPublisher(temp_manifest, only_build=True)

        targets = publisher.targets

        assert len(targets) == 2  # book.pdf + readme.pdf
        assert all(t.build is True for t in targets)

    def test_load_all_targets(self, temp_manifest):
        """Should load all targets when only_build=False."""
        publisher = SmartPublisher(temp_manifest, only_build=False)

        targets = publisher.targets

        assert len(targets) == 3


class TestPrepareEnvironment:
    """Tests for environment preparation."""

    def test_prepare_calls_legacy(self, temp_manifest, mock_legacy_publisher):
        """Should call legacy prepare_publishing."""
        publisher = SmartPublisher(temp_manifest)

        result = publisher.prepare_environment()

        assert result is True
        mock_legacy_publisher.prepare_publishing.assert_called_once()

    def test_prepare_passes_no_apt(self, temp_manifest, mock_legacy_publisher):
        """Should pass no_apt option to legacy function."""
        publisher = SmartPublisher(temp_manifest, no_apt=True)

        publisher.prepare_environment()

        call_kwargs = mock_legacy_publisher.prepare_publishing.call_args.kwargs
        assert call_kwargs["no_apt"] is True

    def test_prepare_idempotent(self, temp_manifest, mock_legacy_publisher):
        """Should skip preparation if already done."""
        publisher = SmartPublisher(temp_manifest)

        publisher.prepare_environment()
        publisher.prepare_environment()

        # Should only call once
        assert mock_legacy_publisher.prepare_publishing.call_count == 1

    def test_prepare_failure(self, temp_manifest, mock_legacy_publisher):
        """Should handle preparation failure."""
        mock_legacy_publisher.prepare_publishing.side_effect = Exception("Prep failed")

        publisher = SmartPublisher(temp_manifest)
        result = publisher.prepare_environment()

        assert result is False
        assert publisher._prepared is False

    def test_prepare_missing_legacy(self, temp_manifest):
        """Should handle missing legacy publisher."""
        with patch("tools.utils.smart_publisher.legacy_publisher", None):
            publisher = SmartPublisher(temp_manifest)
            result = publisher.prepare_environment()

            assert result is False


class TestBuildTarget:
    """Tests for building individual targets."""

    def test_build_success(self, temp_manifest, mock_legacy_publisher):
        """Should build target successfully."""
        publisher = SmartPublisher(temp_manifest)
        target = publisher.targets[0]

        result = publisher.build_target(target)

        assert isinstance(result, BuildResult)
        assert result.success is True
        assert result.target == target
        assert result.error_message is None

    def test_build_failure(self, temp_manifest, mock_legacy_publisher):
        """Should handle build failure."""
        mock_legacy_publisher.build_pdf.return_value = (
            False,
            "Build failed",
        )

        publisher = SmartPublisher(temp_manifest)
        target = publisher.targets[0]

        result = publisher.build_target(target)

        assert result.success is False
        assert result.error_message == "Build failed"

    def test_build_calls_legacy(self, temp_manifest, mock_legacy_publisher):
        """Should call legacy build_pdf with correct args."""
        publisher = SmartPublisher(temp_manifest)
        target = publisher.targets[0]

        publisher.build_target(target)

        mock_legacy_publisher.build_pdf.assert_called_once()

    def test_build_missing_legacy(self, temp_manifest):
        """Should handle missing legacy publisher."""
        with patch("tools.utils.smart_publisher.legacy_publisher", None):
            publisher = SmartPublisher(temp_manifest)
            target = publisher.targets[0]

            result = publisher.build_target(target)

            assert result.success is False
            assert "not available" in result.error_message.lower()


class TestBuildAll:
    """Tests for building all targets."""

    def test_build_all_targets(self, temp_manifest, mock_legacy_publisher):
        """Should build all loaded targets."""
        publisher = SmartPublisher(temp_manifest, only_build=True)

        results = publisher.build_all()

        assert len(results) == 2  # Two buildable targets
        assert all(isinstance(r, BuildResult) for r in results)

    def test_build_all_success(self, temp_manifest, mock_legacy_publisher):
        """Should report all successful builds."""
        publisher = SmartPublisher(temp_manifest, only_build=True)

        results = publisher.build_all()

        assert all(r.success for r in results)

    def test_build_all_partial_failure(self, temp_manifest, mock_legacy_publisher):
        """Should continue building after failure."""
        # First call succeeds, second fails
        mock_legacy_publisher.build_pdf.side_effect = [
            (True, None),
            (False, "Build failed"),
        ]

        publisher = SmartPublisher(temp_manifest, only_build=True)
        results = publisher.build_all()

        assert len(results) == 2
        assert results[0].success is True
        assert results[1].success is False


class TestPublishFromManifest:
    """Tests for publish_from_manifest convenience function."""

    def test_convenience_function(self, temp_manifest, mock_legacy_publisher):
        """Should run full publish workflow."""
        success, failed = publish_from_manifest(temp_manifest)

        # Returns tuple of (success_count, failed_count)
        assert isinstance(success, int)
        assert isinstance(failed, int)
        assert success + failed > 0

    def test_convenience_with_options(self, temp_manifest, mock_legacy_publisher):
        """Should accept workflow options."""
        success, failed = publish_from_manifest(
            temp_manifest, only_build=False, no_apt=True
        )

        # Should include non-buildable targets
        assert success + failed == 3


class TestBuildResultDataclass:
    """Tests for BuildResult dataclass."""

    def test_create_success_result(self, temp_manifest):
        """Should create success result."""
        publisher = SmartPublisher(temp_manifest)
        target = publisher.targets[0]

        result = BuildResult(
            target=target,
            success=True,
            output_path=Path("publish/book.pdf"),
            error_message=None,
        )

        assert result.success is True
        assert result.output_path == Path("publish/book.pdf")

    def test_create_failure_result(self, temp_manifest):
        """Should create failure result."""
        publisher = SmartPublisher(temp_manifest)
        target = publisher.targets[0]

        result = BuildResult(
            target=target,
            success=False,
            output_path=None,
            error_message="Build error",
        )

        assert result.success is False
        assert result.error_message == "Build error"

    def test_result_immutable(self, temp_manifest):
        """Should be immutable (frozen)."""
        publisher = SmartPublisher(temp_manifest)
        target = publisher.targets[0]

        result = BuildResult(
            target=target,
            success=True,
            output_path=None,
            error_message=None,
        )

        with pytest.raises(AttributeError):
            result.success = False


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_manifest(self, tmp_path, mock_legacy_publisher):
        """Should handle empty manifest."""
        manifest = tmp_path / "publish.yml"
        data = {"publish": []}
        with open(manifest, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f)

        publisher = SmartPublisher(manifest)
        results = publisher.build_all()

        assert results == []

    def test_nonexistent_manifest(self, tmp_path):
        """Should handle nonexistent manifest gracefully."""
        manifest = tmp_path / "nonexistent.yml"

        # Current implementation logs error and returns empty list
        publisher = SmartPublisher(manifest)
        targets = publisher.targets
        assert targets == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
