"""Smart publish flag management with book.json awareness.

This module provides unified flag management for publish.yml entries:
- Set flags based on git changes (replaces set_publish_flag.py)
- Reset flags for specific targets (replaces reset_publish_flag.py)
- Book.json aware path matching via smart_publish_target
- Smart Merge integration for content root resolution

Migration from:
- tools/publishing/set_publish_flag.py
- tools/publishing/reset_publish_flag.py

Smart Merge Philosophy:
1. Explicit: Use content_root from book.json if available
2. Convention: Match against entry path if no book.json
3. Fallback: Graceful degradation for missing resources
"""

from __future__ import annotations

import json
import logging
import os
import posixpath
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from tools.logging_config import get_logger
from tools.utils.smart_git import get_changed_files as git_get_changed_files
from tools.utils.smart_git import normalize_posix
from tools.utils.smart_manifest import (
    SmartManifestError,
    detect_repo_root,
    resolve_manifest,
)
from tools.utils.smart_publish_target import (
    get_target_content_root,
    load_publish_targets,
)

logger = get_logger(__name__)


# ============================================================================
# Common Utilities
# ============================================================================


def find_publish_file(explicit: Optional[str] = None) -> Path:
    """Find publish.yml manifest using smart resolution.

    Args:
        explicit: Optional explicit path to manifest

    Returns:
        Resolved path to publish.yml

    Raises:
        SystemExit: If manifest cannot be found
    """
    cwd = Path.cwd()
    repo_root = detect_repo_root(cwd)
    try:
        manifest_path = resolve_manifest(
            explicit=explicit, cwd=cwd, repo_root=repo_root
        )
    except SmartManifestError as exc:
        logger.error(str(exc))
        raise SystemExit(3) from exc
    return manifest_path


def load_publish_manifest(publish_path: Path) -> Dict[str, Any]:
    """Load publish.yml manifest.

    Args:
        publish_path: Path to publish.yml

    Returns:
        Parsed manifest data

    Raises:
        SystemExit: If manifest is invalid
    """
    with open(publish_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if "publish" not in data or not isinstance(data["publish"], list):
        logger.error(
            "Ungültiges publish.yaml-Format: Top-Level-Schlüssel 'publish' (Liste) fehlt."
        )
        raise SystemExit(5)
    return data


def save_publish_manifest(publish_path: Path, data: Dict[str, Any]) -> None:
    """Save publish.yml manifest.

    Args:
        publish_path: Path to publish.yml
        data: Manifest data to save
    """
    with open(publish_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


# ============================================================================
# Set Publish Flags (Git-based)
# ============================================================================


def get_entry_type(entry: Dict[str, Any]) -> str:
    """Extract and normalize source_type from entry.

    Args:
        entry: Publish entry dictionary

    Returns:
        Normalized source type ("file", "folder", "auto")
    """
    value = entry.get("source_type") or entry.get("type") or "auto"
    if isinstance(value, str):
        return value.strip().lower()
    return str(value).strip().lower()


def resolve_entry_path(entry_path: str, manifest_dir: Path, repo_root: Path) -> str:
    """Resolve entry path relative to repository root.

    Args:
        entry_path: Path from publish entry
        manifest_dir: Directory containing manifest
        repo_root: Repository root directory

    Returns:
        Normalized path relative to repo root
    """
    full_entry_path = os.path.normpath(os.path.join(manifest_dir, entry_path))
    try:
        rel_path = os.path.relpath(full_entry_path, repo_root)
    except ValueError:
        rel_path = full_entry_path
    return normalize_posix(rel_path)


def is_path_match(
    entry_path: str,
    entry_type: str,
    changed_file: str,
    content_root: Optional[str] = None,
) -> bool:
    """Check if changed file matches publish entry.

    Uses content_root from book.json if available (Smart Merge).

    Args:
        entry_path: Original entry path from publish.yml
        entry_type: Type of entry ("file", "folder", "auto")
        changed_file: Changed file path from git
        content_root: Optional content root from book.json

    Returns:
        True if file matches entry, False otherwise
    """
    # Use content_root if provided (from book.json), otherwise use entry_path
    match_path = content_root if content_root else entry_path

    ep = normalize_posix(match_path)
    cf = normalize_posix(changed_file)

    # Handle root path explicitly (. or ./ or empty)
    if ep in (".", ""):
        # Root path matches everything
        return True

    if entry_type == "folder":
        # Match if file is in folder (or is the folder itself)
        return cf == ep or cf.startswith(ep + "/")
    elif entry_type == "file":
        return cf == ep
    else:
        # "auto": heuristic - folder if no extension and is directory
        last = posixpath.basename(ep)
        if os.path.isdir(ep) or (("." not in last) and not posixpath.splitext(last)[1]):
            return cf == ep or cf.startswith(ep + "/")
        return cf == ep


def set_publish_flags(
    *,
    manifest_path: Optional[Path] = None,
    commit: str = "HEAD",
    base: Optional[str] = None,
    reset_others: bool = False,
    dry_run: bool = False,
    debug: bool = False,
) -> Dict[str, Any]:
    """Set build flags based on git changes.

    This is the main function for setting publish flags. It:
    1. Loads publish targets using smart_publish_target
    2. Gets changed files from git
    3. Matches files against targets (using book.json content_root)
    4. Updates build flags accordingly

    Args:
        manifest_path: Path to publish.yml (auto-detected if None)
        commit: Target commit SHA (default: HEAD)
        base: Base commit for comparison (optional)
        reset_others: Set non-matching entries to build=false
        dry_run: Don't write changes
        debug: Enable debug logging

    Returns:
        Dictionary with results (changed_files, modified_entries, etc.)
    """
    if debug:
        logger.setLevel(logging.DEBUG)

    # Find manifest
    if manifest_path is None:
        manifest_path = find_publish_file(None)
    else:
        manifest_path = Path(manifest_path).resolve()

    manifest_dir = manifest_path.parent
    repo_root = detect_repo_root(manifest_dir)

    # Get changed files using smart_git
    changed_files = git_get_changed_files(commit, base)
    if debug:
        logger.debug("Changed files (%d):", len(changed_files))
        for c in changed_files:
            logger.debug("  - %s", c)

    # Load targets using smart module
    try:
        targets = load_publish_targets(manifest_path, only_build=False)
        logger.info(
            "Loaded %d publish target(s) using smart_publish_target", len(targets)
        )
    except Exception as exc:
        logger.error("Failed to load targets with smart module: %s", exc)
        logger.info("Falling back to legacy manifest loading")
        targets = []

    # Load manifest data
    data = load_publish_manifest(manifest_path)
    entries = data["publish"]

    touched_entries = []
    for idx, entry in enumerate(entries):
        ep = entry.get("path")
        etype = get_entry_type(entry)
        if not ep:
            logger.warning("publish[%d] ohne 'path' – übersprungen.", idx)
            continue

        # Try to get content root from smart target
        content_root_path = None
        if idx < len(targets):
            target = targets[idx]
            try:
                content_root = get_target_content_root(target)
                # Convert to relative path for matching
                try:
                    content_root_path = normalize_posix(
                        os.path.relpath(content_root, repo_root)
                    )
                    logger.debug(
                        "Target %d: Using content_root=%s (from book.json: %s)",
                        idx,
                        content_root_path,
                        target.book_config is not None,
                    )
                except ValueError:
                    # Paths on different drives on Windows
                    content_root_path = None
            except Exception as exc:
                logger.debug("Failed to get content_root for target %d: %s", idx, exc)

        resolved_ep = resolve_entry_path(ep, manifest_dir, repo_root)

        # Use content_root_path for matching if available (book.json aware)
        hit = any(
            is_path_match(resolved_ep, etype, cf, content_root=content_root_path)
            for cf in changed_files
        )

        # Update build flag
        old_build = bool(entry.get("build", False))
        new_build = True if hit else (False if reset_others else old_build)

        if old_build != new_build:
            entry["build"] = new_build
            touched_entries.append(
                {"path": ep, "type": etype, "from": old_build, "to": new_build}
            )
        else:
            # Ensure build key exists
            entry["build"] = new_build

    # Prepare outputs
    outputs = {
        "changed_files": changed_files,
        "modified_entries": touched_entries,
        "any_build_true": any(e.get("build", False) for e in entries),
    }

    # Write changes
    if dry_run:
        logger.info("[DRY-RUN] Änderungen würden geschrieben werden.")
    else:
        save_publish_manifest(manifest_path, data)

    # Log results
    logger.info("publish file: %s", manifest_path)
    logger.info(
        "commit: %s%s",
        commit,
        f" | base: {base}" if base else "",
    )
    if touched_entries:
        logger.info("geänderte build-Flags:")
        for t in touched_entries:
            logger.info(
                "  - %s (%s): %s -> %s", t["path"], t["type"], t["from"], t["to"]
            )
    else:
        logger.info("keine build-Flag-Änderungen.")

    # Write GitHub Actions outputs
    gh_out = os.getenv("GITHUB_OUTPUT")
    if gh_out:
        try:
            with open(gh_out, "a", encoding="utf-8") as f:
                f.write(f"any_build_true={str(outputs['any_build_true']).lower()}\n")
                f.write(f"modified_count={len(touched_entries)}\n")
        except Exception as e:
            logger.warning("Konnte GITHUB_OUTPUT nicht schreiben: %s", e)

    return outputs


# ============================================================================
# Reset Publish Flags (Target-based)
# ============================================================================


def match_target_indices(
    entries: List[Dict[str, Any]],
    *,
    path: Optional[str] = None,
    out: Optional[str] = None,
    index: Optional[int] = None,
    debug: bool = False,
) -> List[int]:
    """Find indices of entries matching given criteria.

    Args:
        entries: List of publish entries
        path: Path to match (optional)
        out: Output filename to match (optional)
        index: Explicit index to match (optional)
        debug: Enable debug logging

    Returns:
        List of matching indices
    """
    hits: List[int] = []
    for i, e in enumerate(entries):
        if index is not None and i == index:
            hits.append(i)
            continue
        if path is not None and str(e.get("path", "")).strip() == path:
            hits.append(i)
            continue
        if out is not None and str(e.get("out", "")).strip() == out:
            hits.append(i)
            continue

    if debug:
        logger.debug(
            "Match-Kandidaten (path=%r, out=%r, index=%s): %s", path, out, index, hits
        )
    return sorted(set(hits))


def reset_publish_flags(
    *,
    manifest_path: Optional[Path] = None,
    path: Optional[str] = None,
    out: Optional[str] = None,
    index: Optional[int] = None,
    multi: bool = False,
    error_on_no_match: bool = False,
    dry_run: bool = False,
    debug: bool = False,
) -> Dict[str, Any]:
    """Reset build flags for specific targets.

    Args:
        manifest_path: Path to publish.yml (auto-detected if None)
        path: Match by path field
        out: Match by out field
        index: Match by explicit index (0-based)
        multi: Allow multiple matches (default: error if >1)
        error_on_no_match: Raise error if no matches found
        dry_run: Don't write changes
        debug: Enable debug logging

    Returns:
        Dictionary with results (reset_count, matched_indices, etc.)

    Raises:
        SystemExit: If criteria invalid or multiple matches without --multi
    """
    if debug:
        logger.setLevel(logging.DEBUG)

    if path is None and out is None and index is None:
        logger.error("Bitte --path, --out oder --index angeben.")
        raise SystemExit(1)

    # Find manifest
    if manifest_path is None:
        manifest_path = find_publish_file(None)
    else:
        manifest_path = Path(manifest_path).resolve()

    # Load manifest
    data = load_publish_manifest(manifest_path)
    entries: List[Dict[str, Any]] = data["publish"]

    # Validate index bounds
    if index is not None and (index < 0 or index >= len(entries)):
        logger.error(
            "--index %s liegt außerhalb des Bereichs [0..%d].",
            index,
            len(entries) - 1,
        )
        raise SystemExit(6)

    # Find matching entries
    matches = match_target_indices(
        entries, path=path, out=out, index=index, debug=debug
    )

    if not matches:
        msg = "Kein publish-Eintrag gefunden, der den Kriterien entspricht."
        if error_on_no_match:
            logger.error(msg)
            raise SystemExit(7)
        else:
            logger.info(msg)
            return {
                "reset_count": 0,
                "matched_indices": [],
                "matched_paths": [],
                "matched_outs": [],
                "changed": [],
            }

    if len(matches) > 1 and not multi:
        logger.error(
            "Mehrere Einträge passen %s, aber --multi wurde nicht gesetzt.", matches
        )
        raise SystemExit(8)

    # Reset flags
    changed: List[Dict[str, Any]] = []
    for i in matches:
        entry = entries[i]
        before = bool(entry.get("build", False))
        after = False
        if before != after:
            entry["build"] = after
            changed.append(
                {
                    "index": i,
                    "path": entry.get("path"),
                    "out": entry.get("out"),
                    "from": before,
                    "to": after,
                }
            )
        else:
            # Ensure key exists
            entry["build"] = False

    # Write changes
    if dry_run:
        logger.info("[DRY-RUN] Änderungen würden geschrieben werden.")
    else:
        save_publish_manifest(manifest_path, data)

    # Log results
    logger.info("publish file: %s", manifest_path)
    if changed:
        logger.info("zurückgesetzte build-Flags:")
        for c in changed:
            logger.info(
                "  - index=%s path=%s out=%s : %s -> %s",
                c["index"],
                c.get("path"),
                c.get("out"),
                c["from"],
                c["to"],
            )
    else:
        logger.info("Keine tatsächlichen Änderungen (build war bereits false).")

    # Prepare outputs
    outputs = {
        "reset_count": len(matches),
        "matched_indices": matches,
        "matched_paths": [entries[i].get("path") for i in matches],
        "matched_outs": [entries[i].get("out") for i in matches],
        "changed": changed,
    }

    # Write GitHub Actions outputs
    gh_out = os.getenv("GITHUB_OUTPUT")
    if gh_out:
        try:
            with open(gh_out, "a", encoding="utf-8") as f:
                f.write(f"reset_count={outputs['reset_count']}\n")
                f.write(
                    f"matched_indices={json.dumps(outputs['matched_indices'], ensure_ascii=False)}\n"
                )
                f.write(
                    f"matched_paths={json.dumps(outputs['matched_paths'], ensure_ascii=False)}\n"
                )
                f.write(
                    f"matched_outs={json.dumps(outputs['matched_outs'], ensure_ascii=False)}\n"
                )
                f.write(
                    f"changed={json.dumps(outputs['changed'], ensure_ascii=False)}\n"
                )
        except Exception as e:
            logger.warning("Konnte GITHUB_OUTPUT nicht schreiben: %s", e)

    return outputs


__all__ = [
    # Main functions
    "set_publish_flags",
    "reset_publish_flags",
    # Utilities
    "find_publish_file",
    "load_publish_manifest",
    "save_publish_manifest",
    "get_entry_type",
    "resolve_entry_path",
    "is_path_match",
    "match_target_indices",
]
