"""Collect all font declarations across style assets."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

DEFAULT_EXTENSIONS = {".css", ".scss", ".sass", ".less", ".md", ".html"}
DEFAULT_SOURCES = ["assets", "docs", "content", "publish"]

FONT_RE = re.compile(r"font-family\s*:\s*([^;{}]+)", re.IGNORECASE)
INLINE_FONT_RE = re.compile(r"font-family\s*=\s*\"([^\"]+)\"", re.IGNORECASE)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def discover_files(sources: Iterable[str], extensions: Iterable[str]) -> List[Path]:
    ext_set = {ext.lower() for ext in extensions}
    files: List[Path] = []
    for source in sources:
        base = Path(source)
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in ext_set:
                files.append(path)
    return sorted(files)


def normalize_family(entry: str) -> List[str]:
    cleaned = entry.replace("\n", " ")
    families = []
    for token in cleaned.split(","):
        token = token.strip().strip("'\"")
        if token:
            families.append(token)
    return families


def collect_fonts(files: Iterable[Path]) -> Dict[str, Dict[str, int]]:
    usage: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for path in files:
        text = read_text(path)
        matches: List[Tuple[str, ...]] = []
        matches.extend((match.group(1),) for match in FONT_RE.finditer(text))
        matches.extend((match.group(1),) for match in INLINE_FONT_RE.finditer(text))
        if not matches:
            continue
        for (entry,) in matches:
            for family in normalize_family(entry):
                usage[family][str(path)] += 1
    return usage


def build_report(usage: Dict[str, Dict[str, int]], files: List[Path]) -> Dict:
    fonts = [
        {
            "font": family,
            "occurrences": sum(paths.values()),
            "files": sorted({"path": path, "count": count} for path, count in paths.items()),
        }
        for family, paths in sorted(usage.items(), key=lambda item: (-sum(item[1].values()), item[0]))
    ]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": [str(path) for path in files],
        "fonts": fonts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sources",
        nargs="*",
        default=DEFAULT_SOURCES,
        help="Directories to scan recursively (default: assets, docs, content, publish).",
    )
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=sorted(DEFAULT_EXTENSIONS),
        help="File extensions to include (default: css, scss, sass, less, md, html).",
    )
    parser.add_argument(
        "--output",
        default="build/font-report.json",
        help="Path to the JSON report (default: build/font-report.json)",
    )
    args = parser.parse_args()

    files = discover_files(args.sources, args.extensions)
    usage = collect_fonts(files)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(build_report(usage, files), indent=2), encoding="utf-8")
    print(f"Erfasste Schriftdefinitionen: {len(usage)}")


if __name__ == "__main__":
    main()
