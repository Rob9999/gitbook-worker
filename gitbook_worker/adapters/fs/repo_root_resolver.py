from __future__ import annotations

import os
import subprocess
from pathlib import Path

from gitbook_worker.core.ports.repo_root import RepoRootNotFoundError


class DefaultRepoRootResolver:
    """Best-effort repository root resolver.

    Resolution order:
    1) GITBOOK_REPO_ROOT env var
    2) `git rev-parse --show-toplevel`
    3) Upwards scan for marker files/dirs
    """

    def resolve(self, start: Path) -> Path:
        env = os.getenv("GITBOOK_REPO_ROOT")
        if env:
            candidate = Path(env).expanduser().resolve()
            if candidate.exists():
                return candidate

        git_root = self._try_git_toplevel(start)
        if git_root is not None:
            return git_root

        scanned = self._scan_upwards_for_markers(start)
        if scanned is not None:
            return scanned

        raise RepoRootNotFoundError(
            f"Repository root could not be resolved starting from: {start}"
        )

    @staticmethod
    def _try_git_toplevel(start: Path) -> Path | None:
        try:
            proc = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=str(start.resolve()),
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except OSError:
            return None

        if proc.returncode != 0:
            return None

        out = (proc.stdout or "").strip()
        if not out:
            return None
        return Path(out).resolve()

    @staticmethod
    def _scan_upwards_for_markers(start: Path) -> Path | None:
        markers = (
            ".git",
            "pyproject.toml",
            "content.yaml",
            "content.yml",
            "publish.yml",
            "publish.yaml",
            "book.json",
        )

        current = start.resolve()
        if current.is_file():
            current = current.parent

        for candidate in [current, *current.parents]:
            if any((candidate / marker).exists() for marker in markers):
                return candidate
        return None
