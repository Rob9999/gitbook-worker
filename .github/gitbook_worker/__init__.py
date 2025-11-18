"""
Legacy placeholder for the former in-repo package.

The live package now resides at repository root (`gitbook_worker/`). This module
remains so historical documentation under `.github/gitbook_worker/docs/` can
still resolve `gitbook_worker.__version__` without pulling in code.
"""

__version__ = "1.0.2"
__all__ = ["__version__"]
