"""Tests for smart_manage_publish_flags module.

Tests cover:
- Set flags based on git changes (with/without book.json)
- Reset flags for specific targets
- Root path matching
- Book.json content_root awareness
- Shallow clone fallback
- Error handling
"""

import json
import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from tools.utils.smart_git import get_changed_files, normalize_posix
from tools.utils.smart_manage_publish_flags import (
    find_publish_file,
    get_entry_type,
    is_path_match,
    load_publish_manifest,
    reset_publish_flags,
    resolve_entry_path,
    save_publish_manifest,
    set_publish_flags,
)


@pytest.fixture
def temp_manifest(tmp_path):
    """Create a temporary publish.yml manifest."""
    manifest = tmp_path / "publish.yml"
    data = {
        "publish": [
            {
                "path": ".",
                "out": "book.pdf",
                "type": "folder",
                "build": False,
                "use_book_json": True,
            },
            {
                "path": "content/",
                "out": "content.pdf",
                "type": "folder",
                "build": False,
                "use_book_json": False,
            },
            {
                "path": "README.md",
                "out": "readme.pdf",
                "type": "file",
                "build": False,
            },
        ]
    }
    with open(manifest, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)
    return manifest


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary git repository."""
    repo = tmp_path / "repo"
    repo.mkdir()

    # Initialize git
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    # Create initial commit
    readme = repo / "README.md"
    readme.write_text("# Test\n")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    # Create second commit to ensure diff-tree works
    # (diff-tree on first commit may return empty in some Git versions)
    docs = repo / "docs"
    docs.mkdir()
    doc_file = docs / "example.md"
    doc_file.write_text("# Example\n")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add docs"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    return repo


class TestNormalizePosix:
    """Tests for POSIX path normalization."""

    def test_normalize_windows_path(self):
        """Should convert backslashes to forward slashes."""
        assert normalize_posix("content\\file.md") == "content/file.md"

    def test_normalize_leading_dot_slash(self):
        """Should remove leading ./ prefix."""
        assert normalize_posix("./content/file.md") == "content/file.md"

    def test_normalize_already_normalized(self):
        """Should handle already normalized paths."""
        assert normalize_posix("content/file.md") == "content/file.md"

    def test_normalize_root_dot(self):
        """Should normalize root . to ."""
        assert normalize_posix(".") == "."


class TestGetEntryType:
    """Tests for entry type extraction."""

    def test_get_type_from_source_type(self):
        """Should extract from source_type field."""
        entry = {"source_type": "folder"}
        assert get_entry_type(entry) == "folder"

    def test_get_type_from_type_field(self):
        """Should fallback to type field."""
        entry = {"type": "file"}
        assert get_entry_type(entry) == "file"

    def test_get_type_default_auto(self):
        """Should default to auto if both missing."""
        entry = {}
        assert get_entry_type(entry) == "auto"

    def test_get_type_normalizes_case(self):
        """Should normalize to lowercase."""
        entry = {"source_type": "FOLDER"}
        assert get_entry_type(entry) == "folder"


class TestIsPathMatch:
    """Tests for path matching logic."""

    def test_root_path_matches_everything(self):
        """Root path (.) should match all files."""
        assert is_path_match(".", "folder", "content/file.md") is True
        assert is_path_match("", "folder", "README.md") is True

    def test_folder_matches_contained_file(self):
        """Folder should match files within it."""
        assert is_path_match("content", "folder", "content/file.md") is True
        assert is_path_match("content", "folder", "content/sub/file.md") is True

    def test_folder_no_match_outside(self):
        """Folder should not match files outside it."""
        assert is_path_match("content", "folder", "other/file.md") is False

    def test_file_exact_match(self):
        """File type should require exact match."""
        assert is_path_match("README.md", "file", "README.md") is True
        assert is_path_match("README.md", "file", "OTHER.md") is False

    def test_auto_type_folder_heuristic(self):
        """Auto type should detect folders by lack of extension."""
        assert is_path_match("content", "auto", "content/file.md") is True

    def test_content_root_override(self):
        """Should use content_root when provided (book.json awareness)."""
        # Entry path is "." but content_root from book.json is "content/"
        assert (
            is_path_match(".", "folder", "content/file.md", content_root="content")
            is True
        )
        assert (
            is_path_match(".", "folder", "outside/file.md", content_root="content")
            is False
        )


class TestResolveEntryPath:
    """Tests for entry path resolution."""

    def test_resolve_relative_to_manifest(self):
        """Should resolve path relative to manifest directory."""
        result = resolve_entry_path(
            "content",
            manifest_dir=Path("/repo/publish"),
            repo_root=Path("/repo"),
        )
        assert result == "publish/content"

    def test_resolve_root_dot(self):
        """Should handle root . path."""
        result = resolve_entry_path(
            ".",
            manifest_dir=Path("/repo"),
            repo_root=Path("/repo"),
        )
        assert result == "."


class TestManifestOperations:
    """Tests for manifest loading/saving."""

    def test_load_valid_manifest(self, temp_manifest):
        """Should load valid manifest."""
        data = load_publish_manifest(temp_manifest)
        assert "publish" in data
        assert isinstance(data["publish"], list)
        assert len(data["publish"]) == 3

    def test_load_invalid_manifest_missing_publish(self, tmp_path):
        """Should exit on invalid manifest format."""
        invalid = tmp_path / "invalid.yml"
        invalid.write_text("foo: bar\n")

        with pytest.raises(SystemExit) as exc_info:
            load_publish_manifest(invalid)
        assert exc_info.value.code == 5

    def test_save_manifest_roundtrip(self, temp_manifest):
        """Should save and reload manifest correctly."""
        data = load_publish_manifest(temp_manifest)
        data["publish"][0]["build"] = True

        save_publish_manifest(temp_manifest, data)

        reloaded = load_publish_manifest(temp_manifest)
        assert reloaded["publish"][0]["build"] is True


class TestGitChangedFiles:
    """Tests for git diff analysis."""

    def test_git_diff_with_base(self, temp_repo):
        """Should get changed files between commits."""
        # Create second commit
        new_file = temp_repo / "new.md"
        new_file.write_text("New content\n")
        subprocess.run(
            ["git", "add", "."], cwd=temp_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Add new.md"],
            cwd=temp_repo,
            check=True,
            capture_output=True,
        )

        # Get commit SHAs
        result = subprocess.run(
            ["git", "log", "--format=%H", "-n", "2"],
            cwd=temp_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        commits = result.stdout.strip().split("\n")
        head, base = commits[0], commits[1]

        # Change to repo directory
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_repo)
            files = get_changed_files(head, base)
            assert "new.md" in files
        finally:
            os.chdir(original_cwd)

    def test_git_single_commit_fallback(self, temp_repo):
        """Should fallback to single commit analysis when base missing."""
        # Get HEAD sha
        result = subprocess.run(
            ["git", "log", "--format=%H", "-n", "1"],
            cwd=temp_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        head = result.stdout.strip()

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_repo)
            # Use non-existent base to trigger fallback
            files = get_changed_files(head, "nonexistent_base")
            # Should fallback to single commit analysis (HEAD is second commit)
            assert "docs/example.md" in files
        finally:
            os.chdir(original_cwd)


class TestSetPublishFlags:
    """Tests for set_publish_flags function."""

    @patch("tools.utils.smart_manage_publish_flags.git_get_changed_files")
    @patch("tools.utils.smart_manage_publish_flags.load_publish_targets")
    @patch("tools.utils.smart_manage_publish_flags.get_target_content_root")
    def test_set_flags_with_book_json(
        self, mock_get_content_root, mock_load_targets, mock_git_files, temp_manifest
    ):
        """Should set flags using book.json content_root."""
        # Mock git changes
        mock_git_files.return_value = ["content/chapter1.md"]

        # Mock target with book.json content_root
        mock_target = MagicMock()
        mock_target.book_config = MagicMock()
        mock_load_targets.return_value = [mock_target]
        mock_get_content_root.return_value = Path("content")

        # Run
        results = set_publish_flags(
            manifest_path=temp_manifest,
            commit="HEAD",
            dry_run=True,
        )

        # First entry (root with use_book_json) should match via content_root
        assert len(results["modified_entries"]) > 0
        assert results["any_build_true"] is True

    @patch("tools.utils.smart_manage_publish_flags.git_get_changed_files")
    @patch("tools.utils.smart_manage_publish_flags.load_publish_targets")
    def test_set_flags_without_book_json(
        self, mock_load_targets, mock_git_files, temp_manifest
    ):
        """Should set flags using entry path when no book.json."""
        mock_git_files.return_value = ["README.md"]
        mock_load_targets.return_value = []  # No targets

        results = set_publish_flags(
            manifest_path=temp_manifest,
            commit="HEAD",
            dry_run=True,
        )

        # README.md entry should match
        assert any(e["path"] == "README.md" for e in results["modified_entries"])

    @patch("tools.utils.smart_manage_publish_flags.git_get_changed_files")
    @patch("tools.utils.smart_manage_publish_flags.load_publish_targets")
    def test_set_flags_root_path_matches_all(
        self, mock_load_targets, mock_git_files, temp_manifest
    ):
        """Root path (.) should match all changed files."""
        mock_git_files.return_value = ["anywhere/file.md"]
        mock_load_targets.return_value = []

        results = set_publish_flags(
            manifest_path=temp_manifest,
            commit="HEAD",
            dry_run=True,
        )

        # Root entry (path=".") should match
        assert any(e["path"] == "." for e in results["modified_entries"])


class TestResetPublishFlags:
    """Tests for reset_publish_flags function."""

    def test_reset_by_path(self, temp_manifest):
        """Should reset flags by matching path."""
        # Set build=true first
        data = load_publish_manifest(temp_manifest)
        data["publish"][0]["build"] = True
        save_publish_manifest(temp_manifest, data)

        # Reset
        results = reset_publish_flags(
            manifest_path=temp_manifest,
            path=".",
            dry_run=True,
        )

        assert results["reset_count"] == 1
        assert 0 in results["matched_indices"]

    def test_reset_by_out(self, temp_manifest):
        """Should reset flags by matching output filename."""
        data = load_publish_manifest(temp_manifest)
        data["publish"][1]["build"] = True
        save_publish_manifest(temp_manifest, data)

        results = reset_publish_flags(
            manifest_path=temp_manifest,
            out="content.pdf",
            dry_run=True,
        )

        assert results["reset_count"] == 1
        assert "content/" in results["matched_paths"]

    def test_reset_by_index(self, temp_manifest):
        """Should reset flags by explicit index."""
        data = load_publish_manifest(temp_manifest)
        data["publish"][2]["build"] = True
        save_publish_manifest(temp_manifest, data)

        results = reset_publish_flags(
            manifest_path=temp_manifest,
            index=2,
            dry_run=True,
        )

        assert results["reset_count"] == 1
        assert 2 in results["matched_indices"]

    def test_reset_no_criteria_error(self, temp_manifest):
        """Should error if no criteria provided."""
        with pytest.raises(SystemExit) as exc_info:
            reset_publish_flags(manifest_path=temp_manifest)
        assert exc_info.value.code == 1

    def test_reset_multi_match_without_flag_error(self, temp_manifest):
        """Should error on multiple matches without --multi."""
        # Create two entries with same path
        data = load_publish_manifest(temp_manifest)
        data["publish"].append(
            {
                "path": ".",
                "out": "duplicate.pdf",
                "build": True,
            }
        )
        save_publish_manifest(temp_manifest, data)

        with pytest.raises(SystemExit) as exc_info:
            reset_publish_flags(
                manifest_path=temp_manifest,
                path=".",
                multi=False,
            )
        assert exc_info.value.code == 8

    def test_reset_no_match_with_error_flag(self, temp_manifest):
        """Should error on no match when error_on_no_match=True."""
        with pytest.raises(SystemExit) as exc_info:
            reset_publish_flags(
                manifest_path=temp_manifest,
                path="nonexistent",
                error_on_no_match=True,
            )
        assert exc_info.value.code == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
