from __future__ import annotations

from pathlib import Path

from gitbook_worker.core.ports.repo_root import RepoRootResolverPort


def resolve_repo_root(*, start: Path, resolver: RepoRootResolverPort) -> Path:
    """Resolve and return the repository root.

    This use-case contains no IO; any IO/heuristics live in the resolver.
    """

    return resolver.resolve(start)
