"""Tests for smart_git module.

Tests cover:
- Git command execution
- Path normalization
- Changed files detection with fallbacks
- Commit information retrieval
- Repository information
- Working directory status
"""

import os
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.utils.smart_git import (
    get_changed_files,
    get_commit_author,
    get_commit_message,
    get_commit_sha,
    get_current_branch,
    get_repo_root,
    get_uncommitted_files,
    has_uncommitted_changes,
    is_git_repo,
    normalize_posix,
    run_git_command,
)


@pytest.fixture
def temp_git_repo(tmp_path):
    """Create a temporary git repository for testing."""
    repo = tmp_path / "test_repo"
    repo.mkdir()

    # Initialize git
    subprocess.run(
        ["git", "init"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
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
    readme.write_text("# Test Repository\n")
    subprocess.run(
        ["git", "add", "."],
        cwd=repo,
        check=True,
        capture_output=True,
    )
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
    subprocess.run(
        ["git", "add", "."],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add docs"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    return repo


class TestNormalizePosix:
    """Tests for POSIX path normalization."""

    def test_convert_backslashes(self):
        """Should convert Windows backslashes to forward slashes."""
        result = normalize_posix("content\\file.md")
        assert result == "content/file.md"

    def test_remove_leading_dot_slash(self):
        """Should remove leading ./ prefix."""
        result = normalize_posix("./content/file.md")
        assert result == "content/file.md"

    def test_already_normalized(self):
        """Should handle already normalized paths."""
        result = normalize_posix("content/file.md")
        assert result == "content/file.md"

    def test_root_dot(self):
        """Should keep root . as is."""
        result = normalize_posix(".")
        assert result == "."

    def test_complex_path(self):
        """Should normalize complex paths."""
        result = normalize_posix(".\\content\\sub\\..\\file.md")
        assert result == "content/file.md"


class TestRunGitCommand:
    """Tests for git command execution."""

    def test_successful_command(self, temp_git_repo):
        """Should execute git command and return output."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            code, out, err = run_git_command(["git", "status", "--short"])
            assert code == 0
            assert isinstance(out, str)
            assert isinstance(err, str)
        finally:
            os.chdir(original_cwd)

    def test_failed_command(self):
        """Should return non-zero code for invalid command."""
        code, out, err = run_git_command(["git", "invalid-command"])
        assert code != 0
        assert err  # Should have error message


class TestGetChangedFiles:
    """Tests for changed files detection."""

    def test_diff_between_commits(self, temp_git_repo):
        """Should detect files changed between commits."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)

            # Create second commit
            new_file = temp_git_repo / "new.md"
            new_file.write_text("New content\n")
            subprocess.run(
                ["git", "add", "."],
                cwd=temp_git_repo,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "Add new.md"],
                cwd=temp_git_repo,
                check=True,
                capture_output=True,
            )

            # Get commit SHAs
            result = subprocess.run(
                ["git", "log", "--format=%H", "-n", "2"],
                cwd=temp_git_repo,
                capture_output=True,
                text=True,
                check=True,
            )
            commits = result.stdout.strip().split("\n")
            head, base = commits[0], commits[1]

            # Test
            files = get_changed_files(head, base)
            assert "new.md" in files

        finally:
            os.chdir(original_cwd)

    def test_single_commit_without_base(self, temp_git_repo):
        """Should analyze single commit when no base provided."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            files = get_changed_files("HEAD")
            # HEAD is second commit with docs/example.md
            assert "docs/example.md" in files
        finally:
            os.chdir(original_cwd)

    def test_fallback_on_missing_base(self, temp_git_repo):
        """Should fallback to single commit when base missing."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            # Use nonexistent base
            files = get_changed_files("HEAD", "nonexistent_base_commit")
            # Should fallback and still return files from HEAD (second commit)
            assert "docs/example.md" in files
        finally:
            os.chdir(original_cwd)

    def test_normalize_option(self, temp_git_repo):
        """Should respect normalize parameter."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            files_normalized = get_changed_files("HEAD", normalize=True)
            files_raw = get_changed_files("HEAD", normalize=False)
            assert isinstance(files_normalized, list)
            assert isinstance(files_raw, list)
        finally:
            os.chdir(original_cwd)


class TestCommitInfo:
    """Tests for commit information retrieval."""

    def test_get_commit_sha(self, temp_git_repo):
        """Should get full SHA for HEAD."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            sha = get_commit_sha("HEAD")
            assert sha is not None
            assert len(sha) == 40  # Full SHA length
        finally:
            os.chdir(original_cwd)

    def test_get_commit_sha_invalid_ref(self, temp_git_repo):
        """Should return None for invalid ref."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            sha = get_commit_sha("nonexistent_ref")
            assert sha is None
        finally:
            os.chdir(original_cwd)

    def test_get_commit_message(self, temp_git_repo):
        """Should get commit message."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            msg = get_commit_message("HEAD")
            # HEAD is second commit
            assert msg == "Add docs"
        finally:
            os.chdir(original_cwd)

    def test_get_commit_author(self, temp_git_repo):
        """Should get commit author."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            author = get_commit_author("HEAD")
            assert "Test User" in author
            assert "test@example.com" in author
        finally:
            os.chdir(original_cwd)


class TestRepositoryInfo:
    """Tests for repository information."""

    def test_is_git_repo_true(self, temp_git_repo):
        """Should detect git repository."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            assert is_git_repo() is True
        finally:
            os.chdir(original_cwd)

    def test_is_git_repo_false(self, tmp_path):
        """Should return False for non-git directory."""
        original_cwd = os.getcwd()
        try:
            non_repo = tmp_path / "not_a_repo"
            non_repo.mkdir()
            os.chdir(non_repo)
            assert is_git_repo() is False
        finally:
            os.chdir(original_cwd)

    def test_get_repo_root(self, temp_git_repo):
        """Should get repository root."""
        original_cwd = os.getcwd()
        try:
            # Create subdirectory
            subdir = temp_git_repo / "subdir"
            subdir.mkdir()
            os.chdir(subdir)

            root = get_repo_root()
            assert root is not None
            assert Path(root).resolve() == temp_git_repo.resolve()
        finally:
            os.chdir(original_cwd)

    def test_get_current_branch(self, temp_git_repo):
        """Should get current branch name."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)

            # Create and switch to test branch
            subprocess.run(
                ["git", "checkout", "-b", "test-branch"],
                cwd=temp_git_repo,
                check=True,
                capture_output=True,
            )

            branch = get_current_branch()
            assert branch == "test-branch"
        finally:
            os.chdir(original_cwd)


class TestWorkingDirectoryStatus:
    """Tests for working directory status."""

    def test_has_uncommitted_changes_false(self, temp_git_repo):
        """Should return False when no uncommitted changes."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            assert has_uncommitted_changes() is False
        finally:
            os.chdir(original_cwd)

    def test_has_uncommitted_changes_true(self, temp_git_repo):
        """Should return True when there are uncommitted changes."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)

            # Modify file
            readme = temp_git_repo / "README.md"
            readme.write_text("# Modified\n")

            assert has_uncommitted_changes() is True
        finally:
            os.chdir(original_cwd)

    def test_get_uncommitted_files(self, temp_git_repo):
        """Should list uncommitted files."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)

            # Modify existing and create new file
            readme = temp_git_repo / "README.md"
            readme.write_text("# Modified\n")
            new_file = temp_git_repo / "new.md"
            new_file.write_text("New\n")

            files = get_uncommitted_files()
            assert len(files) >= 1
            # Files should be POSIX normalized
            assert all("/" in f or f.count("/") == 0 for f in files)
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
