from __future__ import annotations

from pathlib import Path

from gitbook_worker.tools.utils.smart_content import load_content_config


def test_repository_content_entries(repo_root: Path) -> None:
    config = load_content_config(
        cwd=repo_root,
        repo_root=repo_root,
        allow_missing=False,
    )

    assert config.default_id == "de"

    de_entry = config.get("de")
    assert de_entry.is_local
    assert de_entry.uri.rstrip("/") in {"de", "./de"}
    assert (repo_root / de_entry.uri).resolve().is_dir()

    en_entry = config.get("en")
    assert en_entry.is_local
    assert (repo_root / en_entry.uri).resolve().is_dir()

    ua_entry = config.get("ua")
    assert not ua_entry.is_local
    assert ua_entry.credential_ref == "GITBOOK_CONTENT_UA_DEPLOY_KEY"
