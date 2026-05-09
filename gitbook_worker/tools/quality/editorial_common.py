"""Shared models for editorial quality metrics and acceptance reports."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping, Sequence

import yaml

from gitbook_worker import __version__

SCHEMA_VERSION = "1.0.0"
EDITORIAL_HARD_FINDINGS_EXIT_CODE = 45
EDITORIAL_BLOCKED_EXIT_CODE = 46
EDITORIAL_REPORT_READ_EXIT_CODE = 47
EDITORIAL_INVALID_PROFILE_EXIT_CODE = 48

Severity = Literal["info", "warn", "fail", "blocked"]
AcceptanceStatus = Literal["passed", "passed_with_warnings", "failed", "blocked"]

SEVERITY_ORDER: tuple[Severity, ...] = ("blocked", "fail", "warn", "info")
DEFAULT_EXCLUDE_DIRS: tuple[str, ...] = (
    ".git",
    ".gitbook",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "desktop",
    "logs",
    "publish",
    "release-docs",
    "temp",
    "tmp",
)
DEFAULT_SKIP_FILENAMES: tuple[str, ...] = ("SUMMARY.md",)


@dataclass(frozen=True)
class Finding:
    """A stable editorial finding that can be rendered in JSON and Markdown."""

    id: str
    severity: Severity
    category: str
    rule_id: str
    artifact: str
    location: str
    evidence: str
    editorial_impact: str
    healing: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MarkdownProfile:
    """Markdown and translation rules for an editorial profile."""

    locale_field: str = "content_lang"
    identity_key: str = "content_id"
    source_link_field: str = "source"
    source_locale: str | None = None
    target_locales: tuple[str, ...] = ()
    forbidden_frontmatter_keys: tuple[str, ...] = (
        "lang",
        "language",
        "lang-version",
    )
    required_frontmatter_by_role: Mapping[str, tuple[str, ...]] = field(
        default_factory=lambda: {
            "source": ("content_id", "content_lang"),
            "target": ("content_id", "content_lang", "source", "status"),
        }
    )
    allowed_translation_status: tuple[str, ...] = (
        "draft",
        "in-review",
        "approved",
    )
    exclude_dirs: tuple[str, ...] = DEFAULT_EXCLUDE_DIRS
    skip_filenames: tuple[str, ...] = DEFAULT_SKIP_FILENAMES
    long_token_warn_chars: int = 80


@dataclass(frozen=True)
class PdfProfile:
    """PDF metric thresholds for an editorial profile."""

    low_text_page_threshold: int = 15
    very_low_text_page_threshold: int = 5
    required_fonts: tuple[str, ...] = ()
    pdf_targets: Mapping[str, Mapping[str, int]] = field(default_factory=dict)


@dataclass(frozen=True)
class DocumentationProfile:
    """Rules for report drift and documentation freshness."""

    fail_on_stale_worker_version: bool = False
    fail_on_stale_page_count: bool = False


@dataclass(frozen=True)
class AcceptanceProfile:
    """Complete profile used by metrics and acceptance tools."""

    name: str
    network: bool = False
    fail_on_warnings: bool = False
    markdown: MarkdownProfile = field(default_factory=MarkdownProfile)
    pdf: PdfProfile = field(default_factory=PdfProfile)
    documentation: DocumentationProfile = field(default_factory=DocumentationProfile)

    def to_dict(self) -> dict[str, Any]:
        return _json_ready(asdict(self))  # type: ignore[return-value]


def utc_now_iso() -> str:
    """Return a compact UTC timestamp for reports."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def relative_artifact(path: Path | str, repo_root: Path) -> str:
    """Return a stable POSIX-style path without leaking absolute workspace roots."""

    candidate = Path(path)
    try:
        return candidate.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return candidate.as_posix()


def stable_finding_id(
    rule_id: str,
    artifact: str,
    location: str,
    evidence: str,
    *,
    page: int | None = None,
) -> str:
    """Build a deterministic short ID from normalized finding evidence."""

    normalized = "\n".join(
        [rule_id, artifact, location, str(page or ""), _normalize_id_text(evidence)]
    )
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
    return f"{rule_id}:{digest}"


def make_finding(
    *,
    rule_id: str,
    severity: Severity,
    category: str,
    artifact: str,
    location: str,
    evidence: str,
    editorial_impact: str,
    healing: str,
    page: int | None = None,
) -> Finding:
    """Create a finding with a stable ID."""

    return Finding(
        id=stable_finding_id(rule_id, artifact, location, evidence, page=page),
        severity=severity,
        category=category,
        rule_id=rule_id,
        artifact=artifact,
        location=location,
        evidence=shorten_evidence(evidence),
        editorial_impact=editorial_impact,
        healing=healing,
    )


def shorten_evidence(value: str, *, max_chars: int = 220) -> str:
    """Keep report evidence concise enough for customer-safe dossiers."""

    text = " ".join(str(value).split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def severity_counts(findings: Iterable[Mapping[str, Any] | Finding]) -> dict[str, int]:
    """Count findings by severity."""

    counts = {severity: 0 for severity in SEVERITY_ORDER}
    for finding in findings:
        severity = (
            finding.severity
            if isinstance(finding, Finding)
            else finding.get("severity")
        )
        if severity in counts:
            counts[str(severity)] += 1
    return counts


def status_from_counts(
    counts: Mapping[str, int], *, fail_on_warnings: bool = False
) -> AcceptanceStatus:
    """Return the editorial status implied by severity counts."""

    if counts.get("blocked", 0) > 0:
        return "blocked"
    if counts.get("fail", 0) > 0:
        return "failed"
    if counts.get("warn", 0) > 0:
        return "failed" if fail_on_warnings else "passed_with_warnings"
    return "passed"


def exit_code_for_status(status: AcceptanceStatus) -> int:
    """Map acceptance status to stable exit codes."""

    if status == "blocked":
        return EDITORIAL_BLOCKED_EXIT_CODE
    if status == "failed":
        return EDITORIAL_HARD_FINDINGS_EXIT_CODE
    return 0


def build_report(
    *,
    project: str,
    inputs: Mapping[str, Any],
    metrics: Mapping[str, Any],
    findings: Sequence[Finding],
    profile: AcceptanceProfile,
) -> dict[str, Any]:
    """Build the canonical metrics JSON report."""

    finding_dicts = [finding.to_dict() for finding in findings]
    counts = severity_counts(finding_dicts)
    status = status_from_counts(counts, fail_on_warnings=profile.fail_on_warnings)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now_iso(),
        "project": project,
        "worker_version": __version__,
        "profile": profile.to_dict(),
        "inputs": _json_ready(dict(inputs)),
        "metrics": _json_ready(dict(metrics)),
        "findings": finding_dicts,
        "summary": {
            "status": status,
            "finding_counts": counts,
            "findings_total": len(finding_dicts),
        },
    }


def write_json_report(report: Mapping[str, Any], destination: Path) -> None:
    """Write a canonical JSON report."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(_json_ready(dict(report)), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_acceptance_profile(
    profile_config: Path | None = None,
    profile_name: str = "local-preview",
) -> AcceptanceProfile:
    """Load a built-in or YAML-defined editorial acceptance profile."""

    if profile_config is None:
        raw_profile = _BUILTIN_PROFILES.get(profile_name)
        if raw_profile is None:
            raise ValueError(f"Unknown built-in editorial profile: {profile_name}")
        return _profile_from_mapping(profile_name, raw_profile)

    raw = yaml.safe_load(profile_config.read_text(encoding="utf-8")) or {}
    profiles = raw.get("profiles") if isinstance(raw, Mapping) else None
    if not isinstance(profiles, Mapping):
        raise ValueError("Profile config must contain a 'profiles' mapping")
    raw_profile = profiles.get(profile_name)
    if not isinstance(raw_profile, Mapping):
        available = ", ".join(sorted(str(key) for key in profiles)) or "<none>"
        raise ValueError(
            f"Editorial profile {profile_name!r} not found (available: {available})"
        )
    return _profile_from_mapping(profile_name, raw_profile)


def _profile_from_mapping(name: str, raw: Mapping[str, Any]) -> AcceptanceProfile:
    markdown_raw = (
        raw.get("markdown") if isinstance(raw.get("markdown"), Mapping) else {}
    )
    pdf_raw = raw.get("pdf") if isinstance(raw.get("pdf"), Mapping) else {}
    docs_raw = (
        raw.get("documentation")
        if isinstance(raw.get("documentation"), Mapping)
        else {}
    )
    required_raw = markdown_raw.get("required_frontmatter_by_role", {})
    required_by_role: dict[str, tuple[str, ...]] = {}
    if isinstance(required_raw, Mapping):
        for role, fields in required_raw.items():
            required_by_role[str(role)] = tuple(
                str(field) for field in _as_sequence(fields)
            )

    return AcceptanceProfile(
        name=name,
        network=_as_bool(raw.get("network"), default=False),
        fail_on_warnings=_as_bool(raw.get("fail_on_warnings"), default=False),
        markdown=MarkdownProfile(
            locale_field=str(markdown_raw.get("locale_field") or "content_lang"),
            identity_key=str(markdown_raw.get("identity_key") or "content_id"),
            source_link_field=str(markdown_raw.get("source_link_field") or "source"),
            source_locale=_optional_str(markdown_raw.get("source_locale")),
            target_locales=tuple(
                str(locale)
                for locale in _as_sequence(markdown_raw.get("target_locales"))
            ),
            forbidden_frontmatter_keys=tuple(
                str(key)
                for key in _as_sequence(
                    markdown_raw.get("forbidden_frontmatter_keys")
                    or MarkdownProfile().forbidden_frontmatter_keys
                )
            ),
            required_frontmatter_by_role=required_by_role
            or MarkdownProfile().required_frontmatter_by_role,
            allowed_translation_status=tuple(
                str(status)
                for status in _as_sequence(
                    markdown_raw.get("allowed_translation_status")
                    or MarkdownProfile().allowed_translation_status
                )
            ),
            exclude_dirs=tuple(
                str(part)
                for part in _as_sequence(
                    markdown_raw.get("exclude_dirs") or DEFAULT_EXCLUDE_DIRS
                )
            ),
            skip_filenames=tuple(
                str(part)
                for part in _as_sequence(
                    markdown_raw.get("skip_filenames") or DEFAULT_SKIP_FILENAMES
                )
            ),
            long_token_warn_chars=int(markdown_raw.get("long_token_warn_chars") or 80),
        ),
        pdf=PdfProfile(
            low_text_page_threshold=int(pdf_raw.get("low_text_page_threshold") or 15),
            very_low_text_page_threshold=int(
                pdf_raw.get("very_low_text_page_threshold") or 5
            ),
            required_fonts=tuple(
                str(font) for font in _as_sequence(pdf_raw.get("required_fonts"))
            ),
            pdf_targets=_mapping_of_mappings(pdf_raw.get("pdf_targets") or {}),
        ),
        documentation=DocumentationProfile(
            fail_on_stale_worker_version=_as_bool(
                docs_raw.get("fail_on_stale_worker_version"), default=False
            ),
            fail_on_stale_page_count=_as_bool(
                docs_raw.get("fail_on_stale_page_count"), default=False
            ),
        ),
    )


def _normalize_id_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower())


def _json_ready(value: Any) -> Any:
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Mapping):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _as_sequence(value: Any) -> Sequence[Any]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)):
        return (value,)
    if isinstance(value, Sequence):
        return value
    return (value,)


def _as_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _mapping_of_mappings(value: Any) -> Mapping[str, Mapping[str, int]]:
    if not isinstance(value, Mapping):
        return {}
    result: dict[str, Mapping[str, int]] = {}
    for key, nested in value.items():
        if not isinstance(nested, Mapping):
            continue
        result[str(key)] = {
            str(nested_key): int(nested_value)
            for nested_key, nested_value in nested.items()
            if isinstance(nested_value, int)
            or (isinstance(nested_value, str) and nested_value.isdigit())
        }
    return result


_BUILTIN_PROFILES: Mapping[str, Mapping[str, Any]] = {
    "local-preview": {
        "network": False,
        "fail_on_warnings": False,
        "markdown": {
            "forbidden_frontmatter_keys": ["lang", "language", "lang-version"],
        },
        "pdf": {},
    },
    "release-candidate": {
        "network": False,
        "fail_on_warnings": False,
        "markdown": {
            "forbidden_frontmatter_keys": ["lang", "language", "lang-version"],
        },
        "pdf": {},
        "documentation": {
            "fail_on_stale_worker_version": True,
            "fail_on_stale_page_count": True,
        },
    },
    "publish-final": {
        "network": False,
        "fail_on_warnings": True,
        "markdown": {
            "forbidden_frontmatter_keys": ["lang", "language", "lang-version"],
        },
        "pdf": {},
        "documentation": {
            "fail_on_stale_worker_version": True,
            "fail_on_stale_page_count": True,
        },
    },
    "docs-only": {
        "network": False,
        "fail_on_warnings": False,
        "markdown": {
            "forbidden_frontmatter_keys": ["lang", "language", "lang-version"],
        },
        "pdf": {},
    },
    "multilingual-release-candidate": {
        "network": False,
        "markdown": {
            "locale_field": "content_lang",
            "identity_key": "content_id",
            "source_link_field": "source",
            "source_locale": "ja",
            "target_locales": ["pl", "hr", "no"],
            "forbidden_frontmatter_keys": ["lang", "language", "lang-version"],
            "required_frontmatter_by_role": {
                "source": ["content_id", "content_lang"],
                "target": ["content_id", "content_lang", "source", "status"],
            },
            "allowed_translation_status": ["draft", "in-review", "approved"],
        },
        "pdf": {
            "low_text_page_threshold": 15,
            "very_low_text_page_threshold": 5,
            "required_fonts": [
                "DejaVuSerif",
                "DejaVuSans",
                "DejaVuSansMono",
                "TwemojiMozilla",
                "ProjectCJK-Regular",
            ],
        },
        "documentation": {
            "fail_on_stale_worker_version": True,
            "fail_on_stale_page_count": True,
        },
    },
}


__all__ = [
    "AcceptanceProfile",
    "AcceptanceStatus",
    "DocumentationProfile",
    "EDITORIAL_BLOCKED_EXIT_CODE",
    "EDITORIAL_HARD_FINDINGS_EXIT_CODE",
    "EDITORIAL_INVALID_PROFILE_EXIT_CODE",
    "EDITORIAL_REPORT_READ_EXIT_CODE",
    "Finding",
    "MarkdownProfile",
    "PdfProfile",
    "SCHEMA_VERSION",
    "Severity",
    "build_report",
    "exit_code_for_status",
    "load_acceptance_profile",
    "make_finding",
    "relative_artifact",
    "severity_counts",
    "stable_finding_id",
    "status_from_counts",
    "write_json_report",
]
