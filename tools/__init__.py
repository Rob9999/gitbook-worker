"""
DEPRECATED: Backward-compatibility shim for legacy 'tools.*' imports.

⚠️  THIS MODULE IS DEPRECATED AND WILL BE REMOVED IN A FUTURE VERSION.

Use the canonical import path instead:
    OLD: from tools.workflow_orchestrator import ...
    NEW: from gitbook_worker.tools.workflow_orchestrator import ...

This shim re-exports gitbook_worker.tools for compatibility with:
- Legacy VS Code launch configurations
- Shell scripts and workflows using `-m tools.xxx`
- External automation that hasn't been migrated yet

Migration guide:
1. Update PYTHONPATH to include only .github/:
   - PowerShell: $env:PYTHONPATH = "$PWD\\.github"
   - Bash: export PYTHONPATH="${PWD}/.github"

2. Change imports from 'tools.*' to 'gitbook_worker.tools.*'

3. Update module invocations:
   - OLD: python -m tools.workflow_orchestrator
   - NEW: python -m gitbook_worker.tools.workflow_orchestrator
"""

import sys
import warnings
from pathlib import Path
import os

# Issue deprecation warning on import
warnings.warn(
    "Importing via 'tools' is deprecated. "
    "Use 'from gitbook_worker.tools import ...' instead. "
    "See tools/__init__.py for migration guide.",
    DeprecationWarning,
    stacklevel=2,
)

# Ensure .github/ is in sys.path for gitbook_worker package resolution
_repo_root = Path(__file__).resolve().parent.parent
_github_path = str(_repo_root / ".github")

if _github_path not in sys.path:
    sys.path.insert(0, _github_path)

# Re-export gitbook_worker.tools as 'tools' for backward compatibility
try:
    from gitbook_worker import tools as _tools_module

    # Import all public symbols from gitbook_worker.tools
    __path__ = _tools_module.__path__  # type: ignore

    # Make submodules importable (tools.workflow_orchestrator, etc.)
    # by delegating attribute access to gitbook_worker.tools
    def __getattr__(name):
        """Lazy attribute access to delegate to gitbook_worker.tools."""
        return getattr(_tools_module, name)

except ImportError as e:
    warnings.warn(
        f"Failed to import gitbook_worker.tools: {e}\n"
        f"Ensure PYTHONPATH includes .github/ directory",
        ImportWarning,
        stacklevel=2,
    )
    raise

# Ensure subprocess/text IO uses UTF-8 where possible to avoid
# platform-default codec (cp1252) decoding errors when the
# tools package launches other processes that emit UTF-8.
# This mirrors setting PYTHONUTF8=1 and PYTHONIOENCODING=utf-8 for
# local invocations (harmless if already set).
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# Expose legacy metadata for debugging
__deprecated__ = True
__migration_guide__ = "See docstring above or tools/__init__.py"
