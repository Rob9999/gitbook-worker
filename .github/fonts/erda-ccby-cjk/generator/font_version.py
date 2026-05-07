"""Version metadata for the ERDA CC-BY generated font family."""

from __future__ import annotations

import datetime as _datetime

ERDA_FONT_VERSION = "1.4.0"
ERDA_FONT_VERSION_DATE = "2026-05-07"


def font_build_timestamp() -> str:
    """Return the timestamp used to invalidate OS and application font caches."""

    return _datetime.datetime.now().strftime("%Y%m%d.%H%M%S")


def font_version_string(timestamp: str) -> str:
    """Return the OpenType name-table version string for generated ERDA fonts."""

    return f"Version {ERDA_FONT_VERSION}+{timestamp}"


def unique_font_identifier(font_family: str, timestamp: str) -> str:
    """Return a per-build unique identifier while preserving the family semver."""

    return f"{font_family} Regular {ERDA_FONT_VERSION}+{timestamp}"
