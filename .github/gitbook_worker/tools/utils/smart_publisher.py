"""Smart publisher for converting publish targets to output formats.

This module provides high-level publishing coordination:
- Process PublishTarget objects from smart_publish_target
- Coordinate with existing publisher.py functions
- Handle both file and folder sources
- Integrate book.json configuration
- Manage build lifecycle (prepare, build, cleanup)

Migration from:
- publisher.py (main, get_publish_list workflow)
- Provides clean abstraction over legacy publisher functions

Smart Merge Philosophy:
1. Explicit: Use target configuration as provided
2. Convention: Apply sensible defaults from book.json
3. Fallback: Graceful degradation when resources missing
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from tools.utils.smart_publish_target import (
    PublishTarget,
    get_buildable_targets,
    get_target_content_root,
    load_publish_targets,
)

# Import legacy publisher functions (will be refactored later)
try:
    from tools.publishing import publisher as legacy_publisher
except ImportError:
    legacy_publisher = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BuildResult:
    """Result of building a publish target.

    Attributes:
        target: The PublishTarget that was built
        success: Whether build succeeded
        output_path: Path to generated output file (if successful)
        error_message: Error message if build failed
    """

    target: PublishTarget
    success: bool
    output_path: Optional[Path]
    error_message: Optional[str]


class SmartPublisher:
    """High-level publisher coordinating target conversion.

    This class provides the main publishing workflow:
    1. Load targets from manifest
    2. Prepare environment (fonts, dependencies)
    3. Build each target
    4. Collect results

    Examples:
        >>> publisher = SmartPublisher("publish.yml")
        >>> publisher.prepare_environment()
        >>> results = publisher.build_all()
        >>> for result in results:
        ...     if result.success:
        ...         print(f"✓ {result.target.out}")
        ...     else:
        ...         print(f"✗ {result.target.out}: {result.error_message}")
    """

    def __init__(
        self,
        manifest_path: Path | str,
        *,
        only_build: bool = True,
        no_apt: bool = False,
    ):
        """Initialize smart publisher.

        Args:
            manifest_path: Path to publish.yml manifest
            only_build: If True, process only targets with build=True
            no_apt: If True, skip apt package installation
        """
        self.manifest_path = Path(manifest_path).resolve()
        self.only_build = only_build
        self.no_apt = no_apt
        self._targets: Optional[List[PublishTarget]] = None
        self._prepared = False

    @property
    def targets(self) -> List[PublishTarget]:
        """Get loaded publish targets (lazy loading)."""
        if self._targets is None:
            self._targets = load_publish_targets(
                self.manifest_path,
                only_build=self.only_build,
            )
        return self._targets

    def prepare_environment(self) -> bool:
        """Prepare publishing environment (fonts, LaTeX, Pandoc).

        Returns:
            True if preparation succeeded, False otherwise
        """
        if self._prepared:
            logger.info("Environment already prepared")
            return True

        logger.info("Preparing publishing environment...")

        if legacy_publisher is None:
            logger.error("Legacy publisher module not available")
            return False

        try:
            # Call legacy prepare_publishing function
            legacy_publisher.prepare_publishing(
                no_apt=self.no_apt,
                manifest_path=str(self.manifest_path),
            )
            self._prepared = True
            logger.info("✓ Environment preparation complete")
            return True

        except Exception as exc:
            logger.error("✗ Environment preparation failed: %s", exc)
            return False

    def build_target(self, target: PublishTarget) -> BuildResult:
        """Build a single publish target.

        Args:
            target: PublishTarget to build

        Returns:
            BuildResult with build status and details
        """
        logger.info(
            "Building target %d: %s -> %s", target.index, target.path, target.out
        )

        if legacy_publisher is None:
            return BuildResult(
                target=target,
                success=False,
                output_path=None,
                error_message="Legacy publisher module not available",
            )

        try:
            # Determine content root (use book.json if available)
            content_root = get_target_content_root(target)

            # Prepare legacy build_pdf arguments
            summary_layout = None
            if target.book_config and (
                target.use_book_json
                or target.summary_mode
                or target.summary_order_manifest
            ):
                # Create SummaryContext from book_config
                from tools.publishing.gitbook_style import SummaryContext

                summary_layout = SummaryContext(
                    base_dir=target.book_config.base_dir,
                    root_dir=target.book_config.content_root,
                    summary_path=target.book_config.summary_path,
                )

            # Prepare emoji options
            emoji_options = None
            if target.pdf_options:
                from tools.publishing.publisher import EmojiOptions

                emoji_options = EmojiOptions(
                    color=target.pdf_options.get("emoji_color", True),
                    report=False,
                    report_dir=None,
                )

            # Prepare variables (fonts, etc.)
            variables = {}
            if target.pdf_options:
                for key in ["main_font", "sans_font", "mono_font", "geometry"]:
                    value = target.pdf_options.get(key)
                    if value:
                        # Map to Pandoc variable names
                        var_name_map = {
                            "main_font": "mainfont",
                            "sans_font": "sansfont",
                            "mono_font": "monofont",
                            "geometry": "geometry",
                        }
                        variables[var_name_map.get(key, key)] = value

                # Handle mainfont_fallback
                fallback = target.pdf_options.get("mainfont_fallback")
                if fallback:
                    variables["mainfontfallback"] = fallback

            # Call legacy build_pdf
            success, error_msg = legacy_publisher.build_pdf(
                path=(
                    str(content_root)
                    if target.source_type == "folder"
                    else str(target.path)
                ),
                out=target.out,
                typ=target.source_type,
                use_summary=target.use_summary,
                use_book_json=target.use_book_json,
                keep_combined=target.keep_combined,
                publish_dir=str(target.out_dir),
                paper_format=target.pdf_options.get("paper_format", "a4"),
                summary_mode=target.summary_mode,
                summary_order_manifest=target.summary_order_manifest,
                summary_manual_marker=target.summary_manual_marker,
                summary_appendices_last=target.summary_appendices_last,
                resource_paths=None,  # TODO: Add asset paths
                emoji_options=emoji_options,
                variables=variables if variables else None,
            )

            output_path = target.out_dir / target.out if success else None

            if success:
                logger.info("✓ Target %d built successfully", target.index)
            else:
                logger.error("✗ Target %d build failed: %s", target.index, error_msg)

            return BuildResult(
                target=target,
                success=success,
                output_path=output_path,
                error_message=error_msg,
            )

        except Exception as exc:
            logger.exception("✗ Unexpected error building target %d", target.index)
            return BuildResult(
                target=target,
                success=False,
                output_path=None,
                error_message=f"Unexpected error: {exc}",
            )

    def build_all(self) -> List[BuildResult]:
        """Build all loaded publish targets.

        Returns:
            List of BuildResult objects (one per target)
        """
        if not self.targets:
            logger.warning("No targets to build")
            return []

        logger.info("Building %d target(s)...", len(self.targets))
        results: List[BuildResult] = []

        for target in self.targets:
            result = self.build_target(target)
            results.append(result)

        # Summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        logger.info("Build complete: %d succeeded, %d failed", successful, failed)

        return results

    def run(self) -> Tuple[int, int]:
        """Complete publishing workflow: prepare + build all.

        Returns:
            Tuple of (successful_count, failed_count)
        """
        # Prepare environment
        if not self.prepare_environment():
            logger.error("Environment preparation failed, aborting")
            return (0, len(self.targets))

        # Build all targets
        results = self.build_all()

        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        return (successful, failed)


def publish_from_manifest(
    manifest_path: Path | str,
    *,
    only_build: bool = True,
    no_apt: bool = False,
) -> Tuple[int, int]:
    """Convenience function to publish from manifest.

    Args:
        manifest_path: Path to publish.yml manifest
        only_build: If True, process only targets with build=True
        no_apt: If True, skip apt package installation

    Returns:
        Tuple of (successful_count, failed_count)

    Examples:
        >>> success, failed = publish_from_manifest("publish.yml")
        >>> print(f"Published: {success} succeeded, {failed} failed")
    """
    publisher = SmartPublisher(
        manifest_path,
        only_build=only_build,
        no_apt=no_apt,
    )
    return publisher.run()


__all__ = [
    "BuildResult",
    "SmartPublisher",
    "publish_from_manifest",
]
