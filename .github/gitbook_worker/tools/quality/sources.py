"""Utilities for extracting source sections from Markdown files."""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
)

from tools.logging_config import get_logger

logger = get_logger(__name__)


_SOURCE_HEADERS: Mapping[str, List[str]] = {
    "de": ["Quelle", "Quellen", "Quellen & Verweise", "Quellen und Verweise"],
    "en": ["Source", "Sources", "References", "Sources & References"],
}


@dataclass
class SourceEntry:
    """Representation of a single source line inside a Markdown file."""

    file: Path
    name: str
    link: Optional[str]
    numbering: Optional[str]
    comment: Optional[str]
    kind: str
    lineno: int
    line: str

    def to_csv_row(self) -> List[str]:
        return [
            str(self.file),
            self.name,
            self.link or "",
            self.numbering or "",
            self.comment or "",
            self.kind,
            str(self.lineno),
            self.line,
        ]


def _normalise_language(language: str) -> str:
    lang = (language or "").lower()
    if lang in _SOURCE_HEADERS:
        return lang
    logger.debug("Unknown language '%s', defaulting to 'de'", lang)
    return "de"


def get_header_pattern(language: str = "de", max_level: int = 6) -> re.Pattern[str]:
    """Return a compiled regex that matches language-specific source headers."""

    lang = _normalise_language(language)
    words: List[str] = []
    for key in {lang, "de", "en"}:
        words.extend(_SOURCE_HEADERS.get(key, []))
    # Remove duplicates while preserving order.
    seen: set[str] = set()
    unique_words = [w for w in words if not (w in seen or seen.add(w))]
    escaped = "|".join(re.escape(word) for word in unique_words)
    numbering = r"(?:\d+(?:\.\d+)*\.?)?"
    return re.compile(
        rf"^(#{{1,{max_level}}})\s*{numbering}\s*(?:{escaped})", re.IGNORECASE
    )


def get_list_item_pattern() -> re.Pattern[str]:
    return re.compile(
        r"^(?:\s*)(?:\d+[\.\)-]|[a-zA-Z][\.\)-]|[*\-+])\s+.*(?:\n(?!\s*(?:\d+[\.\)-]|[a-zA-Z][\.\)-]|[*\-+])\s).*)*",
        re.MULTILINE,
    )


def extract_multiline_list_items(text: str) -> List[str]:
    if not isinstance(text, str):
        raise ValueError("Input text must be a string.")
    return get_list_item_pattern().findall(text)


def _iter_markdown_lines(md_file: Path) -> Iterator[tuple[int, str]]:
    try:
        with md_file.open(encoding="utf-8") as handle:
            for lineno, line in enumerate(handle, 1):
                yield lineno, line.rstrip("\n")
    except OSError as exc:
        logger.warning("Cannot open %s: %s", md_file, exc)


def extract_sources_from_file(
    md_file: Path,
    *,
    language: str = "de",
    max_level: int = 6,
) -> List[MutableMapping[str, MutableMapping[str, object]]]:
    header_pattern = get_header_pattern(language, max_level)
    list_pattern = get_list_item_pattern()

    entries: List[MutableMapping[str, MutableMapping[str, object]]] = []
    in_section = False
    current_level: Optional[int] = None

    for lineno, line in _iter_markdown_lines(md_file):
        header_match = header_pattern.match(line)
        if header_match:
            in_section = True
            current_level = len(header_match.group(1))
            logger.debug("Entered sources section in %s at line %s", md_file, lineno)
            continue

        if in_section and line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            if current_level is not None and level <= current_level:
                logger.debug(
                    "Leaving sources section in %s at line %s", md_file, lineno
                )
                break

        list_match = list_pattern.match(line)
        if in_section and list_match:
            numbering = list_match.group(0).strip()
            name_match = re.search(r"^\s*([0-9a-z\*]+[\.) ]|[-*+])\s+(.*)", line)
            raw_name = name_match.group(2).strip() if name_match else ""
            name = re.sub(r"^[0-9a-z\*]+[\.) ]\s*", "", raw_name)
            name = re.sub(r'^"(.*)"$', r"\1", name)
            name = re.sub(r"\[.*?\]\(.*?\)", "", name).strip()

            link_match = re.search(r"\[.*?\]\((.*?)\)", line)
            link = link_match.group(1) if link_match else None
            if link_match and not name:
                name = link_match.group(0).split("]")[0].strip()

            comment_match = re.search(r"\((.*?)\)", line)
            comment = comment_match.group(1) if comment_match else None

            if not name:
                name = f"Referenz zu Zeile {lineno}"

            entries.append(
                {
                    name: {
                        "numbering": numbering,
                        "link": link,
                        "comment": comment,
                        "lineno": lineno,
                        "line": line.strip(),
                        "kind": "external",
                    }
                }
            )
    return entries


def extract_sources(
    md_files: Iterable[Path],
    *,
    language: str = "de",
    max_level: int = 6,
) -> Dict[str, List[MutableMapping[str, MutableMapping[str, object]]]]:
    extracted: Dict[str, List[MutableMapping[str, MutableMapping[str, object]]]] = {}
    for md in md_files:
        if not md.is_file():
            logger.warning("Skipping missing file: %s", md)
            continue
        entries = extract_sources_from_file(md, language=language, max_level=max_level)
        if entries:
            extracted[str(md)] = entries
    return extracted


def write_sources_csv(entries: Iterable[SourceEntry], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["File", "Name", "Link", "Numbering", "Comment", "Kind", "LineNo", "Line"]
        )
        for entry in entries:
            writer.writerow(entry.to_csv_row())
    logger.info("Sources extracted to %s", destination)


def extract_to_csv(
    md_files: Iterable[Path],
    destination: Path,
    *,
    language: str = "de",
    max_level: int = 6,
) -> None:
    raw_entries = extract_sources(md_files, language=language, max_level=max_level)
    csv_rows: List[SourceEntry] = []
    for file_name, entries in raw_entries.items():
        for entry in entries:
            for name, metadata in entry.items():
                if not metadata:
                    continue
                number = str(metadata.get("numbering") or "").strip()
                clean_name = re.sub(r"^[0-9a-z\*]+[\.) ]\s*", "", name)
                csv_rows.append(
                    SourceEntry(
                        file=Path(file_name),
                        name=clean_name,
                        link=str(metadata.get("link") or "") or None,
                        numbering=number or None,
                        comment=str(metadata.get("comment") or "") or None,
                        kind=str(metadata.get("kind") or "external"),
                        lineno=int(metadata.get("lineno") or 0),
                        line=str(metadata.get("line") or ""),
                    )
                )
    if not csv_rows:
        logger.warning("No sources found in markdown files.")
        return
    write_sources_csv(csv_rows, destination)


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract source references from Markdown files."
    )
    parser.add_argument(
        "markdown", nargs="*", type=Path, help="Markdown files to scan."
    )
    parser.add_argument(
        "--root",
        type=Path,
        help=(
            "Recursively discover Markdown files below this directory. "
            "Positional Markdown arguments are merged with the discovered files."
        ),
    )
    parser.add_argument(
        "-o", "--output", required=True, type=Path, help="Destination CSV file."
    )
    parser.add_argument(
        "-l",
        "--language",
        default="de",
        help="Language used for the source headings (default: de).",
    )
    parser.add_argument(
        "--max-level",
        type=int,
        default=6,
        help="Maximum Markdown heading level to treat as a sources section (default: 6).",
    )
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
            discovered = sorted(
                path for path in root_path.rglob("*.md") if path.is_file()
            )
            logger.info(
                "Discovered %s Markdown files under %s", len(discovered), root_path
            )
            md_files.extend(discovered)

    # Deduplicate while preserving order (explicit files first, then discovered files).
    seen: set[Path] = set()
    ordered: List[Path] = []
    for candidate in md_files:
        if candidate not in seen:
            seen.add(candidate)
            ordered.append(candidate)

    if not ordered:
        logger.error("No Markdown files provided or discovered. Nothing to do.")
        return 1

    extract_to_csv(
        ordered, args.output, language=args.language, max_level=args.max_level
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
