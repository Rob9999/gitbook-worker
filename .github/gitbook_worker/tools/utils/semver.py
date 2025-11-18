"""Semantic version helpers for configuration files."""

from __future__ import annotations

import re
from typing import Any

_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


class SemVerError(ValueError):
    """Raised when a value does not comply with Semantic Versioning."""


def ensure_semver(value: Any, *, field: str, default: str | None = None) -> str:
    """Validate ``value`` as semantic version and return it.

    Args:
        value: Raw value extracted from configuration.
        field: Human readable field name used in error messages.
        default: Fallback when ``value`` is ``None`` or empty.

    Returns:
        Normalised semantic version string.

    Raises:
        SemVerError: If no usable value is provided or it violates SemVer.
    """

    candidate = _pick_candidate(value, default=default)
    if candidate is None:
        raise SemVerError(f"{field} muss gesetzt sein und SemVer (MAJOR.MINOR.PATCH) folgen.")

    if not _SEMVER_RE.fullmatch(candidate):
        raise SemVerError(
            f"{field} muss einer SemVer-Version entsprechen (z. B. 1.2.3). Erhalten: {candidate!r}"
        )

    return candidate


def is_semver(value: Any) -> bool:
    """Return ``True`` when ``value`` matches the SemVer specification."""

    if value is None:
        return False
    candidate = str(value).strip()
    if not candidate:
        return False
    return bool(_SEMVER_RE.fullmatch(candidate))


def _pick_candidate(value: Any, *, default: str | None) -> str | None:
    if value is None:
        return default
    candidate = str(value).strip()
    if candidate:
        return candidate
    return default


__all__ = ["SemVerError", "ensure_semver", "is_semver"]

