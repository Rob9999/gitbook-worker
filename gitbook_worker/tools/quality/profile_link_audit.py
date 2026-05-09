"""Check external links in Markdown files selected by filename patterns."""

from __future__ import annotations

import argparse
import csv
import fnmatch
import re
from pathlib import Path
from typing import Iterable, Sequence

import requests

from gitbook_worker.tools.logging_config import get_logger

logger = get_logger(__name__)

LINK_PATTERN = re.compile(r"\[.*?\]\((https?://[^)]+)\)")
DEFAULT_FILENAME_PATTERN = "*profile*.md"
DEFAULT_TIMEOUT = 5.0


def iter_profile_files(
    root: Path, *, filename_patterns: Sequence[str] | None = None
) -> Iterable[Path]:
    """Yield Markdown files whose filename matches at least one pattern."""

    patterns = tuple(filename_patterns or (DEFAULT_FILENAME_PATTERN,))
    normalized_patterns = tuple(pattern.lower() for pattern in patterns)
    for path in root.rglob("*.md"):
        filename = path.name.lower()
        if any(fnmatch.fnmatch(filename, pattern) for pattern in normalized_patterns):
            yield path


def check_links(
    files: Iterable[Path], *, timeout: float = DEFAULT_TIMEOUT
) -> list[list[str]]:
    """Return CSV rows describing failing HTTP checks."""

    broken: list[list[str]] = []
    for markdown_file in files:
        try:
            lines = markdown_file.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            broken.append([str(markdown_file), "", "", "ERR", str(exc)])
            continue
        for line_number, line in enumerate(lines, 1):
            for url in LINK_PATTERN.findall(line):
                try:
                    response = requests.head(url, allow_redirects=True, timeout=timeout)
                    if response.status_code >= 400:
                        broken.append(
                            [
                                str(markdown_file),
                                str(line_number),
                                url,
                                str(response.status_code),
                                response.reason,
                            ]
                        )
                except (
                    Exception
                ) as exc:  # noqa: BLE001 - network diagnostics record all failures
                    broken.append(
                        [str(markdown_file), str(line_number), url, "ERR", str(exc)]
                    )
    return broken


def write_report(rows: list[list[str]], output: Path) -> None:
    """Write link audit rows to a CSV file."""

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["File", "Line", "URL", "Status", "Error"])
        writer.writerows(rows)


def build_arg_parser(
    *,
    default_filename_pattern: str = DEFAULT_FILENAME_PATTERN,
    default_output: str = "profile_link_report.csv",
    description: str | None = None,
) -> argparse.ArgumentParser:
    """Build the CLI parser."""

    parser = argparse.ArgumentParser(description=description or __doc__)
    parser.add_argument("--root", default=".", help="Root directory to search")
    parser.add_argument(
        "--filename-pattern",
        action="append",
        dest="filename_patterns",
        default=None,
        help=(
            "Filename glob for Markdown files to check; repeatable. "
            f"Default: {default_filename_pattern}"
        ),
    )
    parser.add_argument("--output", default=default_output, help="Output CSV filename")
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="HTTP timeout in seconds (default: 5)",
    )
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    default_filename_pattern: str = DEFAULT_FILENAME_PATTERN,
    default_output: str = "profile_link_report.csv",
    description: str | None = None,
) -> int:
    """Run the filtered profile link audit."""

    parser = build_arg_parser(
        default_filename_pattern=default_filename_pattern,
        default_output=default_output,
        description=description,
    )
    args = parser.parse_args(argv)

    root = Path(args.root)
    patterns = tuple(args.filename_patterns or (default_filename_pattern,))
    files = list(iter_profile_files(root, filename_patterns=patterns))
    if not files:
        logger.info("No Markdown files found for patterns: %s", ", ".join(patterns))
        return 0

    rows = check_links(files, timeout=args.timeout)
    write_report(rows, Path(args.output))
    logger.info("Report written to %s. %d problem links found.", args.output, len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
