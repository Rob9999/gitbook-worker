"""
Configuration System for ERDA CC-BY CJK Font Generator.

This module provides a flexible configuration system that externalizes
hardcoded constants and supports YAML-based configuration files.

Features:
- Dataclass-based configuration with validation
- YAML configuration file support
- Sensible defaults for all settings
- Grid size configuration (8×8, 16×16, 24×24)
- Font metadata configuration
- Build output configuration

License: MIT (code), CC BY 4.0 (font glyphs)
"""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class GridConfig:
    """Grid and bitmap configuration."""

    em: int = 1000
    """EM units (font units per em). Standard: 1000"""

    pixels: int = 8
    """Bitmap grid size in pixels (width and height). Options: 8, 16, 24"""

    @property
    def cell(self) -> int:
        """Cell size in EM units."""
        return self.em // (self.pixels + 2)

    @property
    def margin(self) -> int:
        """Margin size in EM units."""
        return self.cell

    def validate(self):
        """Validate grid configuration."""
        if self.em <= 0:
            raise ValueError(f"EM must be positive, got {self.em}")

        if self.pixels not in (8, 16, 24, 32):
            raise ValueError(f"PIXELS must be 8, 16, 24, or 32, got {self.pixels}")


@dataclass
class FontMetadata:
    """Font metadata configuration."""

    family_name: str = "ERDA CC-BY CJK"
    """Font family name"""

    full_name: str = "ERDA CC-BY CJK Fallback"
    """Full font name"""

    version: str = "1.0.1"
    """Font version"""

    copyright_notice: str = (
        "© 2025 ERDA Project. "
        "This font is licensed under CC BY 4.0. "
        "Code is licensed under MIT."
    )
    """Copyright notice"""

    license: str = "CC BY 4.0"
    """License identifier"""

    license_url: str = "https://creativecommons.org/licenses/by/4.0/"
    """License URL"""

    vendor: str = "ERDA Project"
    """Vendor name"""

    designer: str = "ERDA Contributors"
    """Designer name"""

    description: str = (
        "Fallback font for CJK (Chinese, Japanese, Korean) characters "
        "with CC BY 4.0 license. Monospace bitmap font."
    )
    """Font description"""

    def validate(self):
        """Validate font metadata."""
        if not self.family_name:
            raise ValueError("family_name cannot be empty")

        if not self.version:
            raise ValueError("version cannot be empty")


@dataclass
class BuildConfig:
    """Build output configuration."""

    output_dir: Path = field(default_factory=lambda: Path("../true-type"))
    """Output directory for generated font"""

    output_filename: str = "erda-ccby-cjk.ttf"
    """Output filename"""

    log_dir: Path = field(default_factory=lambda: Path("../logs"))
    """Log directory"""

    enable_logging: bool = True
    """Enable build logging"""

    enable_cache: bool = True
    """Enable font cache"""

    def validate(self):
        """Validate build configuration."""
        if not self.output_filename:
            raise ValueError("output_filename cannot be empty")

        if not self.output_filename.endswith(".ttf"):
            raise ValueError("output_filename must end with .ttf")

    @property
    def output_path(self) -> Path:
        """Full output path."""
        return self.output_dir / self.output_filename


@dataclass
class CharacterConfig:
    """Character coverage configuration."""

    include_hiragana: bool = True
    """Include all Hiragana characters"""

    include_katakana: bool = True
    """Include all Katakana characters"""

    include_hangul_algorithmic: bool = True
    """Include algorithmic Hangul generation (11,172 syllables)"""

    include_hanzi_kanji: bool = True
    """Include defined Hanzi/Kanji characters"""

    include_punctuation: bool = True
    """Include CJK punctuation"""

    dataset_files: List[str] = field(
        default_factory=lambda: [
            "chinese.md",
            "japanese.md",
            "korean.md",
            "test-documents.md",
        ]
    )
    """Dataset files to scan for required characters"""

    fallback_for_undefined: bool = True
    """Generate fallback glyphs for undefined characters"""

    def validate(self):
        """Validate character configuration."""
        if not any(
            [
                self.include_hiragana,
                self.include_katakana,
                self.include_hangul_algorithmic,
                self.include_hanzi_kanji,
                self.include_punctuation,
            ]
        ):
            raise ValueError("At least one character set must be enabled")


@dataclass
class FontConfig:
    """Complete font generator configuration."""

    grid: GridConfig = field(default_factory=GridConfig)
    metadata: FontMetadata = field(default_factory=FontMetadata)
    build: BuildConfig = field(default_factory=BuildConfig)
    characters: CharacterConfig = field(default_factory=CharacterConfig)

    def validate(self):
        """Validate all configuration sections."""
        self.grid.validate()
        self.metadata.validate()
        self.build.validate()
        self.characters.validate()

    @classmethod
    def from_yaml(cls, filepath: Path) -> FontConfig:
        """Load configuration from YAML file.

        Args:
            filepath: Path to YAML configuration file

        Returns:
            FontConfig instance

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If YAML is invalid
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data:
            return cls()

        # Parse sections
        grid_data = data.get("grid", {})
        metadata_data = data.get("metadata", {})
        build_data = data.get("build", {})
        characters_data = data.get("characters", {})

        # Convert Path strings
        if "output_dir" in build_data:
            build_data["output_dir"] = Path(build_data["output_dir"])
        if "log_dir" in build_data:
            build_data["log_dir"] = Path(build_data["log_dir"])

        config = cls(
            grid=GridConfig(**grid_data),
            metadata=FontMetadata(**metadata_data),
            build=BuildConfig(**build_data),
            characters=CharacterConfig(**characters_data),
        )

        config.validate()
        return config

    def to_yaml(self, filepath: Path):
        """Save configuration to YAML file.

        Args:
            filepath: Path to save YAML file
        """
        data = {
            "grid": {
                "em": self.grid.em,
                "pixels": self.grid.pixels,
            },
            "metadata": {
                "family_name": self.metadata.family_name,
                "full_name": self.metadata.full_name,
                "version": self.metadata.version,
                "copyright_notice": self.metadata.copyright_notice,
                "license": self.metadata.license,
                "license_url": self.metadata.license_url,
                "vendor": self.metadata.vendor,
                "designer": self.metadata.designer,
                "description": self.metadata.description,
            },
            "build": {
                "output_dir": str(self.build.output_dir),
                "output_filename": self.build.output_filename,
                "log_dir": str(self.build.log_dir),
                "enable_logging": self.build.enable_logging,
                "enable_cache": self.build.enable_cache,
            },
            "characters": {
                "include_hiragana": self.characters.include_hiragana,
                "include_katakana": self.characters.include_katakana,
                "include_hangul_algorithmic": self.characters.include_hangul_algorithmic,
                "include_hanzi_kanji": self.characters.include_hanzi_kanji,
                "include_punctuation": self.characters.include_punctuation,
                "dataset_files": self.characters.dataset_files,
                "fallback_for_undefined": self.characters.fallback_for_undefined,
            },
        }

        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


# Global configuration instance
_config: Optional[FontConfig] = None


def get_config() -> FontConfig:
    """Get the global configuration instance.

    Returns:
        FontConfig instance
    """
    global _config

    if _config is None:
        # Try to load from config file
        config_file = Path(__file__).parent / "font-config.yaml"

        if config_file.exists():
            _config = FontConfig.from_yaml(config_file)
        else:
            # Use defaults
            _config = FontConfig()
            _config.validate()

    return _config


def set_config(config: FontConfig):
    """Set the global configuration instance.

    Args:
        config: FontConfig to use globally
    """
    global _config
    config.validate()
    _config = config


def load_config(filepath: Path) -> FontConfig:
    """Load and set configuration from file.

    Args:
        filepath: Path to configuration file

    Returns:
        Loaded FontConfig instance
    """
    config = FontConfig.from_yaml(filepath)
    set_config(config)
    return config


if __name__ == "__main__":
    # Test configuration system
    print("Testing Font Configuration System...")
    print("=" * 70)

    # Create default config
    config = FontConfig()
    config.validate()

    print("\n📋 Default Configuration:")
    print(f"   Grid: {config.grid.pixels}×{config.grid.pixels} pixels")
    print(f"   EM: {config.grid.em} units")
    print(f"   Cell: {config.grid.cell} units")
    print(f"   Margin: {config.grid.margin} units")
    print(f"   Font: {config.metadata.family_name} v{config.metadata.version}")
    print(f"   Output: {config.build.output_path}")
    print(f"   License: {config.metadata.license}")

    # Save example config
    example_file = Path(__file__).parent / "font-config.example.yaml"
    config.to_yaml(example_file)
    print(f"\n💾 Example config saved to: {example_file}")

    # Test loading
    loaded = FontConfig.from_yaml(example_file)
    print(f"✅ Successfully loaded and validated configuration")

    print("\n" + "=" * 70)
