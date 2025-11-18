"""Smart book.json discovery and content root resolution.

This module provides unified handling of GitBook book.json files:
- Find book.json in parent directories
- Parse and validate book.json structure
- Resolve content root directory from book.json configuration
- Provide fallback behavior when book.json is missing

Migration from:
- gitbook_style.py (_find_book_base, _build_summary_context)
- publisher.py (scattered book.json logic)
- content_discovery.py (book.json handling)

Smart Merge Philosophy:
1. Explicit: Use provided book.json path if given
2. Convention: Search parent directories for book.json
3. Fallback: Use base_dir directly if no book.json found
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BookConfig:
    """Resolved GitBook configuration from book.json.

    Attributes:
        book_json_path: Path to book.json file (None if not found)
        base_dir: Directory containing book.json (or fallback dir)
        content_root: Resolved root directory for markdown content
        summary_filename: Filename for summary (from structure.summary)
        summary_path: Full path to SUMMARY.md (if exists)
        title: Book title from book.json
        language: Book language from book.json
        data: Raw book.json data dictionary
    """

    book_json_path: Optional[Path]
    base_dir: Path
    content_root: Path
    summary_filename: Optional[str]
    summary_path: Optional[Path]
    title: Optional[str]
    language: Optional[str]
    data: Dict[str, Any]


def _read_book_json(book_path: Path) -> Dict[str, Any]:
    """Read and parse book.json file.

    Args:
        book_path: Path to book.json file

    Returns:
        Parsed JSON data or empty dict on error
    """
    if not book_path.exists():
        return {}

    try:
        content = book_path.read_text(encoding="utf-8")
        data = json.loads(content)
        if not isinstance(data, dict):
            logger.warning("book.json at %s is not a JSON object", book_path)
            return {}
        return data
    except json.JSONDecodeError as exc:
        logger.warning("Failed to parse book.json at %s: %s", book_path, exc)
        return {}
    except Exception as exc:
        logger.warning("Error reading book.json at %s: %s", book_path, exc)
        return {}


def _find_book_json(start_dir: Path) -> Optional[Path]:
    """Find book.json by walking up directory tree.

    Args:
        start_dir: Starting directory for search

    Returns:
        Path to book.json if found, None otherwise
    """
    current = start_dir.resolve()

    # Search in current directory and all parents
    for candidate_dir in [current, *current.parents]:
        book_path = candidate_dir / "book.json"
        if book_path.exists():
            logger.debug("Found book.json at: %s", book_path)
            return book_path

    logger.debug("No book.json found starting from: %s", start_dir)
    return None


def _resolve_content_root(
    base_dir: Path,
    book_data: Dict[str, Any],
) -> Path:
    """Resolve content root directory from book.json.

    Args:
        base_dir: Directory containing book.json
        book_data: Parsed book.json data

    Returns:
        Resolved content root directory
    """
    # Check for root field in book.json
    root_value = book_data.get("root")

    if root_value:
        # Normalize root value (remove leading/trailing slashes for relative paths)
        root_str = str(root_value).strip()
        if root_str:
            root_path = Path(root_str)
            # If already absolute, use as-is; otherwise resolve relative to base_dir
            if root_path.is_absolute():
                content_root = root_path.resolve()
                logger.debug("Content root from book.json (absolute): %s", content_root)
            else:
                # Strip leading/trailing slashes for relative paths
                root_str = root_str.strip("/").strip("\\")
                content_root = (base_dir / root_str).resolve()
                logger.debug("Content root from book.json (relative): %s", content_root)
            return content_root

    # Fallback: use base_dir directly
    logger.debug("No root specified in book.json, using base_dir: %s", base_dir)
    return base_dir


def _find_summary_file(
    content_root: Path,
    structure_hint: Optional[str] = None,
) -> Optional[Path]:
    """Find SUMMARY.md in content root.

    Args:
        content_root: Directory to search for SUMMARY.md
        structure_hint: Optional hint from book.json structure.summary

    Returns:
        Path to SUMMARY.md if found, None otherwise
    """
    # Try hint from book.json first
    if structure_hint:
        candidate = content_root / structure_hint
        if candidate.exists() and candidate.is_file():
            logger.debug("Found SUMMARY via book.json hint: %s", candidate)
            return candidate

    # Try standard names (case-insensitive on Windows)
    for name in ("SUMMARY.md", "summary.md", "Summary.md"):
        candidate = content_root / name
        if candidate.exists() and candidate.is_file():
            logger.debug("Found SUMMARY by convention: %s", candidate)
            return candidate

    logger.debug("No SUMMARY.md found in: %s", content_root)
    return None


def discover_book(
    path: Path | str,
    *,
    search_parents: bool = True,
) -> BookConfig:
    """Discover and parse GitBook configuration.

    This is the main entry point for book.json discovery. It implements
    the Smart Merge philosophy:

    1. **Explicit**: If path points to book.json, use it directly
    2. **Convention**: Search parent directories for book.json
    3. **Fallback**: Return config with no book.json if not found

    Args:
        path: Starting path (directory or book.json file)
        search_parents: Whether to search parent directories (default: True)

    Returns:
        BookConfig with resolved paths and configuration

    Examples:
        >>> # Standard GitBook discovery
        >>> config = discover_book(Path("./my-book"))
        >>> print(config.content_root)  # ./my-book/content (from book.json)

        >>> # Fallback when no book.json
        >>> config = discover_book(Path("./plain-folder"))
        >>> print(config.content_root)  # ./plain-folder (no book.json)

        >>> # Direct book.json path
        >>> config = discover_book(Path("./book.json"))
        >>> print(config.base_dir)  # ./ (directory containing book.json)
    """
    path_obj = Path(path).resolve()

    # Determine starting directory
    if path_obj.is_file() and path_obj.name == "book.json":
        # Direct path to book.json
        book_json_path = path_obj
        base_dir = path_obj.parent
    elif path_obj.is_dir():
        # Directory - search for book.json
        if search_parents:
            book_json_path = _find_book_json(path_obj)
        else:
            candidate = path_obj / "book.json"
            book_json_path = candidate if candidate.exists() else None

        base_dir = book_json_path.parent if book_json_path else path_obj
    else:
        # Path doesn't exist - use parent directory
        logger.warning("Path does not exist: %s", path_obj)
        base_dir = path_obj.parent if path_obj.parent.exists() else Path.cwd()
        book_json_path = None

    # Parse book.json if found
    book_data: Dict[str, Any] = {}
    if book_json_path:
        book_data = _read_book_json(book_json_path)

    # Resolve content root
    content_root = _resolve_content_root(base_dir, book_data)

    # Extract summary filename from structure.summary
    structure = book_data.get("structure", {})
    summary_filename: Optional[str] = None
    if isinstance(structure, dict):
        summary_hint = structure.get("summary")
        if summary_hint:
            summary_filename = str(summary_hint).strip()

    # Find SUMMARY.md file
    summary_path = _find_summary_file(content_root, summary_filename)

    # Extract title and language
    title = book_data.get("title")
    if title:
        title = str(title).strip() or None

    language = book_data.get("language")
    if language:
        language = str(language).strip() or None

    logger.info("Book discovery completed:")
    logger.info("  book.json: %s", book_json_path or "Not found")
    logger.info("  base_dir: %s", base_dir)
    logger.info("  content_root: %s", content_root)
    logger.info("  summary: %s", summary_path or "Not found")

    return BookConfig(
        book_json_path=book_json_path,
        base_dir=base_dir,
        content_root=content_root,
        summary_filename=summary_filename,
        summary_path=summary_path,
        title=title,
        language=language,
        data=book_data,
    )


def get_content_root(
    path: Path | str,
    *,
    search_parents: bool = True,
) -> Path:
    """Get content root directory for a GitBook project.

    Convenience function that returns only the content root path.

    Args:
        path: Starting path (directory or book.json file)
        search_parents: Whether to search parent directories

    Returns:
        Resolved content root directory

    Examples:
        >>> root = get_content_root(Path("./"))
        >>> print(root)  # ./content (if book.json exists with root: "content/")
    """
    config = discover_book(path, search_parents=search_parents)
    return config.content_root


def has_book_json(path: Path | str) -> bool:
    """Check if a book.json exists for the given path.

    Args:
        path: Path to check

    Returns:
        True if book.json exists, False otherwise

    Examples:
        >>> if has_book_json("./"):
        ...     print("GitBook project detected")
    """
    path_obj = Path(path).resolve()

    if path_obj.is_file() and path_obj.name == "book.json":
        return path_obj.exists()

    if path_obj.is_dir():
        return (path_obj / "book.json").exists()

    return False


__all__ = [
    "BookConfig",
    "discover_book",
    "get_content_root",
    "has_book_json",
]
