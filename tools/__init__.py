"""
DEPRECATED: Backward-compatibility shim for legacy ``tools.*`` imports.

Use the canonical import path instead:
    OLD: from tools.workflow_orchestrator import ...
    NEW: from gitbook_worker.tools.workflow_orchestrator import ...

This shim re-exports ``gitbook_worker.tools`` so existing launch configurations
and shell scripts keep working while repositories migrate to the standalone
package that now lives at repository root.
"""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

warnings.warn(
    "Importing via 'tools' is deprecated. "
    "Use 'from gitbook_worker.tools import ...' instead. ",
    DeprecationWarning,
    stacklevel=2,
)

_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

try:
    from gitbook_worker import tools as _tools_module

    __path__ = _tools_module.__path__  # type: ignore[attr-defined]

    def __getattr__(name: str):
        return getattr(_tools_module, name)

except ImportError as exc:  # pragma: no cover - defensive
    warnings.warn(
        f"Failed to import gitbook_worker.tools: {exc}\n"
        "Ensure the repository root is on PYTHONPATH.",
        ImportWarning,
        stacklevel=2,
    )
    raise

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

__deprecated__ = True
__migration_guide__ = "See tools/__init__.py"
