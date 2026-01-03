"""Utilities to adjust heading levels when combining Markdown files.

The adjustment keeps included documents aligned with their parent README so
that the first heading of the included file becomes ``parent_level + 1``.
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


def _find_parent_readme_level(md_path: Path) -> Optional[int]:
    parent = md_path.parent
    for candidate in (parent / "README.md", parent / "readme.md"):
        level = _first_heading_level_from_file(candidate)
        if level:
            return level
    return None


def adjust_headings_for_inclusion(content: str, source_path: Path) -> str:
    """Shift heading levels so the first heading becomes parent_level + 1."""

    parent_level = _find_parent_readme_level(source_path)
    if parent_level is None:
        return content

    lines = content.splitlines(keepends=True)
    current_level = _first_heading_level(lines)
    if current_level is None:
        return content

    target_level = parent_level + 1
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
