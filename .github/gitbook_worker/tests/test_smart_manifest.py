"""Tests for smart_manifest module.

Tests cover:
- Manifest resolution with search strategies
- CLI → cwd → repo_root → custom fallback
- detect_repo_root() with .git, book.json, publish.yml
- Config loading from smart.yml
- SmartManifestError handling
- Edge cases (missing files, invalid configs, etc.)
"""

from pathlib import Path

import pytest
import yaml

from tools.utils.smart_manifest import (
    SmartManifestConfig,
    SmartManifestConfigError,
    SmartManifestError,
    _load_config,
    detect_repo_root,
    resolve_manifest,
)


@pytest.fixture
def temp_repo(tmp_path):
    """Create temporary repository structure."""
    # Create .git directory
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    # Create nested directories
    subdir = tmp_path / "project" / "docs"
    subdir.mkdir(parents=True)

    return tmp_path


@pytest.fixture
def temp_manifest(tmp_path):
    """Create temporary manifest file."""
    manifest = tmp_path / "publish.yml"
    manifest.write_text(yaml.safe_dump({"publish": []}))
    return manifest


@pytest.fixture
def temp_config(tmp_path):
    """Create temporary smart.yml config."""
    config = tmp_path / "smart.yml"
    data = {
        "version": "1.0.0",
        "filenames": ["publish.yml", "publish.yaml"],
        "search": [
            {"type": "cli"},
            {"type": "cwd"},
            {"type": "repo_root"},
        ],
    }
    config.write_text(yaml.safe_dump(data))
    return config


class TestDetectRepoRoot:
    """Tests for detect_repo_root function."""

    def test_detect_with_git_dir(self, temp_repo):
        """Should detect repo root from .git directory."""
        subdir = temp_repo / "project" / "docs"

        root = detect_repo_root(subdir)

        assert root == temp_repo

    def test_detect_with_book_json(self, tmp_path):
        """Should detect repo root from book.json."""
        # Create book.json
        (tmp_path / "book.json").write_text("{}")
        subdir = tmp_path / "project"
        subdir.mkdir()

        root = detect_repo_root(subdir)

        assert root == tmp_path

    def test_detect_with_publish_yml(self, tmp_path):
        """Should detect repo root from publish.yml."""
        # Create publish.yml
        (tmp_path / "publish.yml").write_text("publish: []")
        subdir = tmp_path / "project"
        subdir.mkdir()

        root = detect_repo_root(subdir)

        assert root == tmp_path

    def test_detect_fallback_to_start(self, tmp_path):
        """Should fallback to start directory if no markers found."""
        # No .git, book.json, or publish.yml
        subdir = tmp_path / "project"
        subdir.mkdir()

        root = detect_repo_root(subdir)

        # Should return the deepest directory
        assert root == subdir

    def test_detect_from_cwd(self, temp_repo, monkeypatch):
        """Should use cwd when start not provided."""
        # temp_repo already has project/docs structure
        subdir = temp_repo / "project" / "docs"
        monkeypatch.chdir(subdir)

        root = detect_repo_root()

        assert root == temp_repo


class TestResolveManifest:
    """Tests for resolve_manifest function."""

    def test_resolve_explicit_path(self, temp_manifest):
        """Should use explicit path when provided."""
        result = resolve_manifest(explicit=temp_manifest, cwd=temp_manifest.parent)

        assert result == temp_manifest.resolve()

    def test_resolve_explicit_string(self, temp_manifest):
        """Should accept explicit path as string."""
        result = resolve_manifest(explicit=str(temp_manifest), cwd=temp_manifest.parent)

        assert result == temp_manifest.resolve()

    def test_resolve_from_cwd(self, temp_manifest):
        """Should find manifest in cwd."""
        result = resolve_manifest(
            explicit=None, cwd=temp_manifest.parent, repo_root=temp_manifest.parent
        )

        assert result == temp_manifest.resolve()

    def test_resolve_from_repo_root(self, temp_repo):
        """Should find manifest in repo root."""
        manifest = temp_repo / "publish.yml"
        manifest.write_text(yaml.safe_dump({"publish": []}))

        # temp_repo already has project/docs structure
        subdir = temp_repo / "project" / "docs"

        result = resolve_manifest(explicit=None, cwd=subdir, repo_root=temp_repo)

        assert result == manifest.resolve()

    def test_resolve_search_order(self, temp_repo):
        """Should follow CLI → cwd → repo_root order."""
        # Create manifest in repo root
        root_manifest = temp_repo / "publish.yml"
        root_manifest.write_text(yaml.safe_dump({"publish": []}))

        # Create manifest in subdir (cwd) - use existing structure
        subdir = temp_repo / "project" / "docs"
        cwd_manifest = subdir / "publish.yml"
        cwd_manifest.write_text(yaml.safe_dump({"publish": []}))

        # Should prefer cwd over repo_root
        result = resolve_manifest(explicit=None, cwd=subdir, repo_root=temp_repo)

        assert result == cwd_manifest.resolve()

    def test_resolve_nonexistent(self, tmp_path):
        """Should raise SmartManifestError when not found."""
        with pytest.raises(SmartManifestError):
            resolve_manifest(explicit=None, cwd=tmp_path, repo_root=tmp_path)

    def test_resolve_with_custom_config(self, temp_repo, temp_config):
        """Should use custom config path."""
        manifest = temp_repo / "publish.yml"
        manifest.write_text(yaml.safe_dump({"publish": []}))

        result = resolve_manifest(
            explicit=None,
            cwd=temp_repo,
            repo_root=temp_repo,
            config_path=temp_config,
        )

        assert result == manifest.resolve()


class TestLoadConfig:
    """Tests for config loading."""

    def test_load_default_config(self):
        """Should return default config when no file exists."""
        config = _load_config(Path("nonexistent.yml"))

        assert config.version == "1.0.0"
        assert "publish.yml" in config.filenames
        assert len(config.search) >= 3

    def test_load_custom_config(self, temp_config):
        """Should load custom config from file."""
        config = _load_config(temp_config)

        assert config.version == "1.0.0"
        assert config.filenames == ("publish.yml", "publish.yaml")
        assert len(config.search) == 3

    def test_load_config_with_custom_filenames(self, tmp_path):
        """Should support custom filename list."""
        config_path = tmp_path / "smart.yml"
        data = {
            "version": "1.0.0",
            "filenames": ["custom.yml", "manifest.yml"],
            "search": [{"type": "cwd"}],
        }
        config_path.write_text(yaml.safe_dump(data))

        config = _load_config(config_path)

        assert config.filenames == ("custom.yml", "manifest.yml")

    def test_load_config_with_directory_search(self, tmp_path):
        """Should support directory search rules."""
        config_path = tmp_path / "smart.yml"
        data = {
            "version": "1.0.0",
            "filenames": ["publish.yml"],
            "search": [
                {"type": "directory", "directory": "{repo_root}/config"},
            ],
        }
        config_path.write_text(yaml.safe_dump(data))

        config = _load_config(config_path)

        assert len(config.search) == 1
        assert config.search[0].kind == "directory"
        assert config.search[0].directory == "{repo_root}/config"

    def test_load_config_invalid_version(self, tmp_path):
        """Should handle invalid version."""
        config_path = tmp_path / "smart.yml"
        data = {
            "version": "invalid-version",
            "filenames": ["publish.yml"],
            "search": [{"type": "cwd"}],
        }
        config_path.write_text(yaml.safe_dump(data))

        with pytest.raises(SmartManifestConfigError):
            _load_config(config_path)


class TestSmartManifestConfig:
    """Tests for SmartManifestConfig dataclass."""

    def test_create_config(self):
        """Should create config with all fields."""
        from tools.utils.smart_manifest import _SearchRule

        config = SmartManifestConfig(
            version="1.0.0",
            filenames=("publish.yml",),
            search=(_SearchRule("cwd"),),
        )

        assert config.version == "1.0.0"
        assert config.filenames == ("publish.yml",)
        assert len(config.search) == 1

    def test_config_immutable(self):
        """Should be immutable (frozen)."""
        from tools.utils.smart_manifest import _SearchRule

        config = SmartManifestConfig(
            version="1.0.0",
            filenames=("publish.yml",),
            search=(_SearchRule("cwd"),),
        )

        with pytest.raises(AttributeError):
            config.version = "2.0.0"


class TestSearchRules:
    """Tests for search rule configurations."""

    def test_cli_rule(self, temp_manifest):
        """Should prioritize explicit CLI path."""
        result = resolve_manifest(explicit=temp_manifest, cwd=temp_manifest.parent)

        assert result == temp_manifest.resolve()

    def test_cwd_rule(self, temp_manifest):
        """Should search in cwd."""
        result = resolve_manifest(
            explicit=None,
            cwd=temp_manifest.parent,
            repo_root=temp_manifest.parent,
        )

        assert result == temp_manifest.resolve()

    def test_repo_root_rule(self, temp_repo):
        """Should search in repo root."""
        manifest = temp_repo / "publish.yml"
        manifest.write_text(yaml.safe_dump({"publish": []}))

        # temp_repo already has project/docs structure
        subdir = temp_repo / "project" / "docs"

        result = resolve_manifest(explicit=None, cwd=subdir, repo_root=temp_repo)

        assert result == manifest.resolve()


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_config(self, tmp_path):
        """Should handle empty config file."""
        config_path = tmp_path / "smart.yml"
        config_path.write_text("")

        config = _load_config(config_path)

        # Should use defaults
        assert config.version == "1.0.0"
        assert len(config.filenames) > 0

    def test_nonexistent_explicit_path(self, tmp_path):
        """Should raise FileNotFoundError for explicit path."""
        nonexistent = tmp_path / "nonexistent.yml"

        with pytest.raises(SmartManifestError):
            resolve_manifest(explicit=nonexistent, cwd=tmp_path, repo_root=tmp_path)

    def test_resolve_with_yaml_extension(self, tmp_path):
        """Should find .yaml extension."""
        manifest = tmp_path / "publish.yaml"
        manifest.write_text(yaml.safe_dump({"publish": []}))

        result = resolve_manifest(explicit=None, cwd=tmp_path, repo_root=tmp_path)

        assert result == manifest.resolve()

    def test_resolve_prefer_yml_over_yaml(self, tmp_path):
        """Should prefer .yml over .yaml when both exist."""
        yml_manifest = tmp_path / "publish.yml"
        yml_manifest.write_text(yaml.safe_dump({"publish": ["yml"]}))

        yaml_manifest = tmp_path / "publish.yaml"
        yaml_manifest.write_text(yaml.safe_dump({"publish": ["yaml"]}))

        result = resolve_manifest(explicit=None, cwd=tmp_path, repo_root=tmp_path)

        # Should prefer .yml (first in default filenames)
        assert result == yml_manifest.resolve()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
