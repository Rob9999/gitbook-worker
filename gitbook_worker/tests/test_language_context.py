from __future__ import annotations

from pathlib import Path

import pytest

import gitbook_worker.tools.utils.language_context as language_context_mod
from gitbook_worker.tools.utils.language_context import (
    build_language_env,
    resolve_language_context,
)


def _write_content_yaml(root: Path) -> None:
    (root / "content.yaml").write_text(
        """
version: 1.0.0
default: de
contents:
  - id: de
    type: local
    uri: de/
""",
        encoding="utf-8",
    )


def test_language_context_locates_manifest(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()
    lang_root = repo_root / "de"
    lang_root.mkdir()
    (lang_root / "publish.yml").write_text("publish: []\n", encoding="utf-8")
    _write_content_yaml(repo_root)

    ctx = resolve_language_context(repo_root=repo_root, language="de")

    assert ctx.root == lang_root.resolve()
    assert ctx.require_manifest() == (lang_root / "publish.yml").resolve()


def test_build_language_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()
    lang_root = repo_root / "de"
    lang_root.mkdir()
    (lang_root / "publish.yml").write_text("publish: []\n", encoding="utf-8")
    _write_content_yaml(repo_root)

    ctx = resolve_language_context(repo_root=repo_root, language=None)
    env = build_language_env(ctx)

    assert env["GITBOOK_CONTENT_ID"] == "de"
    assert Path(env["GITBOOK_CONTENT_ROOT"]).resolve() == lang_root.resolve()


def test_language_context_fetches_remote_git_entry(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()
    content = repo_root / "content.yaml"
    content.write_text(
        """
version: 1.0.0
default: ua
contents:
  - id: ua
    type: git
    uri: git@example.com:demo/repo.git
    credentialRef: TEST_DEPLOY_KEY
""",
        encoding="utf-8",
    )

    remote_dir = repo_root / ".gitbook-content" / "ua"
    secret = """-----BEGIN OPENSSH PRIVATE KEY-----\nfake\n-----END OPENSSH PRIVATE KEY-----"""
    monkeypatch.setenv("TEST_DEPLOY_KEY", secret)

    captured: dict[str, object] = {}

    def fake_clone(repo_url, clone_dir, *, branch_name=None, force=False, env=None):
        destination = Path(clone_dir)
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "publish.yml").write_text("publish: []\n", encoding="utf-8")
        captured.update(
            {
                "repo_url": repo_url,
                "clone_dir": destination,
                "branch": branch_name,
                "env": env or {},
            }
        )

    monkeypatch.setattr(
        language_context_mod.git_utils, "clone_or_update_repo", fake_clone
    )

    ctx = resolve_language_context(
        repo_root=repo_root,
        language="ua",
        allow_remote_entries=True,
        fetch_remote=True,
    )

    assert captured["repo_url"] == "git@example.com:demo/repo.git"
    assert Path(captured["clone_dir"]).resolve() == remote_dir.resolve()
    assert "GIT_SSH_COMMAND" in captured["env"]
    key_path = repo_root / ".gitbook-content" / "keys" / "ua.key"
    assert key_path.exists()
    assert ctx.root == remote_dir.resolve()
    assert ctx.require_manifest() == (remote_dir / "publish.yml").resolve()


def test_language_context_remote_missing_secret(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()
    (repo_root / "content.yaml").write_text(
        """
version: 1.0.0
default: ua
contents:
  - id: ua
    type: git
    uri: git@example.com:demo/repo.git
    credentialRef: TEST_DEPLOY_KEY
""",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError):
        resolve_language_context(
            repo_root=repo_root,
            language="ua",
            allow_remote_entries=True,
            fetch_remote=True,
        )
