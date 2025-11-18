#!/usr/bin/env python3
# Check external links in files named *staatenprofil*.md.
"""Check external links in files named *staatenprofil*.md."""

import argparse
import csv
import logging
import re
from pathlib import Path
from typing import Iterable, List

import requests

logger = logging.getLogger(__name__)


LINK_PATTERN = re.compile(r"\[.*?\]\((https?://[^)]+)\)")


def iter_staatenprofil_files(root: Path) -> Iterable[Path]:
    """Yield Markdown files containing 'staatenprofil' in the file name."""

    for path in root.rglob("*.md"):
        if "staatenprofil" in path.name.lower():
            yield path


def check_links(files: Iterable[Path]) -> List[List[str]]:
    """Return rows describing broken links."""

    broken: List[List[str]] = []
    for md in files:
        with md.open(encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                for url in LINK_PATTERN.findall(line):
                    try:
                        resp = requests.head(url, allow_redirects=True, timeout=5)
                        if resp.status_code >= 400:
                            broken.append(
                                [
                                    str(md),
                                    str(lineno),
                                    url,
                                    str(resp.status_code),
                                    resp.reason,
                                ]
                            )
                    except Exception as exc:  # network failure or similar
                        broken.append([str(md), str(lineno), url, "ERR", str(exc)])
    return broken


def write_report(rows: List[List[str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["File", "Line", "URL", "Status", "Error"])
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check links in staatenprofil markdown files")
    parser.add_argument("--root", default=".", help="Root directory to search")
    parser.add_argument(
        "--output", default="staatenprofil_link_report.csv", help="Output CSV filename"
    )
    args = parser.parse_args()

    root = Path(args.root)
    files = list(iter_staatenprofil_files(root))
    if not files:
        logger.info("No staatenprofil markdown files found.")
        return

    rows = check_links(files)
    write_report(rows, Path(args.output))
    logger.info(
        "Report written to %s. %d problem links found.", args.output, len(rows)
    )


if __name__ == "__main__":
    main()
