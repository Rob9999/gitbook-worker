"""Tools to audit links, media, and annotations in Markdown files."""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple

import requests
from requests import Response
import tqdm

from tools.logging_config import get_logger

logger = get_logger(__name__)


_LINK_PATTERN = re.compile(r"\[.*?\]\((https?://[^)]+)\)")
_IMAGE_PATTERN = re.compile(r"!\[.*?\]\((.*?)\)")
_HEADING_PATTERN = re.compile(r"^(#{1,6})\s*(.+)")
_CITATION_PATTERN = re.compile(r"^\s*([0-9]+)\.\s")
_TODO_PATTERN = re.compile(r"\b(TODO|FIXME)\b")
_DEFAULT_TIMEOUT = 5.0


@dataclass
class HttpFinding:
    status: str
    file: Path
    url: str
    lineno: int
    line: str
    status_code: str
    error: str

    def to_csv_row(self) -> List[str]:
        return [
            self.status,
            str(self.file),
            self.url,
            str(self.lineno),
            self.line,
            self.status_code,
            self.error,
        ]


@dataclass
class ImageFinding:
    file: Path
    lineno: int
    target: str
    error: str


@dataclass
class DuplicateHeading:
    file: Path
    lineno: int
    title: str
    first_seen: str


@dataclass
class CitationGap:
    file: Path
    missing_numbers: List[int]


@dataclass
class TodoEntry:
    file: Path
    lineno: int
    line: str


def _read_markdown_lines(md_file: Path) -> Iterator[Tuple[int, str]]:
    try:
        with md_file.open(encoding="utf-8") as handle:
            for lineno, line in enumerate(handle, 1):
                yield lineno, line.rstrip("\n")
    except OSError as exc:
        logger.warning("Failed to open %s: %s", md_file, exc)


def _request_head(url: str, timeout: float) -> Optional[Response]:
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code >= 400 or response.status_code == 405:
            response = requests.get(url, timeout=timeout, allow_redirects=True)
        return response
    except Exception as exc:  # noqa: BLE001 - we want to record all failures
        logger.debug("Request for %s failed: %s", url, exc)
        return None


def check_http_links(
    md_files: Iterable[Path],
    report_csv: Path,
    *,
    timeout: float = _DEFAULT_TIMEOUT,
    show_progress: bool = True,
) -> Tuple[List[HttpFinding], List[HttpFinding]]:
    report_csv.parent.mkdir(parents=True, exist_ok=True)
    broken: List[HttpFinding] = []
    good: List[HttpFinding] = []

    with report_csv.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["GO", "File", "Link", "Line#", "Line", "Status Code", "Error"])
        md_list = list(md_files)
        for md in tqdm.tqdm(md_list, desc="Files", unit="file", disable=not show_progress):
            for lineno, line in _read_markdown_lines(md):
                for url in _LINK_PATTERN.findall(line):
                    response = _request_head(url, timeout)
                    if response is None:
                        finding = HttpFinding("💥❌", md, url, lineno, line, "unknown", "request failed")
                        broken.append(finding)
                        writer.writerow(finding.to_csv_row())
                        logger.info("❌ Broken link (request failed) in %s: %s (line %s)", md, url, lineno)
                        continue

                    status_code = response.status_code
                    if status_code >= 400:
                        finding = HttpFinding(
                            "❌",
                            md,
                            url,
                            lineno,
                            line,
                            str(status_code),
                            response.reason or "",
                        )
                        broken.append(finding)
                        writer.writerow(finding.to_csv_row())
                        logger.info("❌ Broken link in %s: %s (line %s)", md, url, lineno)
                    else:
                        finding = HttpFinding(
                            "✅",
                            md,
                            url,
                            lineno,
                            line,
                            str(status_code),
                            "OK",
                        )
                        good.append(finding)
                        writer.writerow(finding.to_csv_row())
                        logger.info("✅ Good link in %s: %s (line %s)", md, url, lineno)

    logger.info("HTTP link check finished: %s broken, %s good", len(broken), len(good))
    return broken, good


def check_images(md_files: Iterable[Path], *, timeout: float = _DEFAULT_TIMEOUT) -> List[ImageFinding]:
    findings: List[ImageFinding] = []
    for md in md_files:
        for lineno, line in _read_markdown_lines(md):
            for target in _IMAGE_PATTERN.findall(line):
                if target.startswith("http"):
                    response = _request_head(target, timeout)
                    if response is None or response.status_code >= 400:
                        error = "request failed" if response is None else str(response.status_code)
                        findings.append(ImageFinding(md, lineno, target, error))
                else:
                    full_path = (md.parent / target).resolve()
                    if not full_path.exists():
                        findings.append(ImageFinding(md, lineno, str(full_path), "not found"))
    return findings


def check_duplicate_headings(md_files: Iterable[Path]) -> List[DuplicateHeading]:
    seen: dict[str, str] = {}
    duplicates: List[DuplicateHeading] = []
    for md in md_files:
        for lineno, line in _read_markdown_lines(md):
            match = _HEADING_PATTERN.match(line)
            if not match:
                continue
            title = match.group(2).strip().lower()
            ref = f"{md}:{lineno}"
            if title in seen:
                duplicates.append(DuplicateHeading(md, lineno, title, seen[title]))
            else:
                seen[title] = ref
    return duplicates


def check_citation_numbering(md_files: Iterable[Path]) -> List[CitationGap]:
    gaps: List[CitationGap] = []
    for md in md_files:
        numbers: List[int] = []
        for _, line in _read_markdown_lines(md):
            match = _CITATION_PATTERN.match(line)
            if match:
                numbers.append(int(match.group(1)))
        if numbers:
            expected = set(range(1, max(numbers) + 1))
            missing = sorted(expected - set(numbers))
            if missing:
                gaps.append(CitationGap(md, missing))
    return gaps


def list_todos(md_files: Iterable[Path]) -> List[TodoEntry]:
    todos: List[TodoEntry] = []
    for md in md_files:
        for lineno, line in _read_markdown_lines(md):
            if _TODO_PATTERN.search(line):
                todos.append(TodoEntry(md, lineno, line.strip()))
    return todos


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Markdown documents for link quality issues.")
    parser.add_argument("markdown", nargs="*", type=Path, help="Markdown files to inspect.")
    parser.add_argument(
        "--root",
        type=Path,
        help=(
            "Recursively discover Markdown files below this directory. "
            "Positional Markdown arguments are merged with the discovered files."
        ),
    )
    parser.add_argument(
        "--format",
        choices=["log"],
        default="log",
        help="Deprecated option retained for backward compatibility (no effect).",
    )
    parser.add_argument("--http-report", type=Path, help="Write HTTP link check CSV report to this path.")
    parser.add_argument("--timeout", type=float, default=_DEFAULT_TIMEOUT, help="Request timeout in seconds (default: 5).")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress bar output.")
    parser.add_argument("--check-images", action="store_true", help="Check remote and local images referenced in Markdown.")
    parser.add_argument("--check-duplicate-headings", action="store_true", help="Detect duplicate headings across files.")
    parser.add_argument("--check-citations", action="store_true", help="Verify consecutive numbering of citations.")
    parser.add_argument("--list-todos", action="store_true", help="List TODO and FIXME markers.")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_args(argv)
    md_files: List[Path] = []

    if args.markdown:
        explicit_files = [path for path in args.markdown if path.is_file()]
        skipped = set(args.markdown) - set(explicit_files)
        for missing in skipped:
            logger.warning("Skipping missing file: %s", missing)
        md_files.extend(explicit_files)

    if args.root:
        root_path = args.root
        if not root_path.exists():
            logger.warning("Root path does not exist: %s", root_path)
        else:
            discovered = sorted(path for path in root_path.rglob("*.md") if path.is_file())
            logger.info("Discovered %s Markdown files under %s", len(discovered), root_path)
            md_files.extend(discovered)

    # Deduplicate while preserving order (explicit files first, then discovered files).
    seen: set[Path] = set()
    ordered: List[Path] = []
    for candidate in md_files:
        if candidate not in seen:
            seen.add(candidate)
            ordered.append(candidate)
    md_files = ordered

    if args.http_report:
        broken, good = check_http_links(
            md_files,
            args.http_report,
            timeout=args.timeout,
            show_progress=not args.no_progress,
        )
        if broken:
            logger.warning("Found %s broken links. See %s for details.", len(broken), args.http_report)
        else:
            logger.info("No broken links detected.")
        logger.info("Recorded %s valid links.", len(good))

    if args.check_images:
        findings = check_images(md_files, timeout=args.timeout)
        for finding in findings:
            logger.warning("Missing image in %s (line %s): %s [%s]", finding.file, finding.lineno, finding.target, finding.error)
        logger.info("Image check finished: %s issues detected.", len(findings))

    if args.check_duplicate_headings:
        duplicates = check_duplicate_headings(md_files)
        for dup in duplicates:
            logger.warning(
                "Duplicate heading '%s' in %s (line %s); first seen at %s",
                dup.title,
                dup.file,
                dup.lineno,
                dup.first_seen,
            )
        logger.info("Duplicate heading check finished: %s duplicates detected.", len(duplicates))

    if args.check_citations:
        gaps = check_citation_numbering(md_files)
        for gap in gaps:
            logger.warning("Citation gaps in %s: missing numbers %s", gap.file, ", ".join(map(str, gap.missing_numbers)))
        logger.info("Citation numbering check finished: %s files with gaps.", len(gaps))

    if args.list_todos:
        todos = list_todos(md_files)
        for todo in todos:
            logger.info("TODO in %s (line %s): %s", todo.file, todo.lineno, todo.line)
        logger.info("TODO scan finished: %s entries found.", len(todos))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
