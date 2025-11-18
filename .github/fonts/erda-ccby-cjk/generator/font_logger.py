"""Logging system for ERDA CC-BY CJK font generation.

This module provides structured logging for font build processes,
including character coverage tracking, build metrics, and error reporting.

License: CC BY 4.0
"""

import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


class FontBuildLogger:
    """Logger for font generation with metrics tracking."""

    def __init__(self, log_dir: str = "../logs", log_level: int = logging.INFO):
        """Initialize font build logger.

        Args:
            log_dir: Directory for log files (relative to script location)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.start_time = time.time()
        self.metrics: Dict = {
            "characters_processed": 0,
            "glyphs_generated": 0,
            "errors": [],
            "warnings": [],
            "character_sources": {
                "katakana": 0,
                "hangul": 0,
                "hanzi": 0,
                "punctuation": 0,
                "fallback": 0,
            },
        }

        # Create log directory
        self.log_dir = Path(__file__).parent / log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.log_file = self.log_dir / f"font-build-{timestamp}.log"

        # Configure logging
        self.logger = logging.getLogger("FontBuilder")
        self.logger.setLevel(log_level)

        # File handler (detailed)
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)

        # Console handler (summary)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.info(f"Log file: {self.log_file}")
        self.info("=" * 70)

    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
        self.metrics["warnings"].append(message)

    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
        self.metrics["errors"].append(message)

    def track_character(self, char: str, source: str) -> None:
        """Track character processing.

        Args:
            char: Character being processed
            source: Source module (katakana, hangul, hanzi, punctuation, fallback)
        """
        self.metrics["characters_processed"] += 1
        if source in self.metrics["character_sources"]:
            self.metrics["character_sources"][source] += 1
        self.debug(f"Character '{char}' (U+{ord(char):04X}) from {source}")

    def track_glyph(self, glyph_name: str, advance_width: int) -> None:
        """Track glyph generation.

        Args:
            glyph_name: Name of generated glyph
            advance_width: Width of the glyph
        """
        self.metrics["glyphs_generated"] += 1
        self.debug(f"Glyph '{glyph_name}' created (width: {advance_width})")

    def log_build_start(self, output_file: str, required_chars: int) -> None:
        """Log start of font build.

        Args:
            output_file: Output font file path
            required_chars: Number of characters to process
        """
        self.info("=" * 70)
        self.info("ERDA CC-BY CJK Font Build Started")
        self.info("=" * 70)
        self.info(f"Output file: {output_file}")
        self.info(f"Required characters: {required_chars}")
        self.info(f"Build started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.info("=" * 70)

    def log_build_complete(self, output_file: str, file_size: int) -> None:
        """Log successful completion of font build.

        Args:
            output_file: Path to generated font file
            file_size: Size of font file in bytes
        """
        elapsed = time.time() - self.start_time

        self.info("=" * 70)
        self.info("FONT BUILD COMPLETED SUCCESSFULLY")
        self.info("=" * 70)
        self.info(f"Font file: {output_file}")
        self.info(f"File size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
        self.info(f"Build time: {elapsed:.2f} seconds")
        self.info("")
        self.info("CHARACTER COVERAGE:")
        self.info(f"  Total processed: {self.metrics['characters_processed']}")
        self.info(f"  Glyphs generated: {self.metrics['glyphs_generated']}")
        self.info("")
        self.info("CHARACTER SOURCES:")
        for source, count in self.metrics["character_sources"].items():
            if count > 0:
                percentage = (
                    (count / self.metrics["characters_processed"] * 100)
                    if self.metrics["characters_processed"] > 0
                    else 0
                )
                self.info(f"  {source:12s}: {count:4d} ({percentage:5.1f}%)")

        if self.metrics["warnings"]:
            self.info("")
            self.info(f"WARNINGS: {len(self.metrics['warnings'])}")
            for warning in self.metrics["warnings"][:10]:  # Show first 10
                self.info(f"  - {warning}")
            if len(self.metrics["warnings"]) > 10:
                self.info(f"  ... and {len(self.metrics['warnings']) - 10} more")

        if self.metrics["errors"]:
            self.info("")
            self.info(f"ERRORS: {len(self.metrics['errors'])}")
            for error in self.metrics["errors"][:10]:  # Show first 10
                self.info(f"  - {error}")
            if len(self.metrics["errors"]) > 10:
                self.info(f"  ... and {len(self.metrics['errors']) - 10} more")

        self.info("=" * 70)
        self.info(f"Full log: {self.log_file}")
        self.info("=" * 70)

    def log_build_failed(self, error_message: str) -> None:
        """Log failed font build.

        Args:
            error_message: Error message
        """
        elapsed = time.time() - self.start_time

        self.error("=" * 70)
        self.error("FONT BUILD FAILED")
        self.error("=" * 70)
        self.error(f"Build time: {elapsed:.2f} seconds")
        self.error(f"Characters processed: {self.metrics['characters_processed']}")
        self.error(f"Error: {error_message}")
        self.error("=" * 70)
        self.error(f"Full log: {self.log_file}")
        self.error("=" * 70)

    def log_cache_refresh(self, system: str, success: bool) -> None:
        """Log font cache refresh operation.

        Args:
            system: System name (Windows, Linux, macOS)
            success: Whether refresh was successful
        """
        if success:
            self.info(f"✓ {system} font cache refreshed successfully")
        else:
            self.warning(f"✗ {system} font cache refresh failed or not supported")

    def get_summary(self) -> Dict:
        """Get build summary metrics.

        Returns:
            Dictionary with build metrics
        """
        return {
            "build_time": time.time() - self.start_time,
            "characters_processed": self.metrics["characters_processed"],
            "glyphs_generated": self.metrics["glyphs_generated"],
            "character_sources": self.metrics["character_sources"],
            "warnings_count": len(self.metrics["warnings"]),
            "errors_count": len(self.metrics["errors"]),
            "log_file": str(self.log_file),
        }
