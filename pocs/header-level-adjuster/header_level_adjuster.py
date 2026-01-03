"""Adjust Markdown heading levels for nested document inclusion.

Problem
-------
When combining many Markdown documents into a single book, a document's
internal headings often start at level 1 ("#"). However, when that document
lives under a folder whose ``readme.md`` already introduces a section heading
(e.g. "### 02 Specs"), the included document should start one level deeper
(e.g. "#### SPEC …") and all its sub-headings should be shifted accordingly.

This module provides a best-effort, defensive transformation:
- Reads the nearest sibling ``readme.md`` (same folder as the document)
  to determine the section heading level.
- Shifts ATX headings (``#`` .. ``######``) in the included document so that
  the document's first heading becomes ``parent_level + 1``.

Design notes
------------
- Only increases heading levels (never flattens).
- Skips transformations inside YAML front matter and fenced code blocks.
- Leaves folder ``readme.md`` files unchanged.
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.logging_config import get_logger

logger = get_logger(__name__)

_HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})(?P<rest>\s+.*)$")
_FENCE_OPEN_RE = re.compile(r"^\s*(```+|~~~+)\s*")


def _strip_front_matter(text: str) -> str:
    lines = text.splitlines(keepends=True)
    if not lines:
        return text
    if lines[0].strip() != "---":
        return text
    try:
        end_idx = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return text
    return "".join(lines[end_idx + 1 :])


def find_first_atx_heading_level(text: str) -> int | None:
    """Return the first ATX heading level (1..6) found in ``text``.

    Ignores YAML front matter and fenced code blocks.
    """

    body = _strip_front_matter(text)
    in_code = False
    fence_marker: str | None = None

    for raw in body.splitlines():
        line = raw.rstrip("\n")

        fence_match = _FENCE_OPEN_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if not in_code:
                in_code = True
                fence_marker = marker
            else:
                if fence_marker and line.lstrip().startswith(fence_marker):
                    in_code = False
                    fence_marker = None
            continue

        if in_code:
            continue

        m = _HEADING_RE.match(line)
        if m:
            return len(m.group("hashes"))

    return None


def shift_atx_headings(text: str, shift: int) -> str:
    """Shift ATX headings by ``shift`` levels.

    The shift is applied to all ATX headings outside YAML front matter and
    fenced code blocks. Heading levels are clamped to a maximum of 6.
    """

    if shift <= 0:
        return text

    lines = text.splitlines(keepends=True)
    out: list[str] = []

    in_front_matter = False
    in_code = False
    fence_marker: str | None = None

    for idx, raw in enumerate(lines):
        line_no_nl = raw.rstrip("\n")

        if idx == 0 and line_no_nl.strip() == "---":
            in_front_matter = True
            out.append(raw)
            continue

        if in_front_matter:
            out.append(raw)
            if line_no_nl.strip() == "---":
                in_front_matter = False
            continue

        fence_match = _FENCE_OPEN_RE.match(line_no_nl)
        if fence_match:
            marker = fence_match.group(1)
            if not in_code:
                in_code = True
                fence_marker = marker
            else:
                if fence_marker and line_no_nl.lstrip().startswith(fence_marker):
                    in_code = False
                    fence_marker = None
            out.append(raw)
            continue

        if in_code:
            out.append(raw)
            continue

        m = _HEADING_RE.match(line_no_nl)
        if m:
            current = len(m.group("hashes"))
            new_level = min(6, current + shift)
            if new_level != current + shift:
                logger.warning(
                    "Heading level clamped to 6 (current=%s, shift=%s)",
                    current,
                    shift,
                )
            out.append(
                "#" * new_level + m.group("rest") + ("\n" if raw.endswith("\n") else "")
            )
            continue

        out.append(raw)

    return "".join(out)


def _read_sibling_readme_heading_level(doc_path: Path) -> int | None:
    parent = doc_path.parent
    for name in ("readme.md", "README.md"):
        candidate = parent / name
        if candidate.exists() and candidate.is_file():
            try:
                content = candidate.read_text(encoding="utf-8")
            except Exception as e:  # pragma: no cover
                logger.warning("Could not read %s: %s", candidate, e)
                return None
            return find_first_atx_heading_level(content)
    return None


def adjust_headings_for_inclusion(text: str, *, doc_path: str | Path) -> str:
    """Adjust heading levels for a document being included into a combined book.

    - If the document is a folder ``readme.md`` itself: no change.
    - Otherwise, if a sibling folder ``readme.md`` exists with heading level L,
      then the included document's first heading is shifted to level L+1.

    Only increases heading levels.
    """

    p = Path(doc_path)
    if p.name.lower() == "readme.md":
        return text

    parent_level = _read_sibling_readme_heading_level(p)
    if not parent_level:
        return text

    desired_top = min(6, parent_level + 1)
    current_top = find_first_atx_heading_level(text)
    if not current_top:
        return text

    if desired_top <= current_top:
        return text

    shift = desired_top - current_top
    return shift_atx_headings(text, shift)
