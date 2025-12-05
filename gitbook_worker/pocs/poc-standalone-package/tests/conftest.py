"""pytest configuration for the PoC package tests.

This keeps the PoC self-contained without requiring installation into the
workspace environment and avoids touching production packages.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_poc_src_on_path() -> None:
    """Expose the PoC src directory as a temporary import root."""
    tests_dir = Path(__file__).resolve().parent
    poc_root = tests_dir.parent
    src_dir = poc_root / "src"

    if not src_dir.exists():  # pragma: no cover - defensive guard
        raise RuntimeError(f"Missing PoC src directory: {src_dir}")

    src_path = str(src_dir)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


_ensure_poc_src_on_path()
