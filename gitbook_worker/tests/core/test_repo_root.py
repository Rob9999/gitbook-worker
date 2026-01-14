from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from gitbook_worker.adapters.fs.repo_root_resolver import DefaultRepoRootResolver
from gitbook_worker.core.application.repo_root import resolve_repo_root
from gitbook_worker.core.ports.repo_root import RepoRootNotFoundError


@dataclass(frozen=True)
class _FakeResolver:
    resolved: Path

    def resolve(self, start: Path) -> Path:
        return self.resolved


def test_resolve_repo_root_use_case_delegates() -> None:
    expected = Path("/tmp/example")
    assert resolve_repo_root(start=Path("."), resolver=_FakeResolver(expected)) == expected


def test_default_repo_root_resolver_scans_for_markers(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    nested = repo_root / "a" / "b"
    nested.mkdir(parents=True)

    # marker that exists in this repo as well
    (repo_root / "content.yaml").write_text("version: 1.0.0\n", encoding="utf-8")

    resolved = DefaultRepoRootResolver().resolve(nested)
    assert resolved == repo_root


def test_default_repo_root_resolver_raises_when_unresolvable(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("GITBOOK_REPO_ROOT", raising=False)
    start = tmp_path / "no_markers"
    start.mkdir()

    resolver = DefaultRepoRootResolver()
    # Force git fallback to be ignored
    monkeypatch.setattr(resolver, "_try_git_toplevel", lambda *_: None)

    with pytest.raises(RepoRootNotFoundError):
        resolver.resolve(start)
