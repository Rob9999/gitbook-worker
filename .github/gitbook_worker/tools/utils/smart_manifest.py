"""Utilities for resolving publish manifests using configurable rules."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import yaml

from tools.utils.semver import SemVerError, ensure_semver

DEFAULT_FILENAMES: tuple[str, ...] = ("publish.yml", "publish.yaml")
DEFAULT_CONFIG_VERSION = "1.0.0"


@dataclass(frozen=True)
class _SearchRule:
    """Describes one search step for manifest resolution."""

    kind: str
    directory: str | None = None
    filenames: tuple[str, ...] | None = None


@dataclass(frozen=True)
class SmartManifestConfig:
    """Configuration used by :func:`resolve_manifest`."""

    version: str
    filenames: tuple[str, ...]
    search: tuple[_SearchRule, ...]


class SmartManifestError(FileNotFoundError):
    """Raised when no manifest could be located."""


class SmartManifestConfigError(ValueError):
    """Raised when the smart manifest configuration is invalid."""


def _default_config() -> SmartManifestConfig:
    return SmartManifestConfig(
        version=DEFAULT_CONFIG_VERSION,
        filenames=DEFAULT_FILENAMES,
        search=(
            _SearchRule("cli"),
            _SearchRule("cwd"),
            _SearchRule("repo_root"),
        ),
    )


def _config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "defaults" / "smart.yml"


def _load_config(path: Path | None = None) -> SmartManifestConfig:
    config_path = path or _config_path()
    if not config_path.is_file():
        return _default_config()

    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

    try:
        version = ensure_semver(
            data.get("version"),
            field="smart.yml version",
            default=DEFAULT_CONFIG_VERSION,
        )
    except SemVerError as exc:  # pragma: no cover - validated by unit tests
        raise SmartManifestConfigError(str(exc)) from exc

    filenames_raw = data.get("filenames")
    if isinstance(filenames_raw, Sequence) and not isinstance(filenames_raw, (str, bytes)):
        filenames = tuple(str(item) for item in filenames_raw if str(item).strip())
    else:
        filenames = DEFAULT_FILENAMES
    if not filenames:
        filenames = DEFAULT_FILENAMES

    search_rules: list[_SearchRule] = []
    raw_search = data.get("search") or []
    if isinstance(raw_search, Sequence) and not isinstance(raw_search, (str, bytes)):
        for entry in raw_search:
            if isinstance(entry, Mapping):
                kind = str(entry.get("type", "")).strip()
                if not kind:
                    continue
                filenames_override_raw = entry.get("filenames")
                filenames_override: tuple[str, ...] | None = None
                if isinstance(filenames_override_raw, Sequence) and not isinstance(
                    filenames_override_raw, (str, bytes)
                ):
                    extracted = [str(item).strip() for item in filenames_override_raw if str(item).strip()]
                    filenames_override = tuple(extracted) if extracted else None
                directory_raw = entry.get("directory")
                directory = str(directory_raw).strip() if directory_raw else None
                search_rules.append(
                    _SearchRule(kind=kind, directory=directory, filenames=filenames_override)
                )
            elif isinstance(entry, str):
                if entry.strip():
                    search_rules.append(_SearchRule(kind=entry.strip()))
    if not search_rules:
        search_rules = list(_default_config().search)

    return SmartManifestConfig(
        version=version,
        filenames=filenames,
        search=tuple(search_rules),
    )


def detect_repo_root(start: Path | None = None) -> Path:
    """Detect the repository root starting from ``start``."""

    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
        if any((candidate / name).exists() for name in DEFAULT_FILENAMES):
            return candidate
        if (candidate / "book.json").exists():
            return candidate
    return current


def _resolve_directory(raw: str, *, cwd: Path, repo_root: Path) -> Path:
    template = raw.replace("{repo_root}", str(repo_root)).replace("{cwd}", str(cwd))
    candidate = Path(template)
    if not candidate.is_absolute():
        candidate = (repo_root / candidate).resolve()
    return candidate


def _iter_candidates(base: Path, filenames: Sequence[str]) -> Iterable[Path]:
    for name in filenames:
        if not name:
            continue
        yield (base / name).resolve()


def resolve_manifest(
    *,
    explicit: Path | str | None,
    cwd: Path | None = None,
    repo_root: Path | None = None,
    config_path: Path | None = None,
) -> Path:
    """Resolve the manifest path according to the smart manifest rules."""

    cfg = _load_config(config_path)
    cwd_path = (cwd or Path.cwd()).resolve()
    repo_root_path = detect_repo_root(repo_root or cwd_path)

    attempts: list[Path] = []

    explicit_path: Path | None = None
    if explicit is not None:
        explicit_path = Path(explicit)
        if explicit_path.is_absolute():
            candidate = explicit_path
        else:
            candidate = (cwd_path / explicit_path).resolve()
        attempts.append(candidate)
        if candidate.exists():
            return candidate
        if not explicit_path.is_absolute() and repo_root_path != cwd_path:
            alt = (repo_root_path / explicit_path).resolve()
            attempts.append(alt)
            if alt.exists():
                return alt
        raise SmartManifestError(
            f"Manifest '{explicit_path}' wurde nicht gefunden. Versuchte Pfade: "
            + ", ".join(str(path) for path in attempts)
        )

    for rule in cfg.search:
        if rule.kind == "cli":
            # Already handled via explicit argument above.
            continue

        filenames = rule.filenames or cfg.filenames
        base_dir: Path | None = None

        if rule.kind == "cwd":
            base_dir = cwd_path
        elif rule.kind == "repo_root":
            base_dir = repo_root_path
        elif rule.kind == "directory" and rule.directory:
            base_dir = _resolve_directory(rule.directory, cwd=cwd_path, repo_root=repo_root_path)

        if base_dir is None:
            continue

        for candidate in _iter_candidates(base_dir, filenames):
            attempts.append(candidate)
            if candidate.exists():
                return candidate

    raise SmartManifestError(
        "Kein publish-Manifest gefunden. Versuchte Pfade: "
        + ", ".join(str(path) for path in attempts)
    )


__all__ = [
    "SmartManifestConfig",
    "SmartManifestConfigError",
    "SmartManifestError",
    "detect_repo_root",
    "resolve_manifest",
]
