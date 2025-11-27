"""Helpers for resolving multilingual language roots and manifests."""

from __future__ import annotations

import os
import shlex
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from gitbook_worker.tools.logging_config import get_logger
from gitbook_worker.tools.utils import git as git_utils

from gitbook_worker.tools.utils.smart_content import (
    ContentConfig,
    ContentEntry,
    load_content_config,
)
from gitbook_worker.tools.utils.smart_manifest import (
    DEFAULT_FILENAMES,
    SmartManifestError,
    detect_repo_root,
    resolve_manifest,
)


LOGGER = get_logger(__name__)
_REMOTE_CACHE_DIRNAME = ".gitbook-content"
_REMOTE_KEYS_DIRNAME = "keys"


@dataclass(frozen=True)
class LanguageContext:
    """Resolved language configuration derived from content.yaml."""

    repo_root: Path
    config: ContentConfig
    content_config_path: Path | None
    language_id: str
    entry: ContentEntry
    root: Path
    manifest: Path | None

    def require_manifest(self) -> Path:
        if self.manifest is None:
            raise FileNotFoundError(
                "No publish manifest found for the selected language."
            )
        return self.manifest


def _iter_manifest_candidates(base: Path | None) -> tuple[Path, ...]:
    if base is None:
        return ()
    return tuple((base / name).resolve() for name in DEFAULT_FILENAMES)


def _first_existing_manifest(base: Path | None) -> Path | None:
    for candidate in _iter_manifest_candidates(base):
        if candidate.exists():
            return candidate
    return None


def resolve_language_context(
    *,
    repo_root: Path | None = None,
    language: str | None = None,
    manifest: Path | str | None = None,
    content_config: Path | str | None = None,
    allow_missing_config: bool = True,
    allow_remote_entries: bool = False,
    require_manifest: bool = True,
    fetch_remote: bool = False,
    remote_cache_dir: Path | None = None,
) -> LanguageContext:
    """Resolve language configuration for CLI entrypoints."""

    repo_root_path = detect_repo_root(repo_root or Path.cwd())

    env_config = os.getenv("GITBOOK_CONTENT_CONFIG")
    config_path = content_config or env_config

    config = load_content_config(
        explicit=config_path,
        cwd=repo_root_path,
        repo_root=repo_root_path,
        allow_missing=allow_missing_config,
    )

    env_language = os.getenv("GITBOOK_CONTENT_ID")
    language_id = (language or env_language or config.default_id) or config.default_id

    entry = config.get(language_id)
    if not allow_remote_entries and not entry.is_local:
        raise ValueError(
            f"Content entry '{language_id}' uses remote type '{entry.type}' which is not supported yet"
        )

    cache_root = remote_cache_dir or (repo_root_path / _REMOTE_CACHE_DIRNAME)
    language_root = _resolve_language_root(
        entry,
        repo_root_path=repo_root_path,
        cache_root=cache_root,
        fetch_remote=fetch_remote,
    )

    explicit_manifest = manifest
    manifest_path: Path | None

    if explicit_manifest is not None:
        manifest_path = resolve_manifest(
            explicit=explicit_manifest,
            cwd=repo_root_path,
            repo_root=repo_root_path,
        )
    else:
        manifest_path = _first_existing_manifest(language_root)
        if manifest_path is None:
            env_root_path = os.getenv("GITBOOK_CONTENT_ROOT")
            if env_root_path:
                manifest_path = _first_existing_manifest(Path(env_root_path))
        if manifest_path is None:
            try:
                manifest_path = resolve_manifest(
                    explicit=None,
                    cwd=language_root,
                    repo_root=repo_root_path,
                )
            except SmartManifestError:
                manifest_path = None

    if require_manifest and manifest_path is None:
        raise FileNotFoundError(f"publish.yml not found for language '{language_id}'")

    return LanguageContext(
        repo_root=repo_root_path,
        config=config,
        content_config_path=config.source_path,
        language_id=language_id,
        entry=entry,
        root=language_root,
        manifest=manifest_path,
    )


def build_language_env(ctx: LanguageContext) -> Mapping[str, str]:
    env: dict[str, str] = {
        "GITBOOK_CONTENT_ID": ctx.language_id,
        "GITBOOK_CONTENT_ROOT": str(ctx.root),
    }
    if ctx.content_config_path is not None:
        env["GITBOOK_CONTENT_CONFIG"] = str(ctx.content_config_path)
    return env


def _resolve_language_root(
    entry: ContentEntry,
    *,
    repo_root_path: Path,
    cache_root: Path,
    fetch_remote: bool,
) -> Path:
    if entry.is_local:
        return entry.resolve_path(repo_root_path)

    env_root_value = os.getenv("GITBOOK_CONTENT_ROOT")
    if env_root_value:
        env_root = Path(env_root_value).expanduser().resolve()
        LOGGER.info(
            "Using existing remote language root from GITBOOK_CONTENT_ROOT: %s",
            env_root,
        )
        return env_root

    if not fetch_remote:
        raise ValueError(
            f"Content entry '{entry.id}' is remote ({entry.type}); set GITBOOK_CONTENT_ROOT"
            " or enable fetch_remote to clone it automatically."
        )

    return _fetch_remote_content(
        entry, repo_root_path=repo_root_path, cache_root=cache_root
    )


def _fetch_remote_content(
    entry: ContentEntry,
    *,
    repo_root_path: Path,
    cache_root: Path,
) -> Path:
    entry_type = (entry.type or "").lower()
    if entry_type != "git":
        raise ValueError(
            f"Remote content type '{entry.type}' is not supported (entry '{entry.id}')"
        )

    destination = (cache_root / entry.id).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    LOGGER.info("Fetching remote content '%s' into %s", entry.id, destination)

    env = _build_git_env(entry, cache_root)
    git_utils.clone_or_update_repo(
        entry.uri,
        destination,
        branch_name=entry.branch,
        env=env if env else None,
    )
    return destination


def _build_git_env(entry: ContentEntry, cache_root: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not entry.credential_ref:
        return env

    secret = os.getenv(entry.credential_ref)
    if not secret:
        raise RuntimeError(
            "Credential reference '"
            + entry.credential_ref
            + "' not found in environment."
        )

    key_path = _resolve_secret_to_path(entry, secret, cache_root)
    quoted = shlex.quote(str(key_path))
    env["GIT_SSH_COMMAND"] = (
        f"ssh -i {quoted} -o IdentitiesOnly=yes -o StrictHostKeyChecking=no"
    )
    LOGGER.debug(
        "Configured SSH key for entry '%s' using credentialRef '%s'",
        entry.id,
        entry.credential_ref,
    )
    return env


def _resolve_secret_to_path(entry: ContentEntry, secret: str, cache_root: Path) -> Path:
    candidate = Path(secret).expanduser()
    if candidate.exists():
        return candidate.resolve()

    if "-----BEGIN" not in secret and "\n" not in secret:
        raise FileNotFoundError(
            f"Credential ref '{entry.credential_ref}' points to '{secret}', but the file does not exist."
        )

    safe_id = _sanitize_entry_id(entry.id)
    key_dir = cache_root / _REMOTE_KEYS_DIRNAME
    key_dir.mkdir(parents=True, exist_ok=True)
    key_path = key_dir / f"{safe_id}.key"
    material = secret.strip()
    if not material.endswith("\n"):
        material += "\n"
    key_path.write_text(material, encoding="utf-8")
    try:
        key_path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except Exception:  # pragma: no cover - best effort on Windows
        pass
    return key_path.resolve()


def _sanitize_entry_id(entry_id: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in entry_id)


__all__ = [
    "LanguageContext",
    "build_language_env",
    "resolve_language_context",
]
