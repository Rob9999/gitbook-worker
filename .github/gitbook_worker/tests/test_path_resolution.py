#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test path resolution for publish.yml, book.json, and content root.

These tests validate that the path resolution fixtures work correctly
and that the project structure can be discovered dynamically.
"""

import json
from pathlib import Path

import pytest

from .conftest import _find_book_json, _get_content_root
from tools.utils.smart_manifest import (
    SmartManifestConfigError,
    SmartManifestError,
    resolve_manifest,
)


def test_repo_root_fixture(repo_root):
    """Test that repo_root fixture finds the repository root."""
    assert repo_root.exists(), "Repository root should exist"
    assert repo_root.is_dir(), "Repository root should be a directory"
    # Check for typical repo markers
    assert (
        (repo_root / ".git").exists()
        or (repo_root / "publish.yml").exists()
        or (repo_root / "book.json").exists()
    ), "Repository root should contain .git, publish.yml, or book.json"


def test_publish_yml_path_fixture(publish_yml_path):
    """Test that publish_yml_path fixture finds publish.yml."""
    assert publish_yml_path.exists(), f"publish.yml not found at {publish_yml_path}"
    assert publish_yml_path.is_file(), "publish.yml should be a file"
    assert publish_yml_path.name in (
        "publish.yml",
        "publish.yaml",
    ), "File should be named publish.yml or publish.yaml"


def test_book_json_path_fixture(book_json_path):
    """Test that book_json_path fixture finds book.json."""
    assert book_json_path.exists(), f"book.json not found at {book_json_path}"
    assert book_json_path.is_file(), "book.json should be a file"
    assert book_json_path.name == "book.json", "File should be named book.json"


def test_book_json_data_fixture(book_json_data):
    """Test that book_json_data fixture loads valid JSON."""
    assert isinstance(book_json_data, dict), "book.json should contain a dictionary"
    # Check for expected fields
    assert "root" in book_json_data, "book.json should have a 'root' field"


def test_content_root_fixture(content_root, book_json_data):
    """Test that content_root fixture resolves to the correct directory."""
    assert content_root.exists(), f"Content root not found at {content_root}"
    assert content_root.is_dir(), "Content root should be a directory"

    # Verify it matches the book.json root value
    expected_root_name = book_json_data.get("root", ".").rstrip("/")
    assert (
        content_root.name == expected_root_name or expected_root_name == "."
    ), f"Content root directory name should match book.json root value ({expected_root_name})"


def test_content_root_contains_markdown_files(content_root):
    """Test that content_root contains markdown files."""
    md_files = list(content_root.rglob("*.md"))
    assert (
        len(md_files) > 0
    ), f"Content root should contain markdown files: {content_root}"


def test_publish_yml_path_resolution_order(tmp_path):
    """Test the resolution order defined in smart.yml."""

    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    work_dir = repo_root / "work"
    work_dir.mkdir()

    # 1. Explicit argument always wins
    explicit_dir = repo_root / "custom"
    explicit_dir.mkdir()
    explicit_manifest = explicit_dir / "publish.yml"
    explicit_manifest.write_text("version: 0.1.0")
    found = resolve_manifest(explicit=explicit_manifest, cwd=work_dir, repo_root=repo_root)
    assert found == explicit_manifest

    # 2. Local directory (work_dir) takes precedence if explicit not set
    local_manifest = work_dir / "publish.yaml"
    local_manifest.write_text("version: 0.1.0")
    found = resolve_manifest(explicit=None, cwd=work_dir, repo_root=repo_root)
    assert found == local_manifest

    # 3. Repo root is used when local directory lacks a manifest
    local_manifest.unlink()
    root_manifest = repo_root / "publish.yml"
    root_manifest.write_text("version: 0.1.0")
    found = resolve_manifest(explicit=None, cwd=work_dir, repo_root=repo_root)
    assert found == root_manifest

    # No manifest should raise a SmartManifestError
    root_manifest.unlink()
    with pytest.raises(SmartManifestError):
        resolve_manifest(explicit=None, cwd=work_dir, repo_root=repo_root)


def test_book_json_path_resolution_order(tmp_path):
    """Test the resolution order for book.json."""
    # Create test structure
    test_repo = tmp_path / "test_repo"
    test_repo.mkdir()

    # Test 1: book.json in root
    (test_repo / "book.json").write_text('{"root": "content/"}')
    found = _find_book_json(test_repo)
    assert found == test_repo / "book.json"

    # Test 2: Search in parent directories
    nested_dir = test_repo / "nested" / "deeply"
    nested_dir.mkdir(parents=True)
    found = _find_book_json(nested_dir)
    assert found == test_repo / "book.json"


def test_content_root_from_book_json(tmp_path):
    """Test that content root is correctly extracted from book.json."""
    test_repo = tmp_path / "test_repo"
    test_repo.mkdir()

    # Create book.json with custom root
    book_data = {"root": "my_content/", "title": "Test Book"}
    (test_repo / "book.json").write_text(json.dumps(book_data))

    # Create the content directory
    content_dir = test_repo / "my_content"
    content_dir.mkdir()

    book_json = _find_book_json(test_repo)
    content = _get_content_root(book_json)

    assert content == content_dir
    assert content.name == "my_content"


def test_content_root_defaults_to_repo_root(tmp_path):
    """Test that content root defaults to repo root when book.json has root='.'"""
    test_repo = tmp_path / "test_repo"
    test_repo.mkdir()

    # Create book.json with root as "."
    book_data = {"root": ".", "title": "Test Book"}
    (test_repo / "book.json").write_text(json.dumps(book_data))

    book_json = _find_book_json(test_repo)
    content = _get_content_root(book_json)

    assert content == test_repo


@pytest.mark.parametrize(
    "root_value,expected_suffix",
    [
        ("content/", "content"),
        ("content", "content"),
        ("docs/", "docs"),
        (".", ""),
        ("", ""),
    ],
)
def test_content_root_trailing_slash_handling(tmp_path, root_value, expected_suffix):
    """Test that content root handles trailing slashes correctly."""
    test_repo = tmp_path / "test_repo"
    test_repo.mkdir()

    # Create book.json
    book_data = {"root": root_value}
    (test_repo / "book.json").write_text(json.dumps(book_data))

    # Create the expected directory if needed
    if expected_suffix:
        (test_repo / expected_suffix).mkdir()

    book_json = _find_book_json(test_repo)
    content = _get_content_root(book_json)

    if expected_suffix:
        assert content.name == expected_suffix
        assert content.parent == test_repo
    else:
        assert content == test_repo


def test_smart_manifest_requires_semver(tmp_path):
    """smart.yml must provide a valid semantic version."""

    smart_cfg = tmp_path / "smart.yml"
    smart_cfg.write_text(
        """
version: invalid
filenames:
  - publish.yml
search: []
""",
        encoding="utf-8",
    )

    with pytest.raises(SmartManifestConfigError):
        resolve_manifest(
            explicit=None,
            cwd=tmp_path,
            repo_root=tmp_path,
            config_path=smart_cfg,
        )
