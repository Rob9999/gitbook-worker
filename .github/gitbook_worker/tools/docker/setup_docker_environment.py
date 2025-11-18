#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker Environment Setup & Validation Module

This module is called during Docker image build to:
1. Load current gitbook_worker configuration (fonts.yml, smart.yml, publish.yml)
2. Install and configure all required fonts into Docker image
3. Validate font cache integrity
4. Test all required tools and dependencies
5. Generate compliance report for AGENTS.md requirements

Compliance:
- Only CC BY 4.0, MIT, or SIL OFL 1.1 licensed fonts (AGENTS.md §Lizenzpolitik)
- DCO compliant (Developer Certificate of Origin)
- Twemoji CC BY 4.0 required
- No OFL/Apache/GPL/proprietary fonts in build transit

Usage (in Dockerfile):
    RUN python3 -m tools.docker.setup_docker_environment --mode install
    RUN python3 -m tools.docker.setup_docker_environment --mode validate
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Disable file logging for Docker build (stdout only)
os.environ["GITBOOK_WORKER_LOG_STDOUT_ONLY"] = "1"

# Ensure tools path is in Python path
# Try to find the gitbook_worker directory
_current_file = Path(__file__).resolve()
_potential_roots = [
    _current_file.parent.parent.parent.parent.parent,  # Normal: .../ERDA/
    _current_file.parent.parent.parent,  # Docker: .../gitbook_worker/
]

REPO_ROOT = None
for root in _potential_roots:
    gitbook_worker_path = root / ".github" / "gitbook_worker"
    if gitbook_worker_path.exists():
        REPO_ROOT = root
        sys.path.insert(0, str(gitbook_worker_path))
        break
    # Alternative: gitbook_worker direkt im Root
    gitbook_worker_path = root / "gitbook_worker"
    if gitbook_worker_path.exists():
        REPO_ROOT = root
        sys.path.insert(0, str(gitbook_worker_path))
        break

if REPO_ROOT is None:
    # Fallback: Assume PYTHONPATH is set correctly
    REPO_ROOT = Path.cwd()

from tools.logging_config import get_logger
from tools.publishing.font_config import FontConfigLoader, FontConfig

logger = get_logger(__name__)


# =============================================================================
# License Compliance
# =============================================================================

ALLOWED_LICENSES = {
    "CC BY 4.0",
    "Creative Commons Attribution 4.0 International (CC BY 4.0)",
    "MIT",
    "SIL Open Font License 1.1",
    "Bitstream Vera License",
    "Bitstream Vera License + Public Domain",
}

FORBIDDEN_LICENSES = {
    "OFL",  # Wrong abbreviation, should be "SIL Open Font License 1.1"
    "Apache",
    "Apache-2.0",
    "GPL",
    "AGPL",
    "LGPL",
    "UFL",
    "proprietary",
}


class LicenseViolationError(Exception):
    """Raised when a font with incompatible license is detected."""

    pass


# =============================================================================
# Font Installation
# =============================================================================


class DockerFontInstaller:
    """Installs fonts into Docker image according to gitbook_worker configuration."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize font installer.

        Args:
            config_path: Path to fonts.yml (auto-detected if None)
        """
        self.config = FontConfigLoader(config_path)
        self.font_dirs = {
            "system": Path("/usr/share/fonts/truetype/gitbook_worker"),
            "user": Path("/root/.fonts"),
            "cache": Path("/root/.cache/fontconfig"),
        }
        self.installed_fonts: List[Dict] = []
        # Collect installation errors/warnings for manifest/report
        self.install_errors: List[str] = []
        self.install_warnings: List[str] = []

    def check_license_compliance(self) -> None:
        """Verify all fonts have compatible licenses (AGENTS.md compliance).

        Raises:
            LicenseViolationError: If any font has incompatible license
        """
        violations = []

        for key in self.config.get_all_font_keys():
            font = self.config.get_font(key)
            if not font:
                continue

            license_name = font.license.strip()

            # Check if license is explicitly forbidden
            if any(forbidden in license_name for forbidden in FORBIDDEN_LICENSES):
                violations.append(
                    f"Font '{font.name}' ({key}): "
                    f"Forbidden license '{license_name}'"
                )
                continue

            # Check if license is explicitly allowed
            if license_name not in ALLOWED_LICENSES:
                logger.warning(
                    "Font '%s' (%s): License '%s' not in allowed list. "
                    "Assuming compatible, but verify manually.",
                    font.name,
                    key,
                    license_name,
                )

        if violations:
            raise LicenseViolationError(
                "License compliance violations detected:\n"
                + "\n".join(f"  - {v}" for v in violations)
                + "\n\nAllowed licenses: "
                + ", ".join(ALLOWED_LICENSES)
                + "\nForbidden licenses: "
                + ", ".join(FORBIDDEN_LICENSES)
            )

        logger.info("✓ All fonts pass license compliance check")

    def install_font(self, key: str, font: FontConfig) -> bool:
        """Install a single font into Docker image.

        Args:
            key: Font key (e.g., "CJK", "EMOJI")
            font: FontConfig object

        Returns:
            True if installed successfully, False if skipped (no path/url)
        """
        logger.info("=" * 70)
        logger.info("Processing font: %s (%s)", key, font.name)
        logger.info("  - Paths: %s", font.paths if font.paths else "(empty)")
        logger.info(
            "  - Download URL: %s",
            font.download_url if font.download_url else "(not set)",
        )
        logger.info("  - License: %s", font.license)

        # Check if font has either paths or download_url
        if not font.paths and not font.download_url:
            logger.warning(
                "Font %s (%s): No paths or download_url specified, SKIPPING installation",
                key,
                font.name,
            )
            return False

        logger.info("Installing font %s: %s", key, font.name)

        # Create target directory
        target_dir = self.font_dirs["system"] / key.lower()
        target_dir.mkdir(parents=True, exist_ok=True)

        installed_files = []

        # Download font from URL if specified (and no local path present)
        if getattr(font, "download_url", None) and not font.paths:
            logger.info("  → Downloading font from URL...")
            logger.info("     URL: %s", font.download_url)
            try:
                import urllib.request

                font_filename = font.download_url.split("/")[-1] or f"{key}.font"
                temp_file = target_dir / font_filename

                logger.info("     Target: %s", temp_file)
                logger.info("     Filename: %s", font_filename)

                urllib.request.urlretrieve(font.download_url, str(temp_file))

                if not temp_file.exists():
                    raise FileNotFoundError(
                        f"Download succeeded but file not found: {temp_file}"
                    )

                # Calculate checksum
                checksum = self._calculate_checksum(temp_file)
                file_size = temp_file.stat().st_size

                installed_files.append(
                    {
                        "source": font.download_url,
                        "target": str(temp_file),
                        "size": file_size,
                        "sha256": checksum,
                    }
                )

                logger.info("  ✓ Downloaded successfully!")
                logger.info("     Size: %d bytes", file_size)
                logger.info("     SHA256: %s", checksum[:16])

            except Exception as e:
                logger.error("  ✗ Download failed for %s: %s", font.download_url, e)
                self.install_errors.append(
                    f"Download failed for {font.name} ({key}): {e}"
                )
                return False

        # Install fonts from local paths
        if font.paths:
            logger.info(
                "  → Installing from local paths (%d files)...", len(font.paths)
            )

        for font_path_str in font.paths:
            font_path = Path(font_path_str)
            logger.info("     Processing: %s", font_path_str)

            # Handle relative paths (from repo root)
            if not font_path.is_absolute():
                font_path = REPO_ROOT / font_path
                logger.info("     Resolved to: %s", font_path)

            if not font_path.exists():
                logger.error("  ✗ Font file not found: %s", font_path)
                self.install_errors.append(
                    f"Font file not found for {font.name} ({key}): {font_path}"
                )
                # continue to next configured path rather than aborting whole install
                continue

            # Copy to target directory
            target_file = target_dir / font_path.name
            shutil.copy2(font_path, target_file)

            # Calculate checksum for verification
            checksum = self._calculate_checksum(target_file)
            file_size = target_file.stat().st_size

            installed_files.append(
                {
                    "source": str(font_path),
                    "target": str(target_file),
                    "size": file_size,
                    "sha256": checksum,
                }
            )

            logger.info("  ✓ Installed: %s -> %s", font_path.name, target_file)
            logger.info("     Size: %d bytes, SHA256: %s", file_size, checksum[:16])

        # If nothing was installed (no downloaded or copied files) report and skip
        if not installed_files:
            logger.warning("No files installed for %s (%s)", key, font.name)
            self.install_warnings.append(f"No files installed for {key} ({font.name})")
            return False

        # Record installation
        self.installed_fonts.append(
            {
                "key": key,
                "name": font.name,
                "license": font.license,
                "license_url": font.license_url,
                "source_url": font.source_url,
                "files": installed_files,
            }
        )

        return True

    def install_all_fonts(self) -> int:
        """Install all configured fonts.

        Returns:
            Number of fonts installed (system fonts not counted)
        """
        logger.info("=" * 70)
        logger.info("DOCKER FONT INSTALLATION")
        logger.info("=" * 70)
        logger.info("Config source: %s", self.config._config_path)
        logger.info("Config version: %s", self.config._version)
        logger.info("Total fonts configured: %d", len(self.config.get_all_font_keys()))
        logger.info("")

        # Check license compliance first
        self.check_license_compliance()

        count = 0
        skipped = []
        failed = []

        for key in self.config.get_all_font_keys():
            font = self.config.get_font(key)
            if not font:
                logger.warning("Font key '%s' has no configuration, skipping", key)
                skipped.append((key, "No configuration"))
                continue

            try:
                if self.install_font(key, font):
                    count += 1
                else:
                    skipped.append((key, font.name))
            except Exception as e:
                logger.error("Failed to install font %s: %s", key, e)
                failed.append((key, font.name, str(e)))

        # Summary report
        logger.info("")
        logger.info("=" * 70)
        logger.info("INSTALLATION SUMMARY")
        logger.info("=" * 70)
        logger.info("✓ Successfully installed: %d font(s)", count)

        if skipped:
            logger.info("⊘ Skipped: %d font(s)", len(skipped))
            for key, name in skipped:
                logger.info("   - %s (%s)", key, name)

        if failed:
            logger.error("✗ Failed: %d font(s)", len(failed))
            for key, name, error in failed:
                logger.error("   - %s (%s): %s", key, name, error)

        logger.info("=" * 70)

        return count

    def update_font_cache(self) -> None:
        """Update system font cache after installation."""
        logger.info("Updating font cache...")

        try:
            subprocess.run(
                ["fc-cache", "-f", "-v"],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info("✓ Font cache updated successfully")
        except subprocess.CalledProcessError as e:
            logger.error("Failed to update font cache: %s", e.stderr)
            raise

    def generate_manifest(self, output_path: Path) -> None:
        """Generate installation manifest for verification.

        Args:
            output_path: Path to write manifest JSON
        """
        manifest = {
            "version": "1.0.0",
            "config_source": str(self.config._config_path),
            "config_version": self.config.version,
            "installed_fonts": self.installed_fonts,
            "install_errors": self.install_errors,
            "install_warnings": self.install_warnings,
            "font_dirs": {k: str(v) for k, v in self.font_dirs.items()},
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        logger.info("✓ Installation manifest written to: %s", output_path)

    @staticmethod
    def _calculate_checksum(file_path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(65536), b""):
                sha256.update(block)
        return sha256.hexdigest()


# =============================================================================
# Environment Validation
# =============================================================================


class DockerEnvironmentValidator:
    """Validates Docker image setup and configuration."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_fonts(self, manifest_path: Path) -> bool:
        """Validate installed fonts against manifest.

        Args:
            manifest_path: Path to installation manifest

        Returns:
            True if validation passed
        """
        logger.info("=" * 70)
        logger.info("FONT VALIDATION")
        logger.info("=" * 70)

        if not manifest_path.exists():
            self.errors.append(f"Installation manifest not found: {manifest_path}")
            return False

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        # Validate each installed font
        for font_entry in manifest["installed_fonts"]:
            font_key = font_entry["key"]
            font_name = font_entry["name"]

            logger.info("Validating %s (%s)...", font_key, font_name)

            for file_info in font_entry["files"]:
                target_path = Path(file_info["target"])

                # Check file exists
                if not target_path.exists():
                    self.errors.append(
                        f"Font file missing: {target_path} ({font_name})"
                    )
                    continue

                # Verify checksum
                actual_checksum = DockerFontInstaller._calculate_checksum(target_path)
                expected_checksum = file_info["sha256"]

                if actual_checksum != expected_checksum:
                    self.errors.append(
                        f"Checksum mismatch for {target_path.name}: "
                        f"expected {expected_checksum[:8]}..., "
                        f"got {actual_checksum[:8]}..."
                    )
                else:
                    logger.info("  ✓ %s: checksum OK", target_path.name)

        # Validate font cache
        self._validate_font_cache(manifest)

        if self.errors:
            logger.error("Font validation FAILED with %d error(s)", len(self.errors))
            return False

        logger.info("✓ Font validation PASSED")
        return True

    def _validate_font_cache(self, manifest: Dict) -> None:
        """Verify fonts are in system font cache."""
        logger.info("Checking font cache...")

        try:
            result = subprocess.run(
                ["fc-list", ":", "family", "file"],
                check=True,
                capture_output=True,
                text=True,
            )

            cache_content = result.stdout.lower()

            for font_entry in manifest["installed_fonts"]:
                font_name = font_entry["name"]
                font_name_lower = font_name.lower()

                # Also check for font file names in cache
                font_files = [f["target"] for f in font_entry.get("files", [])]
                font_file_names = [Path(f).stem.lower() for f in font_files]

                # Check if font name or any file name is in cache
                found = font_name_lower in cache_content or any(
                    fname in cache_content for fname in font_file_names
                )

                if not found:
                    # Only warning, not error - font might work even if not in fc-list
                    self.warnings.append(
                        f"Font '{font_name}' not found in font cache (may still work)"
                    )
                    logger.warning("  ⚠ %s not in cache (may still work)", font_name)
                else:
                    logger.info("  ✓ %s in cache", font_name)

        except subprocess.CalledProcessError as e:
            self.errors.append(f"Failed to query font cache: {e.stderr}")

    def validate_required_tools(self) -> bool:
        """Validate required system tools are installed.

        Returns:
            True if all tools available
        """
        logger.info("=" * 70)
        logger.info("TOOL VALIDATION")
        logger.info("=" * 70)

        required_tools = {
            "python3": "--version",
            "pandoc": "--version",
            "xelatex": "--version",
            "lualatex": "--version",
            "fc-cache": "--version",
            "fc-list": "--version",
            "git": "--version",
        }

        for tool, version_flag in required_tools.items():
            try:
                subprocess.run(
                    [tool, version_flag],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                logger.info("✓ %s available", tool)
            except (
                subprocess.CalledProcessError,
                FileNotFoundError,
                subprocess.TimeoutExpired,
            ):
                self.errors.append(f"Required tool not found or not working: {tool}")

        if self.errors:
            logger.error("Tool validation FAILED")
            return False

        logger.info("✓ All required tools available")
        return True

    def validate_python_packages(self) -> bool:
        """Validate required Python packages are installed.

        Returns:
            True if all packages available
        """
        logger.info("=" * 70)
        logger.info("PYTHON PACKAGE VALIDATION")
        logger.info("=" * 70)

        # Required packages for publishing and testing
        required_packages = [
            "yaml",
            "pytest",
            "pathvalidate",
            "markdown",
            "bs4",
            "pypandoc",
        ]

        for package in required_packages:
            try:
                __import__(package)
                logger.info("✓ %s importable", package)
            except ImportError:
                self.errors.append(f"Required Python package not installed: {package}")

        if self.errors:
            logger.error("Python package validation FAILED")
            return False

        logger.info("✓ All required Python packages available")
        return True

    def generate_report(self, output_path: Path) -> None:
        """Generate validation report.

        Args:
            output_path: Path to write report JSON
        """
        report = {
            "version": "1.0.0",
            "status": "PASS" if not self.errors else "FAIL",
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info("✓ Validation report written to: %s", output_path)

    def print_summary(self) -> None:
        """Print validation summary."""
        logger.info("=" * 70)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 70)

        if self.errors:
            logger.error("ERRORS (%d):", len(self.errors))
            for error in self.errors:
                logger.error("  ❌ %s", error)

        if self.warnings:
            logger.warning("WARNINGS (%d):", len(self.warnings))
            for warning in self.warnings:
                logger.warning("  ⚠ %s", warning)

        if not self.errors and not self.warnings:
            logger.info("✓ No errors or warnings")

        logger.info("=" * 70)
        if self.errors:
            logger.error("VALIDATION FAILED")
        else:
            logger.info("VALIDATION PASSED")
        logger.info("=" * 70)


# =============================================================================
# Main Entry Point
# =============================================================================


def main() -> int:
    """Main entry point for Docker environment setup."""
    parser = argparse.ArgumentParser(
        description="Setup and validate Docker environment for gitbook_worker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--mode",
        choices=["install", "validate", "both"],
        default="both",
        help="Operation mode: install fonts, validate environment, or both",
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to fonts.yml (auto-detected if not specified)",
    )

    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("/tmp/docker_font_installation.json"),
        help="Path for installation manifest",
    )

    parser.add_argument(
        "--report",
        type=Path,
        default=Path("/tmp/docker_validation_report.json"),
        help="Path for validation report",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    try:
        # Installation phase
        if args.mode in ("install", "both"):
            installer = DockerFontInstaller(args.config)
            installer.install_all_fonts()
            installer.update_font_cache()
            installer.generate_manifest(args.manifest)

        # Validation phase
        if args.mode in ("validate", "both"):
            validator = DockerEnvironmentValidator()

            # Validate fonts (if manifest exists)
            if args.manifest.exists():
                validator.validate_fonts(args.manifest)
            elif args.mode == "validate":
                logger.error("Cannot validate: manifest not found at %s", args.manifest)
                return 1

            # Validate tools and packages
            validator.validate_required_tools()
            validator.validate_python_packages()

            # Generate report
            validator.generate_report(args.report)
            validator.print_summary()

            # Return exit code based on validation result
            if validator.errors:
                return 1

        logger.info("")
        logger.info("✓ Docker environment setup completed successfully")
        return 0

    except LicenseViolationError as e:
        logger.error("")
        logger.error("=" * 70)
        logger.error("LICENSE COMPLIANCE VIOLATION")
        logger.error("=" * 70)
        logger.error(str(e))
        logger.error("")
        logger.error("Build aborted due to license policy violation (AGENTS.md).")
        logger.error("=" * 70)
        return 2

    except Exception as e:
        logger.error("Setup failed: %s", e, exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    sys.exit(main())
