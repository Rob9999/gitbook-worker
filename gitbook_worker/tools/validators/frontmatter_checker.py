from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import yaml

FRONTMATTER_EXIT_CODE = 42
_SKIP_DIRS = {"publish", "temp", ".git", ".venv", ".gitbook"}


@dataclass(frozen=True)
class FrontmatterIssue:
    path: Path
    line: int
    message: str
    snippet: str | None = None


def _extract_frontmatter(text: str) -> tuple[str | None, int]:
    """Return (block_text, start_line) or (None, 0) if no frontmatter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, 0
    block_lines: list[str] = []
    for idx, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            return "\n".join(block_lines), 2  # frontmatter content starts at line 2
        block_lines.append(line)
    # unterminated frontmatter
    return "\n".join(block_lines), 2


def _format_snippet(block: str, err_line: int, context: int = 2) -> str:
    lines = block.splitlines()
    start = max(0, err_line - 1 - context)
    end = min(len(lines), err_line + context)
    return "\n".join(lines[start:end])


def check_file(path: Path) -> list[FrontmatterIssue]:
    text = path.read_text(encoding="utf-8")
    block, start_line = _extract_frontmatter(text)
    if block is None:
        return []
    try:
        yaml.safe_load(block or "{}")
        return []
    except yaml.YAMLError as exc:
        problem_line = getattr(getattr(exc, "problem_mark", None), "line", None)
        if problem_line is None:
            line_no = start_line
        else:
            line_no = start_line + int(problem_line)
        snippet = _format_snippet(
            block, int(problem_line) + 1 if problem_line is not None else 1
        )
        return [
            FrontmatterIssue(
                path=path,
                line=line_no,
                message=str(exc).strip(),
                snippet=snippet or None,
            )
        ]


def iter_markdown_files(
    root: Path, *, exclude_dirs: Sequence[str] | None = None
) -> Iterable[Path]:
    excludes = set(exclude_dirs or ()) | _SKIP_DIRS
    for path in root.rglob("*.md"):
        try:
            rel_parts = path.relative_to(root).parts
        except ValueError:
            continue
        if any(part in excludes for part in rel_parts):
            continue
        yield path


def check_frontmatter_tree(
    root: Path, *, exclude_dirs: Sequence[str] | None = None
) -> list[FrontmatterIssue]:
    issues: list[FrontmatterIssue] = []
    for path in iter_markdown_files(root, exclude_dirs=exclude_dirs):
        issues.extend(check_file(path))
    return issues


__all__ = [
    "FrontmatterIssue",
    "FRONTMATTER_EXIT_CODE",
    "check_file",
    "check_frontmatter_tree",
    "iter_markdown_files",
]
