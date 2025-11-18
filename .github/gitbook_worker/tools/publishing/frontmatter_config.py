#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Front matter configuration loader for the publishing system.

This module provides centralized front matter configuration management,
allowing control over YAML front matter injection via frontmatter.yml.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from tools.logging_config import get_logger
from tools.utils.semver import SemVerError, ensure_semver

logger = get_logger(__name__)


@dataclass
class FrontMatterPatterns:
    """Pattern matching configuration for front matter injection."""

    include: List[str]
    exclude: List[str]


@dataclass
class FrontMatterConfig:
    """Configuration for front matter injection."""

    enabled: bool
    patterns: FrontMatterPatterns
    template: Dict[str, Any]


class FrontMatterConfigLoader:
    """Loads and manages front matter configurations from frontmatter.yml."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the front matter configuration loader.

        Args:
            config_path: Path to frontmatter.yml. If None, searches in standard locations.
        """
        self._config_path = config_path or self._find_config_file()
        self._version: str = ""
        self._config: Optional[FrontMatterConfig] = None
        self._load_config()

    @staticmethod
    def _find_config_file() -> Path:
        """Find the frontmatter.yml configuration file.

        Search order:
        1. .github/gitbook_worker/defaults/frontmatter.yml
        2. defaults/frontmatter.yml
        3. frontmatter.yml (current directory)
        """
        search_paths = [
            Path(".github/gitbook_worker/defaults/frontmatter.yml"),
            Path("defaults/frontmatter.yml"),
            Path("frontmatter.yml"),
        ]

        for path in search_paths:
            if path.exists():
                logger.info("✓ Front matter configuration found: %s", path)
                return path.resolve()

        # Fallback to default location
        default_path = (
            Path(__file__).parent.parent.parent / "defaults" / "frontmatter.yml"
        )
        if default_path.exists():
            logger.info("✓ Front matter configuration found: %s", default_path)
            return default_path.resolve()

        raise FileNotFoundError(
            "Front matter configuration file (frontmatter.yml) not found in any standard location"
        )

    def _load_config(self) -> None:
        """Load front matter configuration from YAML file."""
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            data = data or {}

            # Validate version
            try:
                self._version = ensure_semver(
                    data.get("version"),
                    field="frontmatter.yml version",
                    default="1.0.0",
                )
            except SemVerError as exc:
                raise ValueError(str(exc)) from exc

            # Load configuration
            enabled = data.get("enabled", False)
            patterns_data = data.get("patterns", {})
            template = data.get("template", {})

            patterns = FrontMatterPatterns(
                include=patterns_data.get("include", []),
                exclude=patterns_data.get("exclude", []),
            )

            self._config = FrontMatterConfig(
                enabled=enabled, patterns=patterns, template=template
            )

            status = "ENABLED" if enabled else "DISABLED"
            logger.info("✓ Front matter configuration loaded: %s", status)

        except Exception as e:
            logger.error("Error loading front matter configuration: %s", e)
            raise

    @property
    def version(self) -> str:
        """Return the semantic version declared in frontmatter.yml."""
        return self._version

    @property
    def config(self) -> FrontMatterConfig:
        """Get the loaded front matter configuration."""
        if self._config is None:
            raise RuntimeError("Configuration not loaded")
        return self._config

    def merge_with_override(
        self, override: Optional[Dict[str, Any]]
    ) -> FrontMatterConfig:
        """Merge base configuration with publication-level overrides.

        Args:
            override: Override dictionary from publish.yml (frontmatter section)

        Returns:
            Merged FrontMatterConfig
        """
        if override is None or not override:
            return self.config

        # Start with base config values
        enabled = override.get("enabled", self.config.enabled)

        # Merge patterns
        patterns_override = override.get("patterns", {})
        include = patterns_override.get("include", self.config.patterns.include)
        exclude = patterns_override.get("exclude", self.config.patterns.exclude)
        patterns = FrontMatterPatterns(include=include, exclude=exclude)

        # Merge templates (override takes precedence, but keep base fields not overridden)
        template = self.config.template.copy()
        template_override = override.get("template", {})
        template.update(template_override)

        return FrontMatterConfig(enabled=enabled, patterns=patterns, template=template)

    def matches_patterns(self, file_path: Path, repo_root: Path) -> bool:
        """Check if a file path matches the inclusion/exclusion patterns.

        Args:
            file_path: Absolute path to the file to check
            repo_root: Repository root directory

        Returns:
            True if file matches include patterns and not excluded, False otherwise
        """
        try:
            relative_path = file_path.relative_to(repo_root)
        except ValueError:
            # File not under repo_root
            return False

        relative_str = relative_path.as_posix()

        # Check exclusion patterns first (they take precedence)
        for pattern in self.config.patterns.exclude:
            if relative_path.match(pattern):
                logger.debug("File excluded by pattern '%s': %s", pattern, relative_str)
                return False

        # Check inclusion patterns
        for pattern in self.config.patterns.include:
            if relative_path.match(pattern):
                logger.debug("File included by pattern '%s': %s", pattern, relative_str)
                return True

        # No include pattern matched
        return False
