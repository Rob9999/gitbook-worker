"""Robust content discovery tool for all publishing modes (GitBook, folder, file).

This module implements a smart content discovery system that:
1. Respects book.json configuration (root, structure.summary)
2. Falls back gracefully when book.json is not available
3. Handles all source types: folder with GitBook, folder without, single file
4. Uses the Smart Merge philosophy: prefer explicit config, fall back to convention

Usage:
    from tools.utils.content_discovery import discover_content

    # Discover content for a publish entry
    result = discover_content(
        path="./",
        source_type="folder",
        use_book_json=True,
        use_summary=True
    )

    # Access discovered paths
    print(f"Content root: {result.content_root}")
    print(f"Summary: {result.summary_path}")
    print(f"Markdown files: {result.markdown_files}")
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ContentDiscoveryResult:
    """Result of content discovery operation.

    Attributes:
        base_dir: The base directory (where book.json or publish.yml resides)
        content_root: The root directory containing markdown content
        summary_path: Path to SUMMARY.md (if exists)
        markdown_files: List of discovered markdown files
        book_json_path: Path to book.json (if exists)
        source_type: Detected or specified source type (file/folder)
        use_summary: Whether SUMMARY.md should be used for ordering
    """

    base_dir: Path
    content_root: Path
    summary_path: Optional[Path]
    markdown_files: List[Path]
    book_json_path: Optional[Path]
    source_type: str
    use_summary: bool


def _find_book_json(start_dir: Path) -> Optional[Path]:
    """Find book.json by walking up the directory tree.

    Args:
        start_dir: Starting directory for search

    Returns:
        Path to book.json if found, None otherwise
    """
    for candidate in [start_dir, *start_dir.parents]:
        book_path = candidate / "book.json"
        if book_path.exists():
            logger.debug("Found book.json at: %s", book_path)
            return book_path
    return None


def _read_book_json(book_path: Path) -> Dict[str, Any]:
    """Read and parse book.json.

    Args:
        book_path: Path to book.json file

    Returns:
        Parsed JSON data or empty dict on error
    """
    try:
        return json.loads(book_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Failed to parse book.json at %s: %s", book_path, exc)
        return {}


def _find_summary(
    root_dir: Path, structure_hint: Optional[str] = None
) -> Optional[Path]:
    """Find SUMMARY.md in content root.

    Args:
        root_dir: Directory to search in
        structure_hint: Optional hint from book.json structure.summary

    Returns:
        Path to SUMMARY.md if found, None otherwise
    """
    # Try hint from book.json first
    if structure_hint:
        candidate = root_dir / structure_hint
        if candidate.exists():
            logger.debug("Found SUMMARY via book.json hint: %s", candidate)
            return candidate

    # Try standard names (case-insensitive on Windows)
    for name in ("SUMMARY.md", "summary.md", "Summary.md"):
        candidate = root_dir / name
        if candidate.exists():
            logger.debug("Found SUMMARY by convention: %s", candidate)
            return candidate

    return None


def _collect_markdown_recursive(root_dir: Path) -> List[Path]:
    """Recursively collect all markdown files in directory.

    Args:
        root_dir: Root directory to start search

    Returns:
        List of markdown file paths
    """
    markdown_files: List[Path] = []

    if not root_dir.exists():
        logger.warning("Content root does not exist: %s", root_dir)
        return markdown_files

    # Prefer README.md at the top
    readme = root_dir / "README.md"
    if readme.exists():
        markdown_files.append(readme)

    # Collect all other .md and .markdown files
    for pattern in ("**/*.md", "**/*.markdown"):
        for file_path in sorted(root_dir.glob(pattern)):
            if file_path.is_file() and file_path not in markdown_files:
                markdown_files.append(file_path)

    logger.debug("Found %d markdown files in %s", len(markdown_files), root_dir)
    return markdown_files


def _extract_paths_from_summary(summary_path: Path, root_dir: Path) -> List[Path]:
    """Extract markdown file paths from SUMMARY.md.

    Args:
        summary_path: Path to SUMMARY.md
        root_dir: Root directory for resolving relative paths

    Returns:
        List of markdown file paths in order from SUMMARY.md
    """
    if not summary_path.exists():
        return []

    markdown_files: List[Path] = []
    # Match markdown links: [text](path.md) or [text](path.markdown)
    pattern = re.compile(r"\(([^)]+\.(?:md|markdown))\)", re.IGNORECASE)

    try:
        with summary_path.open("r", encoding="utf-8") as f:
            for line in f:
                for match in pattern.findall(line):
                    # Remove anchor/fragment (#section)
                    target = match.split("#", 1)[0].strip()

                    # Skip URLs
                    if target.startswith(("http://", "https://", "ftp://")):
                        continue

                    # Resolve path relative to root_dir
                    candidate = (root_dir / target).resolve()

                    # Check if file exists and has markdown extension
                    if candidate.exists() and candidate.suffix.lower() in {
                        ".md",
                        ".markdown",
                    }:
                        if candidate not in markdown_files:
                            markdown_files.append(candidate)
                    else:
                        logger.debug(
                            "SUMMARY.md references non-existent file: %s", target
                        )

    except Exception as exc:
        logger.warning("Failed to parse SUMMARY.md at %s: %s", summary_path, exc)
        return []

    logger.debug("Extracted %d files from SUMMARY.md", len(markdown_files))
    return markdown_files


def _normalize_source_type(
    source_type: Optional[str],
    path: Path,
) -> str:
    """Normalize source type to 'file' or 'folder'.

    Args:
        source_type: User-specified source type (may be empty/None)
        path: Path to analyze for auto-detection

    Returns:
        Normalized source type: 'file' or 'folder'
    """
    if source_type:
        normalized = source_type.strip().lower()
        if normalized in {"file", "folder"}:
            return normalized

    # Auto-detect based on path
    if path.is_file():
        return "file"
    elif path.is_dir():
        return "folder"

    # Default to folder if path doesn't exist yet
    return "folder"


def discover_content(
    *,
    path: str | Path,
    source_type: Optional[str] = None,
    use_book_json: bool = False,
    use_summary: bool = False,
    base_dir: Optional[Path] = None,
) -> ContentDiscoveryResult:
    """Discover content to publish using smart merge philosophy.

    This function implements the following discovery strategy:

    1. **Explicit Configuration First** (Smart Merge Priority 1)
       - If use_book_json=True, read book.json for root and structure
       - If use_summary=True, read SUMMARY.md for file ordering

    2. **Convention Over Configuration** (Smart Merge Priority 2)
       - Search for book.json in parent directories
       - Look for SUMMARY.md in standard locations (SUMMARY.md, summary.md)
       - Recursively collect all .md files if no SUMMARY

    3. **Graceful Fallback** (Smart Merge Priority 3)
       - If book.json not found, use path as content root
       - If SUMMARY.md not found, use alphabetical file order
       - Handle single-file mode seamlessly

    Args:
        path: Entry path from publish.yml (can be file or folder)
        source_type: Optional source type hint ('file', 'folder', or None for auto)
        use_book_json: Whether to respect book.json configuration
        use_summary: Whether to use SUMMARY.md for file ordering
        base_dir: Optional base directory (defaults to path parent or cwd)

    Returns:
        ContentDiscoveryResult with all discovered paths and metadata

    Examples:
        >>> # GitBook mode with book.json and SUMMARY.md
        >>> result = discover_content(
        ...     path="./",
        ...     source_type="folder",
        ...     use_book_json=True,
        ...     use_summary=True
        ... )
        >>> print(result.content_root)  # ./content (from book.json)

        >>> # Folder without GitBook (fallback mode)
        >>> result = discover_content(
        ...     path="./docs",
        ...     source_type="folder",
        ...     use_book_json=False,
        ...     use_summary=False
        ... )
        >>> print(result.content_root)  # ./docs (uses path directly)

        >>> # Single file mode
        >>> result = discover_content(
        ...     path="./README.md",
        ...     source_type="file"
        ... )
        >>> print(result.markdown_files)  # [Path('./README.md')]
    """
    # Step 1: Normalize input path
    path_obj = Path(path).resolve()

    # Determine base directory
    if base_dir is None:
        if path_obj.is_file():
            base_dir = path_obj.parent
        elif path_obj.is_dir():
            base_dir = path_obj
        else:
            base_dir = Path.cwd()
    base_dir = base_dir.resolve()

    # Normalize source type
    normalized_source_type = _normalize_source_type(source_type, path_obj)

    logger.debug("Content discovery started:")
    logger.debug("  path: %s", path_obj)
    logger.debug("  source_type: %s", normalized_source_type)
    logger.debug("  use_book_json: %s", use_book_json)
    logger.debug("  use_summary: %s", use_summary)
    logger.debug("  base_dir: %s", base_dir)

    # Step 2: Handle single file mode (early exit)
    if normalized_source_type == "file":
        if not path_obj.exists():
            logger.warning("Source file does not exist: %s", path_obj)
            return ContentDiscoveryResult(
                base_dir=base_dir,
                content_root=base_dir,
                summary_path=None,
                markdown_files=[],
                book_json_path=None,
                source_type="file",
                use_summary=False,
            )

        return ContentDiscoveryResult(
            base_dir=base_dir,
            content_root=path_obj.parent,
            summary_path=None,
            markdown_files=[path_obj],
            book_json_path=None,
            source_type="file",
            use_summary=False,
        )

    # Step 3: Folder mode - discover book.json (if enabled)
    book_json_path: Optional[Path] = None
    book_data: Dict[str, Any] = {}

    if use_book_json:
        book_json_path = _find_book_json(base_dir)
        if book_json_path:
            book_data = _read_book_json(book_json_path)
            # Update base_dir to where book.json was found
            base_dir = book_json_path.parent
            logger.debug("Using base_dir from book.json location: %s", base_dir)

    # Step 4: Determine content root
    content_root: Path

    if book_data and "root" in book_data:
        # Priority 1: Explicit root from book.json
        root_value = book_data["root"]
        content_root = (base_dir / root_value).resolve()
        logger.debug("Content root from book.json: %s", content_root)
    elif path_obj.is_dir():
        # Priority 2: Use provided path as content root
        content_root = path_obj
        logger.debug("Content root from provided path: %s", content_root)
    else:
        # Priority 3: Fallback to base directory
        content_root = base_dir
        logger.debug("Content root fallback to base_dir: %s", content_root)

    # Step 5: Find SUMMARY.md (if enabled)
    summary_path: Optional[Path] = None
    summary_hint: Optional[str] = None

    if use_summary:
        # Check if book.json specifies custom SUMMARY location
        structure = book_data.get("structure", {})
        if isinstance(structure, dict):
            summary_hint = structure.get("summary")

        summary_path = _find_summary(content_root, summary_hint)

        if summary_path:
            logger.info("Using SUMMARY.md for content ordering: %s", summary_path)
        else:
            logger.debug("No SUMMARY.md found, will use recursive collection")

    # Step 6: Collect markdown files
    markdown_files: List[Path] = []

    if use_summary and summary_path:
        # Priority 1: Extract files from SUMMARY.md
        markdown_files = _extract_paths_from_summary(summary_path, content_root)

        # Fallback: If SUMMARY.md is empty or invalid, use recursive collection
        if not markdown_files:
            logger.warning(
                "SUMMARY.md exists but contains no valid files, falling back to recursive collection"
            )
            markdown_files = _collect_markdown_recursive(content_root)
    else:
        # Priority 2: Recursive collection (fallback mode)
        markdown_files = _collect_markdown_recursive(content_root)

    # Step 7: Return result
    logger.info("Content discovery completed:")
    logger.info("  content_root: %s", content_root)
    logger.info("  summary_path: %s", summary_path or "None")
    logger.info("  markdown_files: %d found", len(markdown_files))

    return ContentDiscoveryResult(
        base_dir=base_dir,
        content_root=content_root,
        summary_path=summary_path,
        markdown_files=markdown_files,
        book_json_path=book_json_path,
        source_type=normalized_source_type,
        use_summary=use_summary and summary_path is not None,
    )


__all__ = [
    "ContentDiscoveryResult",
    "discover_content",
]
