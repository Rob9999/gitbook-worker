"""Smart publish target resolution and binding.

This module provides unified handling of publish.yml entries:
- Load and parse publish.yml manifest
- Resolve all publish targets with their configurations
- Bind book.json configuration to each publish target
- Filter targets by build flag
- Provide unified target dictionaries for processing

Migration from:
- publisher.py (get_publish_list, scattered manifest parsing)
- set_publish_flag.py (manifest loading)
- workflow_orchestrator (manifest resolution)

Smart Merge Philosophy:
1. Explicit: Use manifest configuration as provided
2. Convention: Auto-detect source_type, fill missing fields
3. Fallback: Provide sensible defaults for optional fields
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from tools.utils.smart_book import BookConfig, discover_book
from tools.utils.smart_manifest import resolve_manifest

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PublishTarget:
    """Unified publish target with resolved configuration.

    Attributes:
        index: Index in publish[] array (for tracking)
        path: Source path (file or folder)
        out: Output filename
        out_dir: Output directory (default: "publish")
        out_format: Output format (default: "pdf")
        source_type: Source type ("file" or "folder")
        source_format: Source format (default: "markdown")
        use_summary: Whether to use SUMMARY.md ordering
        use_book_json: Whether to respect book.json configuration
        keep_combined: Whether to keep combined markdown file
        summary_mode: Summary generation mode (e.g., "gitbook")
        summary_order_manifest: Path to summary order manifest
        summary_manual_marker: Marker for manual entries in summary
        summary_appendices_last: Whether to place appendices last
        reset_build_flag: Whether to reset build flag after build
        build: Current build flag status
        book_config: Resolved BookConfig (if use_book_json=True)
        assets: List of asset configurations
        pdf_options: PDF-specific options
        raw_entry: Original manifest entry
    """

    index: int
    path: Path
    out: str
    out_dir: Path
    out_format: str
    source_type: str
    source_format: str
    use_summary: bool
    use_book_json: bool
    keep_combined: bool
    summary_mode: Optional[str]
    summary_order_manifest: Optional[Path]
    summary_manual_marker: Optional[str]
    summary_appendices_last: bool
    reset_build_flag: bool
    build: bool
    book_config: Optional[BookConfig]
    assets: List[Dict[str, Any]] = field(default_factory=list)
    pdf_options: Dict[str, Any] = field(default_factory=dict)
    raw_entry: Dict[str, Any] = field(default_factory=dict)


def _as_bool(value: Any, default: bool = False) -> bool:
    """Convert value to boolean.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Boolean value
    """
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes", "y", "on")
    return default


def _normalize_source_type(
    source_type: Optional[str],
    path: Path,
) -> str:
    """Normalize source type to 'file' or 'folder'.

    Args:
        source_type: User-specified source type
        path: Path to analyze for auto-detection

    Returns:
        Normalized source type: 'file' or 'folder'
    """
    if source_type:
        normalized = source_type.strip().lower()
        if normalized in {"file", "folder"}:
            return normalized

    # Auto-detect based on path
    if path.exists():
        if path.is_file():
            return "file"
        elif path.is_dir():
            return "folder"

    # Default to folder if path doesn't exist yet
    return "folder"


def _parse_assets(raw_assets: Any) -> List[Dict[str, Any]]:
    """Parse assets configuration from manifest entry.

    Args:
        raw_assets: Raw assets value from manifest

    Returns:
        List of asset dictionaries
    """
    assets: List[Dict[str, Any]] = []

    if not isinstance(raw_assets, list):
        return assets

    for raw_asset in raw_assets:
        if isinstance(raw_asset, dict):
            path_value = raw_asset.get("path")
            if not path_value:
                continue
            assets.append(
                {
                    "path": str(path_value),
                    "type": str(raw_asset.get("type") or "").strip() or None,
                    "copy_to_output": _as_bool(raw_asset.get("copy_to_output")),
                }
            )
        elif raw_asset:
            assets.append(
                {
                    "path": str(raw_asset),
                    "type": None,
                    "copy_to_output": False,
                }
            )

    return assets


def _parse_pdf_options(raw_options: Any) -> Dict[str, Any]:
    """Parse PDF options from manifest entry.

    Args:
        raw_options: Raw pdf_options value from manifest

    Returns:
        Dictionary of PDF options
    """
    if not isinstance(raw_options, dict):
        return {}

    return {
        "emoji_color": _as_bool(raw_options.get("emoji_color"), default=True),
        "main_font": raw_options.get("main_font"),
        "sans_font": raw_options.get("sans_font"),
        "mono_font": raw_options.get("mono_font"),
        "mainfont_fallback": raw_options.get("mainfont_fallback"),
        "geometry": raw_options.get("geometry"),
        "paper_format": raw_options.get("paper_format"),
    }


def _resolve_target(
    index: int,
    entry: Dict[str, Any],
    manifest_dir: Path,
) -> Optional[PublishTarget]:
    """Resolve a single publish target from manifest entry.

    Args:
        index: Index in publish[] array
        entry: Raw manifest entry
        manifest_dir: Directory containing manifest

    Returns:
        Resolved PublishTarget or None if invalid
    """
    # Required fields
    path_value = entry.get("path")
    out_value = entry.get("out")

    if not path_value or not out_value:
        logger.warning(
            "Skipping publish target %d: missing 'path' or 'out' field", index
        )
        return None

    # Resolve path (absolute or relative to manifest)
    path_obj = Path(path_value)
    if not path_obj.is_absolute():
        path_obj = (manifest_dir / path_obj).resolve()
    else:
        path_obj = path_obj.resolve()

    # Resolve output directory
    out_dir_value = entry.get("out_dir")
    if out_dir_value:
        out_dir = Path(out_dir_value)
        if not out_dir.is_absolute():
            out_dir = (manifest_dir / out_dir).resolve()
    else:
        out_dir = manifest_dir / "publish"

    # Extract configuration
    source_type_raw = str(entry.get("source_type") or entry.get("type") or "").strip()
    source_type = _normalize_source_type(source_type_raw, path_obj)

    out_format = str(entry.get("out_format", "pdf") or "pdf").lower()
    source_format = str(entry.get("source_format", "markdown") or "markdown").lower()

    use_summary = _as_bool(entry.get("use_summary"))
    use_book_json = _as_bool(entry.get("use_book_json"))
    keep_combined = _as_bool(entry.get("keep_combined"))
    summary_appendices_last = _as_bool(entry.get("summary_appendices_last"))
    reset_build_flag = _as_bool(entry.get("reset_build_flag"))
    build = _as_bool(entry.get("build"), default=False)

    summary_mode = entry.get("summary_mode")
    summary_manual_marker = entry.get("summary_manual_marker")

    # Resolve summary order manifest
    summary_order_manifest: Optional[Path] = None
    som_value = entry.get("summary_order_manifest")
    if som_value:
        som_path = Path(som_value)
        if not som_path.is_absolute():
            summary_order_manifest = (manifest_dir / som_path).resolve()
        else:
            summary_order_manifest = som_path

    # Parse assets and PDF options
    assets = _parse_assets(entry.get("assets"))
    pdf_options = _parse_pdf_options(entry.get("pdf_options"))

    # Discover book.json configuration if requested
    book_config: Optional[BookConfig] = None
    if use_book_json and source_type == "folder":
        try:
            book_config = discover_book(path_obj, search_parents=True)
            logger.debug(
                "Target %d: Discovered book.json: %s",
                index,
                book_config.book_json_path or "Not found",
            )
        except Exception as exc:
            logger.warning("Target %d: Failed to discover book.json: %s", index, exc)

    return PublishTarget(
        index=index,
        path=path_obj,
        out=str(out_value),
        out_dir=out_dir,
        out_format=out_format,
        source_type=source_type,
        source_format=source_format,
        use_summary=use_summary,
        use_book_json=use_book_json,
        keep_combined=keep_combined,
        summary_mode=summary_mode,
        summary_order_manifest=summary_order_manifest,
        summary_manual_marker=summary_manual_marker,
        summary_appendices_last=summary_appendices_last,
        reset_build_flag=reset_build_flag,
        build=build,
        book_config=book_config,
        assets=assets,
        pdf_options=pdf_options,
        raw_entry=entry,
    )


def load_publish_targets(
    manifest_path: Path | str,
    *,
    only_build: bool = False,
) -> List[PublishTarget]:
    """Load all publish targets from manifest.

    Args:
        manifest_path: Path to publish.yml manifest
        only_build: If True, return only targets with build=True

    Returns:
        List of resolved PublishTarget objects

    Examples:
        >>> # Load all targets
        >>> targets = load_publish_targets("publish.yml")
        >>> for target in targets:
        ...     print(f"{target.path} -> {target.out}")

        >>> # Load only targets marked for build
        >>> targets = load_publish_targets("publish.yml", only_build=True)
        >>> print(f"Building {len(targets)} targets")
    """
    manifest_path_obj = Path(manifest_path).resolve()

    if not manifest_path_obj.exists():
        logger.error("Manifest not found: %s", manifest_path_obj)
        return []

    # Load and parse manifest
    try:
        content = manifest_path_obj.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
    except Exception as exc:
        logger.error("Failed to parse manifest %s: %s", manifest_path_obj, exc)
        return []

    if not isinstance(data, dict):
        logger.error("Manifest is not a YAML dictionary: %s", manifest_path_obj)
        return []

    manifest_dir = manifest_path_obj.parent
    publish_entries = data.get("publish", [])

    if not isinstance(publish_entries, list):
        logger.warning("Manifest 'publish' field is not a list")
        return []

    # Resolve all targets
    targets: List[PublishTarget] = []

    for index, entry in enumerate(publish_entries):
        if not isinstance(entry, dict):
            logger.warning("Publish entry %d is not a dictionary", index)
            continue

        target = _resolve_target(index, entry, manifest_dir)
        if target is None:
            continue

        # Filter by build flag if requested
        if only_build and not target.build:
            continue

        targets.append(target)

    logger.info(
        "Loaded %d publish target(s) from %s%s",
        len(targets),
        manifest_path_obj.name,
        " (filtered by build=true)" if only_build else "",
    )

    return targets


def get_buildable_targets(manifest_path: Path | str) -> List[PublishTarget]:
    """Get all publish targets marked for build.

    Convenience function that filters targets by build=True.

    Args:
        manifest_path: Path to publish.yml manifest

    Returns:
        List of targets with build=True

    Examples:
        >>> targets = get_buildable_targets("publish.yml")
        >>> if not targets:
        ...     print("Nothing to build")
    """
    return load_publish_targets(manifest_path, only_build=True)


def find_target_by_path(
    targets: List[PublishTarget],
    path: Path | str,
) -> Optional[PublishTarget]:
    """Find publish target by path.

    Args:
        targets: List of publish targets
        path: Path to search for

    Returns:
        Matching PublishTarget or None if not found
    """
    search_path = Path(path).resolve()

    for target in targets:
        if target.path == search_path:
            return target

    return None


def get_target_content_root(target: PublishTarget) -> Path:
    """Get effective content root for a publish target.

    Returns the content root from book.json if available,
    otherwise returns the target path.

    Args:
        target: PublishTarget to analyze

    Returns:
        Effective content root directory

    Examples:
        >>> target = targets[0]
        >>> root = get_target_content_root(target)
        >>> print(root)  # ./content (if book.json exists)
    """
    if target.book_config:
        return target.book_config.content_root
    elif target.source_type == "folder":
        return target.path
    else:
        # File type - return parent directory
        return target.path.parent


__all__ = [
    "PublishTarget",
    "load_publish_targets",
    "get_buildable_targets",
    "find_target_by_path",
    "get_target_content_root",
]
