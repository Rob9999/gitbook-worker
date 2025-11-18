"""Configuration loader for automatic README generation.

This module provides configuration management for the automatic README.md
generation feature in the workflow orchestrator. It uses the same smart
matching pattern system as other gitbook_worker configurations.

Configuration hierarchy (highest to lowest priority):
1. publish.yml (readme: section)
2. Local readme.yml (project root)
3. Default readme.yml (.github/gitbook_worker/defaults/)

Example configuration in publish.yml:
    readme:
      enabled: true
      patterns:
        exclude:
          - "special-dir/**"
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from tools.logging_config import get_logger
from tools.utils.smart_manifest import detect_repo_root

LOGGER = get_logger(__name__)

DEFAULT_README_CONFIG = (
    Path(__file__).resolve().parent.parent.parent / "defaults" / "readme.yml"
)


@dataclass(frozen=True)
class ReadmePatterns:
    """Pattern configuration for README generation."""

    include: tuple[str, ...]
    exclude: tuple[str, ...]


@dataclass(frozen=True)
class ReadmeTemplate:
    """Template configuration for generated README files."""

    use_directory_name: bool
    header_level: int
    footer: str


@dataclass(frozen=True)
class ReadmeLogging:
    """Logging configuration for README generation."""

    level: str
    log_skipped: bool
    log_created: bool


@dataclass(frozen=True)
class ReadmeConfig:
    """Complete README generation configuration."""

    enabled: bool
    patterns: ReadmePatterns
    template: ReadmeTemplate
    readme_variants: tuple[str, ...]
    logging: ReadmeLogging


class ReadmeConfigLoader:
    """Load and merge README configuration from multiple sources."""

    def __init__(self, repo_root: Path | None = None) -> None:
        """Initialize loader with repository root detection.

        Args:
            repo_root: Repository root path. If None, auto-detect.
        """
        if repo_root is None:
            repo_root = detect_repo_root(Path.cwd())
        self.repo_root = repo_root
        self.config = self._load_config()

    def _load_config(self) -> ReadmeConfig:
        """Load configuration from all sources and merge."""
        # 1. Load default configuration
        default_config = self._load_yaml(DEFAULT_README_CONFIG)

        # 2. Try to load local readme.yml (project root)
        local_config_path = self.repo_root / "readme.yml"
        local_config = {}
        if local_config_path.exists():
            local_config = self._load_yaml(local_config_path)
            LOGGER.debug("Loaded local readme.yml from %s", local_config_path)

        # 3. Merge configurations (local overrides default)
        merged = self._deep_merge(default_config, local_config)

        # 4. Parse into dataclasses
        return self._parse_config(merged)

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        """Load YAML configuration file."""
        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return data
        except Exception as exc:
            LOGGER.warning("Failed to load %s: %s", path, exc)
            return {}

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries (override wins)."""
        result = base.copy()
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _parse_config(self, data: dict) -> ReadmeConfig:
        """Parse configuration dictionary into dataclasses."""
        patterns_data = data.get("patterns", {})
        patterns = ReadmePatterns(
            include=tuple(patterns_data.get("include", [])),
            exclude=tuple(patterns_data.get("exclude", [])),
        )

        template_data = data.get("template", {})
        template = ReadmeTemplate(
            use_directory_name=template_data.get("use_directory_name", True),
            header_level=template_data.get("header_level", 1),
            footer=template_data.get("footer", ""),
        )

        logging_data = data.get("logging", {})
        logging_config = ReadmeLogging(
            level=logging_data.get("level", "info"),
            log_skipped=logging_data.get("log_skipped", False),
            log_created=logging_data.get("log_created", True),
        )

        return ReadmeConfig(
            enabled=data.get("enabled", True),
            patterns=patterns,
            template=template,
            readme_variants=tuple(
                data.get("readme_variants", ["README.md", "readme.md"])
            ),
            logging=logging_config,
        )

    def merge_with_override(self, override: Mapping[str, Any] | None) -> ReadmeConfig:
        """Merge current configuration with override from publish.yml.

        Args:
            override: Override configuration from publish.yml (readme: section)

        Returns:
            New ReadmeConfig with overrides applied
        """
        if not override:
            return self.config

        # Convert current config back to dict for merging
        current = {
            "enabled": self.config.enabled,
            "patterns": {
                "include": list(self.config.patterns.include),
                "exclude": list(self.config.patterns.exclude),
            },
            "template": {
                "use_directory_name": self.config.template.use_directory_name,
                "header_level": self.config.template.header_level,
                "footer": self.config.template.footer,
            },
            "readme_variants": list(self.config.readme_variants),
            "logging": {
                "level": self.config.logging.level,
                "log_skipped": self.config.logging.log_skipped,
                "log_created": self.config.logging.log_created,
            },
        }

        # Merge with override
        merged = self._deep_merge(current, dict(override))

        # Parse back to dataclass
        return self._parse_config(merged)

    def matches_patterns(self, path: Path, repo_root: Path | None = None) -> bool:
        """Check if path matches include/exclude patterns.

        Args:
            path: Path to check (can be absolute or relative)
            repo_root: Repository root for relative path conversion

        Returns:
            True if path should be processed, False if excluded
        """
        if repo_root is None:
            repo_root = self.repo_root

        # Convert to relative path for pattern matching
        try:
            rel_path = path.relative_to(repo_root)
        except ValueError:
            # Path is outside repo root
            return False

        # Convert to forward slashes for consistent pattern matching
        path_str = str(rel_path).replace("\\", "/")

        # Check exclude patterns first (exclude takes priority)
        for pattern in self.config.patterns.exclude:
            if fnmatch.fnmatch(path_str, pattern):
                return False

        # If include patterns are specified, check them
        if self.config.patterns.include:
            for pattern in self.config.patterns.include:
                if fnmatch.fnmatch(path_str, pattern):
                    return True
            # Path didn't match any include pattern
            return False

        # No include patterns specified = include all (except excluded)
        return True

    def has_readme(self, directory: Path) -> bool:
        """Check if directory has any README variant (case-insensitive).

        Args:
            directory: Directory path to check

        Returns:
            True if any readme variant exists
        """
        if not directory.is_dir():
            return False

        # Check each variant (case-insensitive on Windows, case-sensitive on Linux)
        for variant in self.config.readme_variants:
            candidate = directory / variant
            if candidate.exists():
                return True

        # On case-sensitive systems, also check lowercase variants
        # This handles the case where README.md exists but we're looking for readme.md
        try:
            # List all files in directory
            for item in directory.iterdir():
                if item.is_file():
                    # Check if filename matches any variant (case-insensitive)
                    for variant in self.config.readme_variants:
                        if item.name.lower() == variant.lower():
                            return True
        except (OSError, PermissionError):
            # Can't list directory, assume no README
            pass

        return False

    def generate_readme_content(self, directory: Path) -> str:
        """Generate README content for directory.

        Args:
            directory: Directory for which to generate README

        Returns:
            Generated README content
        """
        template = self.config.template

        # Generate header
        header_prefix = "#" * template.header_level
        directory_name = directory.name

        content = f"{header_prefix} {directory_name}\n"

        # Add footer if specified
        if template.footer:
            footer = template.footer.replace("{{directory_name}}", directory_name)
            content += footer

        # Ensure content ends with newline
        if not content.endswith("\n"):
            content += "\n"

        return content


__all__ = [
    "ReadmeConfig",
    "ReadmeConfigLoader",
    "ReadmePatterns",
    "ReadmeTemplate",
    "ReadmeLogging",
]
