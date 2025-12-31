#!/usr/bin/env python3
"""Repository path helpers bundled with the gitbook_worker package."""

from __future__ import annotations

import os
import pathlib

# Absolute Root of the repository (package checkout or install location)
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

# Defensive: ensure we imported the correct package instance (guards against stray
# gitbook_worker copies on sys.path). Require core assets to exist relative to this
# package root, otherwise fail fast with a clear error.
_REQUIRED_PATHS = [
    REPO_ROOT / "gitbook_worker" / "defaults" / "smart.yml",
    REPO_ROOT / "gitbook_worker" / "tools" / "publishing" / "pipeline.py",
]
missing = [str(p) for p in _REQUIRED_PATHS if not p.exists()]
if missing:
    raise RuntimeError(
        "Invalid gitbook_worker import: expected package assets not found. "
        f"Package root: {REPO_ROOT}. Missing: {', '.join(missing)}. "
        "Ensure PYTHONPATH does not shadow the installed gitbook_worker package."
    )

# Absolute .github Directory
GITHUB_DIR = REPO_ROOT / ".github"

# Absolute repository Tools Directory (package-first layout)
GH_TOOLS_DIR = REPO_ROOT / "gitbook_worker" / "tools"

# Absolute repository Docker Directory
GH_DOCKER_DIR = GH_TOOLS_DIR / "docker"

# Absolute repository Logs directory
GH_LOGS_DIR = REPO_ROOT / "logs"
GH_LOGS_DIR.mkdir(exist_ok=True)


def _maybe_print_paths() -> None:
    """Print paths for workflow.log when opt-in flag is enabled (default on).
    Respect GITBOOK_WORKER_PRINT_PATHS=0 to stay quiet in tests or imports.
    """
    flag = os.getenv("GITBOOK_WORKER_PRINT_PATHS", "1")
    if flag not in {"", "0", "false", "False"}:
        print(f"INFO: Repo Root         :  {REPO_ROOT}")
        print(f"INFO: Docker Directory  :  {GH_DOCKER_DIR}")
        print(f"INFO: Logs Directory    :  {GH_LOGS_DIR}")
        print(f"INFO: Tools Directory   :  {GH_TOOLS_DIR}")
        print(f"INFO: .github Directory :  {GITHUB_DIR}")


_maybe_print_paths()
