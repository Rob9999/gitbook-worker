#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Font configuration loader for the publishing system.

This module provides centralized font configuration management,
eliminating hardcoded font paths from the codebase.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from tools.logging_config import get_logger
from tools.utils.semver import SemVerError, ensure_semver

logger = get_logger(__name__)


@dataclass(frozen=True)
class FontConfig:
    """Configuration for a single font."""

    name: str
    paths: List[str]
    license: str
    license_url: str
    source_url: Optional[str] = None
    download_url: Optional[str] = None


class FontConfigLoader:
    """Loads and manages font configurations from fonts.yml."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the font configuration loader.

        Args:
            config_path: Path to fonts.yml. If None, searches in standard locations.
        """
        self._config_path = config_path or self._find_config_file()
        self._version: str = ""
        self._fonts: Dict[str, FontConfig] = {}
        self._load_config()

    @staticmethod
    def _find_config_file() -> Path:
        """Find the fonts.yml configuration file.

        Search order:
        1. .github/gitbook_worker/defaults/fonts.yml
        2. defaults/fonts.yml
        3. fonts.yml (current directory)
        """
        search_paths = [
            Path(".github/gitbook_worker/defaults/fonts.yml"),
            Path("defaults/fonts.yml"),
            Path("fonts.yml"),
        ]

        for path in search_paths:
            if path.exists():
                logger.info("✓ Font-Konfiguration gefunden: %s", path)
                return path.resolve()

        # Fallback to default location
        default_path = Path(__file__).parent.parent.parent / "defaults" / "fonts.yml"
        if default_path.exists():
            logger.info("✓ Font-Konfiguration gefunden: %s", default_path)
            return default_path.resolve()

        raise FileNotFoundError(
            "Font configuration file (fonts.yml) not found in any standard location"
        )

    def _load_config(self) -> None:
        """Load font configurations from YAML file."""
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            data = data or {}

            try:
                self._version = ensure_semver(
                    data.get("version"),
                    field="fonts.yml version",
                    default="1.0.0",
                )
            except SemVerError as exc:
                raise ValueError(str(exc)) from exc

            fonts_data = data.get("fonts", {})
            for key, config in fonts_data.items():
                paths = config.get("paths", [])
                # Filter out None/empty paths
                paths = [p for p in paths if p]

                self._fonts[key] = FontConfig(
                    name=config.get("name", ""),
                    paths=paths,
                    license=config.get("license", ""),
                    license_url=config.get("license_url", ""),
                    source_url=config.get("source_url"),
                    download_url=config.get("download_url") or config.get("url"),
                )

            logger.info("✓ %d Font-Konfigurationen geladen", len(self._fonts))

        except Exception as e:
            logger.error("Fehler beim Laden der Font-Konfiguration: %s", e)
            raise

    @property
    def version(self) -> str:
        """Return the semantic version declared in fonts.yml."""

        return self._version

    def get_font(self, key: str) -> Optional[FontConfig]:
        """Get font configuration by key (e.g., 'CJK', 'SERIF').

        Args:
            key: Font configuration key (case-insensitive)

        Returns:
            FontConfig if found, None otherwise
        """
        return self._fonts.get(key.upper())

    def get_font_name(self, key: str, default: str = "") -> str:
        """Get font name by key.

        Args:
            key: Font configuration key
            default: Default value if font not found

        Returns:
            Font name or default
        """
        font = self.get_font(key)
        return font.name if font else default

    def get_font_paths(self, key: str) -> List[str]:
        """Get list of possible font paths by key.

        Args:
            key: Font configuration key

        Returns:
            List of font paths (may be empty for system fonts)
        """
        font = self.get_font(key)
        return font.paths if font else []

    def find_font_file(self, key: str) -> Optional[str]:
        """Find the first existing font file for the given key.

        Args:
            key: Font configuration key

        Returns:
            Path to existing font file, or None if not found
        """
        paths = self.get_font_paths(key)
        for path in paths:
            if os.path.exists(path):
                logger.debug("✓ Font gefunden: %s -> %s", key, path)
                return path

        if paths:
            logger.debug("Font %s nicht gefunden in: %s", key, paths)
        return None

    def get_all_font_keys(self) -> List[str]:
        """Get all available font configuration keys.

        Returns:
            List of font keys
        """
        return list(self._fonts.keys())

    def get_default_fonts(self) -> Dict[str, str]:
        """Get default font names for common roles.

        Returns:
            Dictionary mapping role to font name (serif, sans, mono, emoji, cjk)
        """
        return {
            "serif": self.get_font_name("SERIF", "DejaVu Serif"),
            "sans": self.get_font_name("SANS", "DejaVu Sans"),
            "mono": self.get_font_name("MONO", "DejaVu Sans Mono"),
            "emoji": self.get_font_name("EMOJI", "Twemoji Mozilla"),
            "cjk": self.get_font_name("CJK", "ERDA CC-BY CJK"),
        }

    def match_font_key(self, font_name: Optional[str]) -> Optional[str]:
        """Match a font display name to its configuration key.

        Tries exact match first, then case-insensitive partial match.

        Args:
            font_name: Font display name (e.g., "ERDA CC-BY CJK", "DejaVu Serif")

        Returns:
            Configuration key (e.g., "CJK", "SERIF") or None if no match

        Examples:
            >>> loader.match_font_key("ERDA CC-BY CJK")
            'CJK'
            >>> loader.match_font_key("DejaVu Serif")
            'SERIF'
        """
        if not font_name:
            return None

        # Exact match first
        for key, font in self._fonts.items():
            if font.name == font_name:
                return key

        # Case-insensitive partial match
        font_name_lower = font_name.lower()
        for key, font in self._fonts.items():
            if (
                font_name_lower in font.name.lower()
                or font.name.lower() in font_name_lower
            ):
                return key

        return None

    def merge_manifest_fonts(
        self, manifest_fonts: List[Dict[str, any]]
    ) -> "FontConfigLoader":
        """Create a new FontConfigLoader with manifest font overrides applied.

        This implements a hierarchical merge where fonts specified in publish.yml
        override the corresponding fonts from fonts.yml.

        Args:
            manifest_fonts: List of font specifications from publish.yml, each with:
                - name: Font display name (matched to config key)
                - path: Font file path (absolute or relative)
                - url: Optional download URL (not used in merge)

        Returns:
            New FontConfigLoader instance with merged configuration

        Example:
            >>> base = get_font_config()
            >>> manifest = [{"name": "ERDA CC-BY CJK", "path": "custom/path.ttf"}]
            >>> merged = base.merge_manifest_fonts(manifest)
            >>> merged.get_font_paths("CJK")
            ['custom/path.ttf']
        """
        # Create a new loader with same base config
        merged = FontConfigLoader.__new__(FontConfigLoader)
        merged._config_path = self._config_path
        merged._fonts = {}

        # Copy all base fonts
        for key, font in self._fonts.items():
            merged._fonts[key] = FontConfig(
                name=font.name,
                paths=font.paths.copy(),
                license=font.license,
                license_url=font.license_url,
                source_url=font.source_url,
                download_url=getattr(font, "download_url", None),
            )

        # Apply manifest overrides
        for font_spec in manifest_fonts:
            if not isinstance(font_spec, dict):
                continue

            font_name = font_spec.get("name")
            font_path = font_spec.get("path")

            if not font_name or not font_path:
                continue

            # Try to match display name to config key
            key = self.match_font_key(font_name)
            if key and key in merged._fonts:
                logger.info(
                    "✓ Manifest override: %s (%s) → %s",
                    font_name,
                    key,
                    font_path,
                )
                # Override with single path from manifest
                merged._fonts[key] = FontConfig(
                    name=merged._fonts[key].name,
                    paths=[str(font_path)],  # Single path from manifest
                    license=merged._fonts[key].license,
                    license_url=merged._fonts[key].license_url,
                    source_url=merged._fonts[key].source_url,
                    download_url=font_spec.get("url") or font_spec.get("download_url"),
                )
            else:
                logger.debug(
                    "Font '%s' aus manifest konnte keinem Key zugeordnet werden",
                    font_name,
                )

        return merged


# Global singleton instance
_loader: Optional[FontConfigLoader] = None


def get_font_config() -> FontConfigLoader:
    """Get the global FontConfigLoader instance (singleton).

    Returns:
        FontConfigLoader instance
    """
    global _loader
    if _loader is None:
        _loader = FontConfigLoader()
    return _loader


def reset_font_config() -> None:
    """Reset the global FontConfigLoader instance (mainly for testing)."""
    global _loader
    _loader = None
