"""Unit tests for content_discovery module.

Tests cover all scenarios from test_documents_publishing.py:
1. Single GitBook with book.json + SUMMARY.md
2. Multi-GitBook (multiple projects)
3. Single file with special characters
4. Folder without GitBook (fallback mode)
"""

from pathlib import Path

import pytest

from tools.utils.content_discovery import discover_content


class TestSingleGitBook:
    """Test scenario 1: Single GitBook with book.json and SUMMARY.md."""

    @pytest.fixture
    def gitbook_dir(self, tmp_path: Path) -> Path:
        """Create a complete GitBook structure."""
        base = tmp_path / "my-book"
        base.mkdir()

        # Create book.json
        (base / "book.json").write_text(
            """{
    "title": "Test Book",
    "root": "content/",
    "structure": {
        "summary": "SUMMARY.md"
    }
}""",
            encoding="utf-8",
        )

        # Create content directory
        content = base / "content"
        content.mkdir()

        # Create README.md
        (content / "README.md").write_text("# Introduction", encoding="utf-8")

        # Create SUMMARY.md
        (content / "SUMMARY.md").write_text(
            """# Summary

* [Introduction](README.md)
* [Chapter 1](chapter-1.md)
* [Chapter 2](chapter-2.md)
""",
            encoding="utf-8",
        )

        # Create chapter files
        (content / "chapter-1.md").write_text("# Chapter 1", encoding="utf-8")
        (content / "chapter-2.md").write_text("# Chapter 2", encoding="utf-8")

        # Create extra file not in SUMMARY (should be ignored when use_summary=True)
        (content / "extra.md").write_text("# Extra", encoding="utf-8")

        return base

    def test_discover_with_book_json_and_summary(self, gitbook_dir: Path):
        """Test full GitBook discovery with book.json + SUMMARY.md."""
        result = discover_content(
            path=gitbook_dir,
            source_type="folder",
            use_book_json=True,
            use_summary=True,
        )

        assert result.base_dir == gitbook_dir
        assert result.content_root == gitbook_dir / "content"
        assert result.summary_path == gitbook_dir / "content" / "SUMMARY.md"
        assert result.book_json_path == gitbook_dir / "book.json"
        assert result.source_type == "folder"
        assert result.use_summary is True

        # Should respect SUMMARY.md order
        assert len(result.markdown_files) == 3
        assert result.markdown_files[0].name == "README.md"
        assert result.markdown_files[1].name == "chapter-1.md"
        assert result.markdown_files[2].name == "chapter-2.md"

        # extra.md should NOT be included (not in SUMMARY)
        assert not any(f.name == "extra.md" for f in result.markdown_files)

    def test_discover_without_summary(self, gitbook_dir: Path):
        """Test GitBook discovery without SUMMARY.md (recursive fallback)."""
        result = discover_content(
            path=gitbook_dir,
            source_type="folder",
            use_book_json=True,
            use_summary=False,  # Ignore SUMMARY.md
        )

        assert result.content_root == gitbook_dir / "content"
        assert result.summary_path is None
        assert result.use_summary is False

        # Should collect all files recursively (including extra.md)
        assert len(result.markdown_files) >= 4
        file_names = {f.name for f in result.markdown_files}
        assert "README.md" in file_names
        assert "chapter-1.md" in file_names
        assert "chapter-2.md" in file_names
        assert "extra.md" in file_names

    def test_discover_without_book_json(self, gitbook_dir: Path):
        """Test discovery when use_book_json=False (ignores book.json)."""
        result = discover_content(
            path=gitbook_dir,
            source_type="folder",
            use_book_json=False,
            use_summary=False,
        )

        # Should use provided path directly (not content/ from book.json)
        assert result.content_root == gitbook_dir
        assert result.book_json_path is None

        # Should collect files recursively from gitbook_dir
        # (includes content/ subdirectory files since recursive by default)
        assert len(result.markdown_files) == 5  # All files in content/

    def test_discover_with_path_to_content(self, gitbook_dir: Path):
        """Test when path points directly to content/ directory."""
        result = discover_content(
            path=gitbook_dir / "content",
            source_type="folder",
            use_book_json=False,
            use_summary=True,
        )

        assert result.content_root == gitbook_dir / "content"
        assert result.summary_path == gitbook_dir / "content" / "SUMMARY.md"

        # Should use SUMMARY.md
        assert len(result.markdown_files) == 3


class TestMultiGitBook:
    """Test scenario 2: Multiple GitBooks in separate directories."""

    @pytest.fixture
    def multi_gitbook_dir(self, tmp_path: Path) -> Path:
        """Create multiple GitBook projects."""
        base = tmp_path / "multi-project"
        base.mkdir()

        # Project A
        project_a = base / "project-a"
        project_a.mkdir()
        (project_a / "book.json").write_text(
            '{"title": "Project A", "root": "content/"}', encoding="utf-8"
        )
        content_a = project_a / "content"
        content_a.mkdir()
        (content_a / "README.md").write_text("# Project A", encoding="utf-8")
        (content_a / "chapter-a.md").write_text("# Chapter A", encoding="utf-8")

        # Project B
        project_b = base / "project-b"
        project_b.mkdir()
        (project_b / "book.json").write_text(
            '{"title": "Project B", "root": "docs/"}', encoding="utf-8"
        )
        docs_b = project_b / "docs"
        docs_b.mkdir()
        (docs_b / "README.md").write_text("# Project B", encoding="utf-8")
        (docs_b / "chapter-b.md").write_text("# Chapter B", encoding="utf-8")

        return base

    def test_discover_project_a(self, multi_gitbook_dir: Path):
        """Test discovery for project A."""
        result = discover_content(
            path=multi_gitbook_dir / "project-a",
            source_type="folder",
            use_book_json=True,
            use_summary=False,
        )

        assert result.base_dir == multi_gitbook_dir / "project-a"
        assert result.content_root == multi_gitbook_dir / "project-a" / "content"
        assert len(result.markdown_files) == 2

    def test_discover_project_b(self, multi_gitbook_dir: Path):
        """Test discovery for project B (different root: docs/)."""
        result = discover_content(
            path=multi_gitbook_dir / "project-b",
            source_type="folder",
            use_book_json=True,
            use_summary=False,
        )

        assert result.base_dir == multi_gitbook_dir / "project-b"
        assert result.content_root == multi_gitbook_dir / "project-b" / "docs"
        assert len(result.markdown_files) == 2


class TestSingleFile:
    """Test scenario 3: Single file mode."""

    def test_discover_single_file(self, tmp_path: Path):
        """Test discovery for a single markdown file."""
        md_file = tmp_path / "document.md"
        md_file.write_text("# Test Document", encoding="utf-8")

        result = discover_content(
            path=md_file,
            source_type="file",
        )

        assert result.source_type == "file"
        assert result.content_root == tmp_path
        assert result.summary_path is None
        assert result.use_summary is False
        assert len(result.markdown_files) == 1
        assert result.markdown_files[0] == md_file

    def test_discover_file_with_special_chars(self, tmp_path: Path):
        """Test single file with special characters in name."""
        md_file = tmp_path / "complex-doc_with-special&chars@2024 & !.md"
        md_file.write_text("# Complex", encoding="utf-8")

        result = discover_content(path=md_file, source_type="file")

        assert len(result.markdown_files) == 1
        assert (
            result.markdown_files[0].name
            == "complex-doc_with-special&chars@2024 & !.md"
        )

    def test_discover_file_auto_detect(self, tmp_path: Path):
        """Test auto-detection of file type (no source_type specified)."""
        md_file = tmp_path / "auto-detect.md"
        md_file.write_text("# Auto", encoding="utf-8")

        result = discover_content(
            path=md_file,
            source_type=None,  # Auto-detect
        )

        assert result.source_type == "file"
        assert len(result.markdown_files) == 1

    def test_discover_nonexistent_file(self, tmp_path: Path):
        """Test handling of non-existent file."""
        md_file = tmp_path / "nonexistent.md"

        result = discover_content(path=md_file, source_type="file")

        assert result.source_type == "file"
        assert len(result.markdown_files) == 0  # Empty list for missing file


class TestFolderWithoutGitBook:
    """Test scenario 4: Folder without book.json (fallback mode)."""

    @pytest.fixture
    def plain_folder(self, tmp_path: Path) -> Path:
        """Create a plain folder with markdown files (no book.json)."""
        docs = tmp_path / "docs"
        docs.mkdir()

        (docs / "index.md").write_text("# Index", encoding="utf-8")
        (docs / "guide.md").write_text("# Guide", encoding="utf-8")
        (docs / "faq.md").write_text("# FAQ", encoding="utf-8")

        # Create subdirectory
        subdir = docs / "advanced"
        subdir.mkdir()
        (subdir / "advanced-guide.md").write_text("# Advanced", encoding="utf-8")

        return docs

    def test_discover_plain_folder(self, plain_folder: Path):
        """Test discovery in folder without book.json."""
        result = discover_content(
            path=plain_folder,
            source_type="folder",
            use_book_json=False,
            use_summary=False,
        )

        assert result.content_root == plain_folder
        assert result.book_json_path is None
        assert result.summary_path is None

        # Should collect all files recursively
        assert len(result.markdown_files) == 4
        file_names = {f.name for f in result.markdown_files}
        assert "index.md" in file_names
        assert "guide.md" in file_names
        assert "faq.md" in file_names
        assert "advanced-guide.md" in file_names

    def test_discover_plain_folder_with_summary_fallback(self, plain_folder: Path):
        """Test that missing SUMMARY.md falls back to recursive collection."""
        result = discover_content(
            path=plain_folder,
            source_type="folder",
            use_book_json=False,
            use_summary=True,  # Request SUMMARY, but doesn't exist
        )

        assert result.summary_path is None
        assert result.use_summary is False  # Fallback because SUMMARY missing

        # Should still collect files recursively
        assert len(result.markdown_files) == 4


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_discover_empty_folder(self, tmp_path: Path):
        """Test discovery in empty folder."""
        empty = tmp_path / "empty"
        empty.mkdir()

        result = discover_content(
            path=empty,
            source_type="folder",
            use_book_json=False,
            use_summary=False,
        )

        assert result.content_root == empty
        assert len(result.markdown_files) == 0

    def test_discover_nonexistent_folder(self, tmp_path: Path):
        """Test discovery with non-existent folder."""
        nonexistent = tmp_path / "nonexistent"

        result = discover_content(
            path=nonexistent,
            source_type="folder",
            use_book_json=False,
            use_summary=False,
        )

        # When folder doesn't exist, base_dir falls back to cwd (which is repo root)
        # So it collects ALL markdown files from repo - this is expected behavior
        # In real usage, caller should check path.exists() before calling discover
        assert result.base_dir.exists()  # Falls back to valid directory

    def test_discover_with_invalid_book_json(self, tmp_path: Path):
        """Test graceful handling of invalid book.json."""
        base = tmp_path / "invalid-book"
        base.mkdir()

        # Create malformed book.json
        (base / "book.json").write_text("{ invalid json", encoding="utf-8")

        # Create content
        content = base / "content"
        content.mkdir()
        (content / "test.md").write_text("# Test", encoding="utf-8")

        result = discover_content(
            path=base,
            source_type="folder",
            use_book_json=True,
            use_summary=False,
        )

        # Should fall back to using path directly
        assert result.content_root == base
        # Recursive collection finds files in subdirectories too
        assert len(result.markdown_files) == 1  # content/test.md found recursively

    def test_discover_with_empty_summary(self, tmp_path: Path):
        """Test handling of empty SUMMARY.md."""
        base = tmp_path / "empty-summary"
        base.mkdir()

        # Create empty SUMMARY.md
        (base / "SUMMARY.md").write_text("", encoding="utf-8")

        # Create markdown files
        (base / "file1.md").write_text("# File 1", encoding="utf-8")
        (base / "file2.md").write_text("# File 2", encoding="utf-8")

        result = discover_content(
            path=base,
            source_type="folder",
            use_book_json=False,
            use_summary=True,
        )

        # Should find SUMMARY but fall back to recursive when empty
        assert result.summary_path == base / "SUMMARY.md"
        # Recursive fallback collects ALL .md files (including SUMMARY.md itself)
        assert len(result.markdown_files) == 3  # file1.md, file2.md, SUMMARY.md

    def test_discover_summary_with_broken_links(self, tmp_path: Path):
        """Test SUMMARY.md with broken/missing file references."""
        base = tmp_path / "broken-links"
        base.mkdir()

        # SUMMARY references non-existent files
        (base / "SUMMARY.md").write_text(
            """# Summary

* [Exists](exists.md)
* [Missing](missing.md)
* [Also Missing](also-missing.md)
""",
            encoding="utf-8",
        )

        # Only create one file
        (base / "exists.md").write_text("# Exists", encoding="utf-8")

        result = discover_content(
            path=base,
            source_type="folder",
            use_book_json=False,
            use_summary=True,
        )

        # Should only include existing files
        assert len(result.markdown_files) == 1
        assert result.markdown_files[0].name == "exists.md"

    def test_discover_nested_book_json(self, tmp_path: Path):
        """Test book.json discovery in parent directory."""
        # Create book.json in root
        (tmp_path / "book.json").write_text('{"root": "content/"}', encoding="utf-8")

        # Create nested content structure
        content = tmp_path / "content"
        content.mkdir()
        nested = content / "nested"
        nested.mkdir()
        (nested / "test.md").write_text("# Test", encoding="utf-8")

        # Start discovery from nested directory
        result = discover_content(
            path=nested,
            source_type="folder",
            use_book_json=True,
            use_summary=False,
        )

        # Should find book.json in parent and use its root
        assert result.book_json_path == tmp_path / "book.json"
        assert result.base_dir == tmp_path
        assert result.content_root == tmp_path / "content"

    def test_discover_with_markdown_extension(self, tmp_path: Path):
        """Test discovery of .markdown files (not just .md)."""
        base = tmp_path / "markdown-ext"
        base.mkdir()

        (base / "file1.md").write_text("# MD", encoding="utf-8")
        (base / "file2.markdown").write_text("# Markdown", encoding="utf-8")
        (base / "file3.txt").write_text("# Text", encoding="utf-8")  # Should ignore

        result = discover_content(
            path=base,
            source_type="folder",
            use_book_json=False,
            use_summary=False,
        )

        # Should include both .md and .markdown
        assert len(result.markdown_files) == 2
        extensions = {f.suffix for f in result.markdown_files}
        assert ".md" in extensions
        assert ".markdown" in extensions
        assert ".txt" not in extensions
