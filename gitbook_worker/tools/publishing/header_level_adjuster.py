"""Utilities to adjust heading levels when combining Markdown files.

Specification: "Per document apply the header level dictated by SUMMARY.md
(or content discovery). Shift the entire in-document heading cascade upward
or downward while keeping relative heading structure intact."

The adjustment can be driven either by a caller-provided ``target_level``
or, as a fallback, by the parent README heuristic (``parent_level + 1``).
YAML frontmatter and fenced code blocks are skipped to avoid corrupting
metadata or code samples.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional


def _first_heading_level(lines: Iterable[str]) -> Optional[int]:
    """Return the level of the first ATX heading outside fences/frontmatter."""

    in_frontmatter = False
    frontmatter_done = False
    in_fence = False
    fence_marker = ""

    for raw in lines:
        line = raw.rstrip("\n")

        if not frontmatter_done and line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            in_frontmatter = False
            frontmatter_done = True
            continue

        if in_frontmatter:
            continue

        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif stripped.startswith(fence_marker):
                in_fence = False
                fence_marker = ""
            continue

        if in_fence:
            continue

        if stripped.startswith("#"):
            hashes = stripped.split()[0]
            level = len(hashes)
            if level > 0:
                return level

    return None


def _first_heading_level_from_file(path: Path) -> Optional[int]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return _first_heading_level(handle.readlines())
    except OSError:
        return None


def _find_readme_level(
    folder: Path, *, exclude: Optional[Path] = None
) -> Optional[int]:
    """Return the first heading level from a README in ``folder``.

    Skips the ``exclude`` path to avoid self-referencing when the document
    being processed *is* the README in that folder.
    """

    for candidate in (folder / "README.md", folder / "readme.md"):
        if exclude and candidate.resolve() == exclude.resolve():
            continue
        level = _first_heading_level_from_file(candidate)
        if level:
            return level
    return None


def _find_parent_readme_level(md_path: Path) -> Optional[int]:
    """Find an appropriate parent heading level for ``md_path``.

    - For regular files: use the README in the same folder (excluding the file
      itself, in case it *is* that README).
    - For README files: try the parent's README; if absent, do not adjust.
    """

    parent = md_path.parent

    # If the document itself is a README, avoid self-reference and look one
    # level up. This prevents shifting top-level sections downward.
    if md_path.name.lower() == "readme.md":
        grandparent = parent.parent if parent else None
        if grandparent:
            return _find_readme_level(grandparent)
        return None

    return _find_readme_level(parent, exclude=md_path)


def adjust_headings_for_inclusion(
    content: str, source_path: Path, *, target_level: int | None = None
) -> str:
    """Shift heading levels while keeping intra-document hierarchy intact.

    When ``target_level`` is provided, headings are shifted by a constant
    offset so that the first heading becomes ``target_level``. If omitted,
    the parent README heuristic is used and only downward adjustments are
    applied (i.e. headings are made deeper, not shallower).
    """

    lines = content.splitlines(keepends=True)
    current_level = _first_heading_level(lines)
    if current_level is None:
        return content

    if target_level is None:
        # Do not auto-adjust README files when no explicit target is given; they
        # usually represent the entry point for their directory.
        if source_path.name.lower() == "readme.md":
            return content

        parent_level = _find_parent_readme_level(source_path)
        if parent_level is None:
            return content

        target_level = parent_level + 1
        delta = target_level - current_level
        # Only deepen headings; never flatten or lift already-nested content.
        if delta <= 0:
            return content
    else:
        delta = target_level - current_level
        if delta == 0:
            return content

    adjusted: list[str] = []
    in_frontmatter = False
    frontmatter_done = False
    in_fence = False
    fence_marker = ""

    for raw in lines:
        line = raw.rstrip("\n")
        newline = "\n" if raw.endswith("\n") else ""

        if not frontmatter_done and line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                adjusted.append(raw)
                continue
            in_frontmatter = False
            frontmatter_done = True
            adjusted.append(raw)
            continue

        if in_frontmatter:
            adjusted.append(raw)
            continue

        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif stripped.startswith(fence_marker):
                in_fence = False
                fence_marker = ""
            adjusted.append(raw)
            continue

        if in_fence:
            adjusted.append(raw)
            continue

        if stripped.startswith("#"):
            prefix = stripped.split()[0]
            level = len(prefix)
            new_level = max(1, min(6, level + delta))
            rest = line[len(prefix) :].lstrip()
            adjusted.append(f"{'#'*new_level} {rest}{newline}")
        else:
            adjusted.append(raw)

    return "".join(adjusted)
