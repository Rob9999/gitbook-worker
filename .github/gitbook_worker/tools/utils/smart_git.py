"""Smart git utilities with fallback support.

This module provides robust git operations with graceful fallbacks:
- Changed file detection with shallow clone support
- Commit analysis with multiple fallback strategies
- POSIX path normalization for cross-platform compatibility

Smart Merge Philosophy:
1. Explicit: Try git diff between commits
2. Convention: Fallback to single-commit analysis
3. Fallback: Use ls-tree for full file list

Used by:
- smart_manage_publish_flags.py (change detection)
- Other modules requiring git integration
"""

from __future__ import annotations

import posixpath
import subprocess
from typing import List, Optional, Tuple

from tools.logging_config import get_logger

logger = get_logger(__name__)


# ============================================================================
# Git Command Execution
# ============================================================================


def run_git_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Run a git command and return result.

    Args:
        cmd: Git command as list of strings (e.g., ["git", "diff", "--name-only"])

    Returns:
        Tuple of (returncode, stdout, stderr)

    Example:
        >>> code, out, err = run_git_command(["git", "status", "--short"])
        >>> if code == 0:
        ...     print(f"Git output: {out}")
    """
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, err = p.communicate()
    return p.returncode, out, err


# ============================================================================
# Path Normalization
# ============================================================================


def normalize_posix(path_str: str) -> str:
    """Normalize path to POSIX style (forward slashes).

    Git always uses forward slashes, so we normalize to POSIX style
    for consistent matching across platforms.

    Args:
        path_str: Path string to normalize (may contain backslashes)

    Returns:
        Normalized POSIX path with forward slashes

    Example:
        >>> normalize_posix("content\\\\file.md")
        'content/file.md'
        >>> normalize_posix("./content/file.md")
        'content/file.md'
        >>> normalize_posix(".")
        '.'
    """
    p = path_str.replace("\\", "/")
    p = p.lstrip("./")
    return posixpath.normpath(p)


# ============================================================================
# Changed Files Detection
# ============================================================================


def get_changed_files(
    commit: str,
    base: Optional[str] = None,
    *,
    normalize: bool = True,
) -> List[str]:
    """Get list of changed files between base and commit.

    Handles shallow clones (fetch-depth=1) by falling back to
    single-commit analysis when base is missing.

    Fallback strategy:
    1. Try: git diff base..commit
    2. If base missing: git diff-tree commit (single commit)
    3. If still fails: git ls-tree commit (all files)

    Args:
        commit: Target commit SHA (e.g., "HEAD", "abc123")
        base: Base commit SHA for comparison (optional)
        normalize: Normalize paths to POSIX style (default: True)

    Returns:
        List of changed file paths

    Example:
        >>> # Compare HEAD with previous commit
        >>> files = get_changed_files("HEAD", "HEAD~1")
        >>> print(files)
        ['content/chapter1.md', 'README.md']

        >>> # Single commit analysis (no base)
        >>> files = get_changed_files("HEAD")
        >>> print(files)
        ['content/new-file.md']

        >>> # Shallow clone scenario (base missing)
        >>> files = get_changed_files("HEAD", "nonexistent_base")
        >>> # Automatically falls back to single-commit analysis
    """

    def _diff_tree_single(target_commit: str) -> Tuple[int, str, str]:
        """Analyze single commit using diff-tree."""
        return run_git_command(
            [
                "git",
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                target_commit,
            ]
        )

    # Attempt comparison between base and commit
    if base:
        code, out, err = run_git_command(["git", "diff", "--name-only", base, commit])
        ctx = f"{base}..{commit}"

        if code != 0:
            # Check if error is due to missing base (shallow clone)
            lowered_error = err.lower()
            missing_base_keywords = [
                "bad revision",
                "unknown revision",
                "ambiguous argument",
                "not a valid object name",
                "bad object",
                "invalid upstream",
                "invalid revision",
                "no merge base",
            ]

            if any(kw in lowered_error for kw in missing_base_keywords):
                logger.warning(
                    "Could not find base commit %s (fetch-depth=1?). "
                    "Falling back to single-commit analysis.",
                    base,
                )
                code, out, err = _diff_tree_single(commit)
                ctx = commit
            else:
                logger.warning(
                    "Git diff %s failed (%s). Falling back to single-commit analysis.",
                    ctx,
                    err.strip() or f"Exit-Code {code}",
                )
                code, out, err = _diff_tree_single(commit)
                ctx = commit
    else:
        # No base provided, analyze single commit
        code, out, err = _diff_tree_single(commit)
        ctx = commit

    # Further fallback if diff-tree also failed
    if code != 0:
        logger.warning(
            "Git command failed (%s): %s",
            ctx,
            err.strip() or f"Exit-Code {code}",
        )

        # Final fallback: list all files in target commit
        ls_code, ls_out, ls_err = run_git_command(
            ["git", "ls-tree", "--full-tree", "-r", "--name-only", commit]
        )

        if ls_code == 0:
            file_count = len(ls_out.splitlines())
            logger.warning(
                "Fallback to ls-tree(%s). Treating %d file(s) as changed.",
                commit,
                file_count,
            )
            files = [line for line in ls_out.splitlines() if line.strip()]
            return [normalize_posix(f) for f in files] if normalize else files

        logger.error(
            "Final fallback ls-tree(%s) also failed: %s",
            commit,
            ls_err.strip(),
        )
        return []

    # Success - parse file list
    files = [line for line in out.splitlines() if line.strip()]
    return [normalize_posix(f) for f in files] if normalize else files


# ============================================================================
# Commit Information
# ============================================================================


def get_commit_sha(ref: str = "HEAD") -> Optional[str]:
    """Get full SHA for a git reference.

    Args:
        ref: Git reference (e.g., "HEAD", "main", "HEAD~1")

    Returns:
        Full commit SHA or None if ref invalid

    Example:
        >>> sha = get_commit_sha("HEAD")
        >>> print(sha)
        'abc123def456...'

        >>> sha = get_commit_sha("nonexistent")
        >>> print(sha)
        None
    """
    code, out, err = run_git_command(["git", "rev-parse", ref])
    if code == 0:
        return out.strip()
    logger.debug("Could not resolve ref %s: %s", ref, err.strip())
    return None


def get_commit_message(ref: str = "HEAD") -> Optional[str]:
    """Get commit message for a git reference.

    Args:
        ref: Git reference (e.g., "HEAD", "abc123")

    Returns:
        Commit message (first line) or None if ref invalid

    Example:
        >>> msg = get_commit_message("HEAD")
        >>> print(msg)
        'feat: Add new feature'
    """
    code, out, err = run_git_command(["git", "log", "-1", "--format=%s", ref])
    if code == 0:
        return out.strip()
    logger.debug("Could not get commit message for %s: %s", ref, err.strip())
    return None


def get_commit_author(ref: str = "HEAD") -> Optional[str]:
    """Get commit author for a git reference.

    Args:
        ref: Git reference (e.g., "HEAD", "abc123")

    Returns:
        Author name and email or None if ref invalid

    Example:
        >>> author = get_commit_author("HEAD")
        >>> print(author)
        'John Doe <john@example.com>'
    """
    code, out, err = run_git_command(["git", "log", "-1", "--format=%an <%ae>", ref])
    if code == 0:
        return out.strip()
    logger.debug("Could not get commit author for %s: %s", ref, err.strip())
    return None


# ============================================================================
# Repository Information
# ============================================================================


def is_git_repo(path: Optional[str] = None) -> bool:
    """Check if path is inside a git repository.

    Args:
        path: Path to check (default: current directory)

    Returns:
        True if inside git repo, False otherwise

    Example:
        >>> if is_git_repo():
        ...     print("In a git repository")
        ... else:
        ...     print("Not in a git repository")
    """
    cmd = ["git", "rev-parse", "--is-inside-work-tree"]
    code, out, _ = run_git_command(cmd)
    return code == 0 and out.strip().lower() == "true"


def get_repo_root(path: Optional[str] = None) -> Optional[str]:
    """Get root directory of git repository.

    Args:
        path: Path inside repository (default: current directory)

    Returns:
        Absolute path to repository root or None if not in repo

    Example:
        >>> root = get_repo_root()
        >>> print(root)
        '/home/user/my-project'
    """
    cmd = ["git", "rev-parse", "--show-toplevel"]
    code, out, _ = run_git_command(cmd)
    if code == 0:
        return out.strip()
    return None


def get_current_branch() -> Optional[str]:
    """Get name of current git branch.

    Returns:
        Branch name or None if detached HEAD or error

    Example:
        >>> branch = get_current_branch()
        >>> print(branch)
        'main'
    """
    code, out, _ = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if code == 0:
        branch = out.strip()
        return None if branch == "HEAD" else branch
    return None


# ============================================================================
# Working Directory Status
# ============================================================================


def has_uncommitted_changes() -> bool:
    """Check if working directory has uncommitted changes.

    Returns:
        True if there are uncommitted changes, False otherwise

    Example:
        >>> if has_uncommitted_changes():
        ...     print("Warning: uncommitted changes detected")
    """
    code, out, _ = run_git_command(["git", "status", "--porcelain"])
    if code == 0:
        return bool(out.strip())
    return False


def get_uncommitted_files() -> List[str]:
    """Get list of files with uncommitted changes.

    Returns:
        List of file paths (POSIX normalized)

    Example:
        >>> files = get_uncommitted_files()
        >>> print(files)
        ['content/modified.md', 'new-file.md']
    """
    code, out, _ = run_git_command(["git", "status", "--porcelain"])
    if code != 0:
        return []

    files = []
    for line in out.splitlines():
        if len(line) > 3:
            # Format: "XY filename" where XY is status code
            filepath = line[3:].strip()
            files.append(normalize_posix(filepath))

    return files


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Command execution
    "run_git_command",
    # Path utilities
    "normalize_posix",
    # Change detection
    "get_changed_files",
    # Commit info
    "get_commit_sha",
    "get_commit_message",
    "get_commit_author",
    # Repository info
    "is_git_repo",
    "get_repo_root",
    "get_current_branch",
    # Working directory
    "has_uncommitted_changes",
    "get_uncommitted_files",
]
