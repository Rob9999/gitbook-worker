from pathlib import Path
from typing import Iterable, Sequence

from gitbook_worker.tools.quality.profile_link_audit import (
    check_links,
    main as _profile_link_audit_main,
    iter_profile_files,
    write_report,
)

LEGACY_FILENAME_PATTERN = "*staatenprofil*.md"
LEGACY_OUTPUT = "staatenprofil_link_report.csv"

__all__ = [
    "LEGACY_FILENAME_PATTERN",
    "LEGACY_OUTPUT",
    "check_links",
    "iter_staatenprofil_files",
    "main",
    "write_report",
]


def iter_staatenprofil_files(root: Path) -> Iterable[Path]:
    """Yield Markdown files matching the legacy Staatenprofil filename pattern."""

    return iter_profile_files(root, filename_patterns=(LEGACY_FILENAME_PATTERN,))


def main(argv: Sequence[str] | None = None) -> int:
    """Run the legacy Staatenprofil link audit entry point."""

    return _profile_link_audit_main(
        argv,
        default_filename_pattern=LEGACY_FILENAME_PATTERN,
        default_output=LEGACY_OUTPUT,
        description=(
            "Legacy alias for profile_link_audit with "
            "--filename-pattern *staatenprofil*.md"
        ),
    )


if __name__ == "__main__":
    raise SystemExit(main())
