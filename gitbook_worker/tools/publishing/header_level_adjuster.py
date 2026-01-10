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

import os
from pathlib import Path
from typing import Iterable, Optional
from gitbook_worker.tools.logging_config import get_logger

logger = get_logger(__name__)

# Toggle: align a document's first heading to the summary-derived level while
# preserving its internal cascade. Enabled via env for reversible experiments.
FORCE_SUMMARY_LEVEL = os.environ.get("GBW_FORCE_SUMMARY_LEVEL", "0") == "1"

# ---------- Summary-driven test helper ----------


def _parse_summary_lines(summary_text: str) -> list[tuple[int, str, str]]:
    """Return (depth, title, href) tuples from a GitBook-style SUMMARY.md.

    Depth is derived from leading spaces before ``*`` (2 spaces == one level).
    """

    entries: list[tuple[int, str, str]] = []
    for raw in summary_text.splitlines():
        line = raw.rstrip()
        if not line.lstrip().startswith("*"):
            continue

        leading_spaces = len(line) - len(line.lstrip(" "))
        depth = leading_spaces // 2 + 1  # 0/2 -> 1 (top-level), etc.

        # Extract [title](href) without relying on regex-heavy parsing.
        title_start = line.find("[")
        link_sep = line.find("](")
        end_paren = line.rfind(")")
        if title_start == -1 or link_sep == -1 or end_paren == -1:
            continue

        title = line[title_start + 1 : link_sep]
        href = line[link_sep + 2 : end_paren]
        entries.append((depth, title, href))

    return entries


def render_summary_toc(summary_path: Path) -> str:
    """Generate a TOC preview that enforces heading levels from SUMMARY.md.

    For testing header leveling, we intentionally ignore any existing headings
    inside the target documents and instead map each SUMMARY.md entry to a
    synthetic heading ``#`` repeated by its summary depth.
    """

    text = summary_path.read_text(encoding="utf-8")
    rows = _parse_summary_lines(text)
    rendered: list[str] = []
    for depth, title, href in rows:
        rendered.append(f"{'#'*depth} {title}  ({href})")
    return "\n".join(rendered)


def demo_summary_toc(summary_path: Path) -> None:
    """Print a SUMMARY.md-driven TOC for manual inspection.

    Usage (from repo root):
    ``python -m gitbook_worker.tools.publishing.header_level_adjuster demo``
    """

    print(render_summary_toc(summary_path))


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
    logger.debug(
        "Adjusting headings for %s (target_level=%s)", source_path, target_level
    )
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
        if not FORCE_SUMMARY_LEVEL and delta == 0:
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
            adjusted_line = f"{'#'*new_level} {rest}{newline}"
            adjusted.append(adjusted_line)
            logger.info(
                "Adjusted heading: level %d -> %d: '%s' -> '%s'",
                level,
                new_level,
                line.strip(),
                adjusted_line.strip(),
            )
        else:
            adjusted.append(raw)

    joined = "".join(adjusted)

    logger.debug(
        "Shifting headings in %s: current_level=%d, target_level=%d, delta=%d, lines=%s, adjusted=%s",
        source_path,
        current_level,
        target_level,
        delta,
        lines,
        adjusted,
    )

    return joined


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    if not args:
        summary = Path("customer-de/content/SUMMARY.md")
    else:
        summary = Path(args[0])

    demo_summary_toc(summary)
