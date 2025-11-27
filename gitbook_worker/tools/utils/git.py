"""Git helper utilities built on top of the shared runner."""

from __future__ import annotations

import shutil
import stat
from pathlib import Path
from typing import Mapping, Optional

from gitbook_worker.tools.logging_config import get_logger

from .run import run

LOGGER = get_logger(__name__)


def _handle_readonly(func, path, exc_info):
    """Ensure read-only files can be removed on Windows."""
    try:
        Path(path).chmod(stat.S_IWRITE)
    except Exception:  # pragma: no cover - defensive fallback
        LOGGER.debug("Cannot update permissions for %s", path, exc_info=True)
    func(path)


def remove_tree(path: str | Path) -> None:
    """Delete a directory tree, clearing read-only bits first."""
    target = Path(path)
    if not target.exists():
        LOGGER.debug("remove_tree skipped, %s does not exist", target)
        return
    LOGGER.info("Removing directory tree %s", target)
    shutil.rmtree(target, onerror=_handle_readonly)


def checkout_branch(
    repo_dir: str | Path,
    branch_name: str,
    *,
    env: Mapping[str, str] | None = None,
) -> None:
    """Check out *branch_name* inside *repo_dir* and fast-forward to origin."""
    repo_path = Path(repo_dir)
    if not repo_path.exists():
        raise FileNotFoundError(f"Repository directory not found: {repo_path}")
    repo_str = str(repo_path)
    LOGGER.info("Checking out branch %s in %s", branch_name, repo_path)
    run(["git", "-C", repo_str, "checkout", branch_name], env=dict(env or {}))
    run(
        ["git", "-C", repo_str, "pull", "--ff-only", "origin", branch_name],
        check=False,
        env=dict(env or {}),
    )


def _is_git_repository(path: Path) -> bool:
    return (path / ".git").is_dir()


def clone_or_update_repo(
    repo_url: str,
    clone_dir: str | Path,
    *,
    branch_name: Optional[str] = None,
    force: bool = False,
    env: Mapping[str, str] | None = None,
) -> None:
    """Clone *repo_url* into *clone_dir* or update the existing checkout."""
    destination = Path(clone_dir)
    repo_str = str(destination)
    if destination.exists() and not _is_git_repository(destination):
        LOGGER.warning(
            "Existing path %s is not a Git repository; removing it.", destination
        )
        remove_tree(destination)

    if destination.exists() and force:
        LOGGER.info("Force-refreshing repository at %s", destination)
        remove_tree(destination)

    if not destination.exists():
        LOGGER.info("Cloning %s into %s", repo_url, destination)
        cmd = ["git", "clone"]
        if branch_name:
            cmd += ["--branch", branch_name]
        cmd += [repo_url, repo_str]
        run(cmd, env=dict(env or {}))
        return

    LOGGER.info("Updating existing repository at %s", destination)
    run(
        ["git", "-C", repo_str, "fetch", "--all", "--tags", "--prune"],
        env=dict(env or {}),
    )
    if branch_name:
        checkout_branch(destination, branch_name, env=env)
        run(
            ["git", "-C", repo_str, "reset", "--hard", f"origin/{branch_name}"],
            env=dict(env or {}),
        )
    else:
        run(["git", "-C", repo_str, "pull", "--ff-only"], env=dict(env or {}))
    run(["git", "-C", repo_str, "clean", "-fdx"], check=False, env=dict(env or {}))


__all__ = [
    "checkout_branch",
    "clone_or_update_repo",
    "remove_tree",
]
