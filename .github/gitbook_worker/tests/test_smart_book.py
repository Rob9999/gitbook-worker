"""Tests for smart_book module.

Tests cover:
- Book.json discovery with parent search
- Content root resolution
- Summary path resolution
- Invalid/missing book.json handling
- Edge cases (empty files, malformed JSON, etc.)
"""

import json
from pathlib import Path

import pytest

from tools.utils.smart_book import (
    BookConfig,
    discover_book,
    get_content_root,
    has_book_json,
)


@pytest.fixture
def temp_gitbook_project(tmp_path):
    """Create a temporary GitBook project structure."""
    project = tmp_path / "project"
    project.mkdir()

    # Create book.json
    book_json = project / "book.json"
    book_json.write_text(
        json.dumps(
            {
                "root": "./content",
                "structure": {"summary": "SUMMARY.md", "readme": "README.md"},
                "title": "Test Book",
                "language": "de",
            }
        )
    )

    # Create content directory
    content = project / "content"
    content.mkdir()

    # Create SUMMARY.md
    summary = content / "SUMMARY.md"
    summary.write_text("# Summary\n\n* [Chapter 1](chapter1.md)\n")

    return project


@pytest.fixture
def temp_nested_project(tmp_path):
    """Create nested project with book.json in parent."""
    project = tmp_path / "project"
    project.mkdir()

    # book.json in root
    book_json = project / "book.json"
    book_json.write_text(json.dumps({"root": "./docs"}))

    # Nested subdirectory
    subdir = project / "docs" / "subdir"
    subdir.mkdir(parents=True)

    return project, subdir


class TestDiscoverBook:
    """Tests for discover_book function."""

    def test_discover_with_book_json(self, temp_gitbook_project):
        """Should discover book.json and extract all fields."""
        result = discover_book(temp_gitbook_project)

        assert isinstance(result, BookConfig)
        assert result.book_json_path == temp_gitbook_project / "book.json"
        assert result.base_dir == temp_gitbook_project
        assert result.content_root == temp_gitbook_project / "content"
        assert result.summary_filename == "SUMMARY.md"
        assert result.summary_path == temp_gitbook_project / "content" / "SUMMARY.md"
        assert result.title == "Test Book"
        assert result.language == "de"

    def test_discover_with_parent_search(self, temp_nested_project):
        """Should search parent directories for book.json."""
        project, subdir = temp_nested_project

        result = discover_book(subdir, search_parents=True)

        assert result.book_json_path == project / "book.json"
        assert result.content_root == project / "docs"

    def test_discover_without_parent_search(self, temp_nested_project):
        """Should not search parents when search_parents=False."""
        project, subdir = temp_nested_project

        result = discover_book(subdir, search_parents=False)

        # Should not find book.json, use subdir as content_root
        assert result.book_json_path is None
        assert result.content_root == subdir

    def test_discover_no_book_json(self, tmp_path):
        """Should handle missing book.json gracefully."""
        plain_dir = tmp_path / "plain"
        plain_dir.mkdir()

        result = discover_book(plain_dir)

        assert result.book_json_path is None
        assert result.base_dir == plain_dir
        assert result.content_root == plain_dir
        assert result.summary_filename is None
        assert result.title is None

    def test_discover_invalid_json(self, tmp_path):
        """Should handle invalid JSON gracefully."""
        project = tmp_path / "project"
        project.mkdir()

        # Create invalid book.json
        book_json = project / "book.json"
        book_json.write_text("{ invalid json }")

        result = discover_book(project)

        # Should still find book.json but with empty data (graceful fallback)
        assert result.book_json_path == book_json
        assert result.content_root == project  # No root in empty data

    def test_discover_with_relative_root(self, tmp_path):
        """Should resolve relative root path correctly."""
        project = tmp_path / "project"
        project.mkdir()

        book_json = project / "book.json"
        book_json.write_text(json.dumps({"root": "../other"}))

        result = discover_book(project)

        # Should resolve relative path
        assert result.content_root == (project / ".." / "other").resolve()

    def test_discover_with_absolute_root(self, tmp_path):
        """Should handle absolute root path."""
        project = tmp_path / "project"
        project.mkdir()

        abs_root = tmp_path / "absolute_content"
        abs_root.mkdir()

        book_json = project / "book.json"
        book_json.write_text(json.dumps({"root": str(abs_root)}))

        result = discover_book(project)

        assert result.content_root == abs_root

    def test_discover_empty_book_json(self, tmp_path):
        """Should handle empty book.json."""
        project = tmp_path / "project"
        project.mkdir()

        book_json = project / "book.json"
        book_json.write_text("{}")

        result = discover_book(project)

        # Should use defaults
        assert result.book_json_path == book_json
        assert result.content_root == project  # No root specified
        assert result.summary_filename is None

    def test_discover_with_structure_only(self, tmp_path):
        """Should extract structure.summary."""
        project = tmp_path / "project"
        project.mkdir()

        # Create the TOC.md file so it can be found
        toc = project / "TOC.md"
        toc.write_text("# Table of Contents")

        book_json = project / "book.json"
        book_json.write_text(json.dumps({"structure": {"summary": "TOC.md"}}))

        result = discover_book(project)

        assert result.summary_filename == "TOC.md"
        assert result.summary_path == toc


class TestGetContentRoot:
    """Tests for get_content_root convenience function."""

    def test_get_content_root_with_book_json(self, temp_gitbook_project):
        """Should return content root from book.json."""
        root = get_content_root(temp_gitbook_project)
        assert root == temp_gitbook_project / "content"

    def test_get_content_root_without_book_json(self, tmp_path):
        """Should return path itself when no book.json."""
        plain_dir = tmp_path / "plain"
        plain_dir.mkdir()

        root = get_content_root(plain_dir)
        assert root == plain_dir

    def test_get_content_root_with_parent_search(self, temp_nested_project):
        """Should search parents for book.json."""
        project, subdir = temp_nested_project

        root = get_content_root(subdir)
        assert root == project / "docs"


class TestHasBookJson:
    """Tests for has_book_json check function."""

    def test_has_book_json_true(self, temp_gitbook_project):
        """Should return True when book.json exists."""
        assert has_book_json(temp_gitbook_project) is True

    def test_has_book_json_false(self, tmp_path):
        """Should return False when no book.json."""
        plain_dir = tmp_path / "plain"
        plain_dir.mkdir()

        assert has_book_json(plain_dir) is False

    def test_has_book_json_with_parent_search(self, temp_nested_project):
        """Should check directory for book.json."""
        project, subdir = temp_nested_project

        # has_book_json() only checks the exact directory
        assert has_book_json(project) is True
        assert has_book_json(subdir) is False

    def test_has_book_json_no_parent_search(self, temp_nested_project):
        """Should work with explicit book.json path."""
        project, subdir = temp_nested_project

        book_json = project / "book.json"
        assert has_book_json(book_json) is True


class TestBookConfig:
    """Tests for BookConfig dataclass."""

    def test_book_config_immutable(self, temp_gitbook_project):
        """Should be immutable (frozen dataclass)."""
        config = discover_book(temp_gitbook_project)

        with pytest.raises(AttributeError):
            config.title = "New Title"

    def test_book_config_repr(self, temp_gitbook_project):
        """Should have readable repr."""
        config = discover_book(temp_gitbook_project)
        repr_str = repr(config)

        assert "BookConfig" in repr_str
        assert "Test Book" in repr_str


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_discover_with_nonexistent_path(self, tmp_path):
        """Should handle nonexistent path gracefully."""
        nonexistent = tmp_path / "nonexistent"

        result = discover_book(nonexistent)

        # Should fall back to parent directory (tmp_path)
        assert result.content_root == tmp_path

    def test_discover_with_file_path(self, tmp_path):
        """Should handle file path (not directory)."""
        file_path = tmp_path / "file.md"
        file_path.write_text("content")

        result = discover_book(file_path)

        # Should fall back to parent directory (tmp_path)
        assert result.content_root == tmp_path

    def test_discover_deeply_nested(self, tmp_path):
        """Should search deeply nested directories."""
        # Create deep structure
        deep = tmp_path / "a" / "b" / "c" / "d" / "e"
        deep.mkdir(parents=True)

        # book.json at root
        book_json = tmp_path / "book.json"
        book_json.write_text(json.dumps({"root": "./content"}))

        result = discover_book(deep, search_parents=True)

        # Should find book.json at root
        assert result.book_json_path == book_json

    def test_discover_with_symlink(self, tmp_path):
        """Should handle symlinks correctly."""
        # Create actual directory
        actual = tmp_path / "actual"
        actual.mkdir()

        book_json = actual / "book.json"
        book_json.write_text(json.dumps({"root": "./content"}))

        # Create symlink
        link = tmp_path / "link"
        try:
            link.symlink_to(actual)

            result = discover_book(link)

            # Should resolve symlink
            assert result.book_json_path is not None
            assert result.content_root == actual / "content"
        except OSError:
            # Skip test if symlinks not supported (Windows without admin)
            pytest.skip("Symlinks not supported on this system")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
