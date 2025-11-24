"""Smart content configuration loader for multilingual repositories."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Mapping, Optional

import yaml

from gitbook_worker.tools.utils.smart_manifest import detect_repo_root
from gitbook_worker.tools.utils.semver import SemVerError, ensure_semver

_DEFAULT_CONTENT_VERSION = "1.0.0"
_CONTENT_FILENAMES: tuple[str, ...] = ("content.yaml", "content.yml")


@dataclass(frozen=True)
class ContentEntry:
    """Represents one language/content variant."""

    id: str
    uri: str
    type: str = "local"
    description: Optional[str] = None
    credential_ref: Optional[str] = None
    branch: Optional[str] = None
    raw: Mapping[str, object] | None = None

    @property
    def is_local(self) -> bool:
        return (self.type or "local").lower() == "local"

    def resolve_path(self, repo_root: Path) -> Path:
        """Return absolute path for local entries."""

        if not self.is_local:
            raise ValueError(
                f"Content entry '{self.id}' uses type='{self.type}' which cannot be resolved locally yet"
            )
        path = Path(self.uri or ".")
        if not path.is_absolute():
            path = (repo_root / path).resolve()
        return path


@dataclass(frozen=True)
class ContentConfig:
    """Loaded content configuration."""

    version: str
    default_id: str
    entries: Dict[str, ContentEntry]
    source_path: Optional[Path] = None

    def get(self, language_id: Optional[str]) -> ContentEntry:
        target_id = language_id or self.default_id
        if not target_id:
            raise KeyError("No language ID provided and no default configured")
        try:
            return self.entries[target_id]
        except KeyError as exc:
            available = ", ".join(sorted(self.entries)) or "<none>"
            raise KeyError(
                f"Language '{target_id}' not found in content config (available: {available})"
            ) from exc


def _coerce_entry(entry_id: str, payload: Mapping[str, object]) -> ContentEntry:
    uri = str(payload.get("uri") or payload.get("path") or ".")
    entry_type = str(payload.get("type") or "local")
    description = payload.get("description")
    if description is not None:
        description = str(description)
    credential_ref = payload.get("credentialRef") or payload.get("credential_ref")
    if credential_ref is not None:
        credential_ref = str(credential_ref)
    branch = payload.get("branch")
    if branch is not None:
        branch = str(branch)
    return ContentEntry(
        id=str(entry_id),
        uri=uri,
        type=entry_type,
        description=description,
        credential_ref=credential_ref,
        branch=branch,
        raw=dict(payload),
    )


def _parse_contents(entries_raw: Iterable[object]) -> Dict[str, ContentEntry]:
    entries: Dict[str, ContentEntry] = {}
    for entry in entries_raw:
        if isinstance(entry, Mapping):
            if "id" in entry:
                payload = entry
                entry_id = str(entry.get("id"))
                entry_payload = payload
            elif len(entry) == 1:
                entry_id, entry_payload = next(iter(entry.items()))
                if not isinstance(entry_payload, Mapping):
                    entry_payload = {}
                entry_id = str(entry_id)
            else:
                # Unsupported mapping without id
                continue
        else:
            continue

        content_entry = _coerce_entry(entry_id, entry_payload)
        entries[content_entry.id] = content_entry
    return entries


def _resolve_content_file(
    *,
    explicit: Path | str | None,
    cwd: Path,
    repo_root: Path,
) -> Optional[Path]:
    """Locate content.yaml similar to smart manifest search."""

    candidates: list[Path] = []

    def _maybe_add(base: Path) -> Optional[Path]:
        for name in _CONTENT_FILENAMES:
            candidate = (base / name).resolve()
            candidates.append(candidate)
            if candidate.exists():
                return candidate
        return None

    if explicit is not None:
        explicit_path = Path(explicit)
        candidate = (
            explicit_path
            if explicit_path.is_absolute()
            else (cwd / explicit_path).resolve()
        )
        candidates.append(candidate)
        if candidate.exists():
            return candidate
        if not explicit_path.is_absolute():
            alt = (repo_root / explicit_path).resolve()
            if alt != candidate:
                candidates.append(alt)
                if alt.exists():
                    return alt
        raise FileNotFoundError(
            "content config not found; tried: "
            + ", ".join(str(path) for path in candidates)
        )

    # Prefer cwd, then repo root
    for base in (cwd, repo_root):
        found = _maybe_add(base)
        if found:
            return found

    return None


def load_content_config(
    explicit: Path | str | None = None,
    *,
    cwd: Path | None = None,
    repo_root: Path | None = None,
    allow_missing: bool = True,
) -> ContentConfig:
    """Load multilingual content configuration.

    Args:
        explicit: Optional path override for content.yaml/yml
        cwd: Current working directory (defaults to Path.cwd())
        repo_root: Repository root (detected automatically if None)
        allow_missing: Return default config when file is absent
    """

    cwd_path = (cwd or Path.cwd()).resolve()
    repo_root_path = detect_repo_root(repo_root or cwd_path)

    content_path = _resolve_content_file(
        explicit=explicit, cwd=cwd_path, repo_root=repo_root_path
    )

    if content_path is None:
        if not allow_missing:
            raise FileNotFoundError("content.yaml not found in repository")
        default_entry = ContentEntry(
            id="default", uri="./", type="local", description="Repository root"
        )
        return ContentConfig(
            version=_DEFAULT_CONTENT_VERSION,
            default_id="default",
            entries={"default": default_entry},
            source_path=None,
        )

    raw = yaml.safe_load(content_path.read_text(encoding="utf-8")) or {}

    try:
        version = ensure_semver(
            raw.get("version"),
            field="content.yaml version",
            default=_DEFAULT_CONTENT_VERSION,
        )
    except SemVerError as exc:
        raise ValueError(str(exc)) from exc

    default_id = str(raw.get("default") or raw.get("default_id") or "").strip()

    contents_raw = raw.get("contents")
    if not isinstance(contents_raw, list):
        contents_raw = []

    entries = _parse_contents(contents_raw)

    if not entries:
        # Fall back to repository root when config exists but empty
        default_entry = ContentEntry(
            id="default", uri="./", type="local", description="Repository root"
        )
        entries[default_entry.id] = default_entry
        if not default_id:
            default_id = default_entry.id

    if not default_id or default_id not in entries:
        # Choose first entry as default when unspecified or invalid
        default_id = next(iter(entries.keys()))

    return ContentConfig(
        version=version,
        default_id=default_id,
        entries=entries,
        source_path=content_path,
    )


__all__ = [
    "ContentEntry",
    "ContentConfig",
    "load_content_config",
]
