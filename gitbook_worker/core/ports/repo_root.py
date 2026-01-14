from __future__ import annotations

from pathlib import Path
from typing import Protocol


class RepoRootNotFoundError(FileNotFoundError):
    """Raised when a repository root cannot be resolved."""


class RepoRootResolverPort(Protocol):
    """Resolve a repository root based on a starting path."""

    def resolve(self, start: Path) -> Path:  # pragma: no cover
        ...
