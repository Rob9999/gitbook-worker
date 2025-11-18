"""Scan Markdown sources for emoji usage and emit a JSON report."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

from .emoji_utils import (
    EmojiRecord,
    iter_emoji_sequences,
    summarize_emojis,
)


DEFAULT_SOURCES = ["content", "docs", "publish"]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def discover_markdown_files(sources: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for source in sources:
        base = Path(source)
        if not base.exists():
            continue
        for path in base.rglob("*.md"):
            if path.is_file():
                files.append(path)
    return sorted(files)


def collect_emojis(paths: Iterable[Path]) -> Dict[str, Dict[str, int]]:
    per_file: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for path in paths:
        text = read_text(path)
        for glyph in iter_emoji_sequences(text):
            per_file[glyph][str(path)] += 1
    return per_file


def build_records(per_file: Dict[str, Dict[str, int]]) -> List[EmojiRecord]:
    glyphs: List[str] = []
    for glyph, mapping in per_file.items():
        for _ in range(sum(mapping.values())):
            glyphs.append(glyph)
    return summarize_emojis(glyphs)


def render_inventory_table(records: List[EmojiRecord]) -> str:
    if not records:
        return "| Emoji | Codepoints | CLDR-Name | Vorkommen |\n| --- | --- | --- | --- |\n| (keine) | – | – | 0 |"
    lines = ["| Emoji | Codepoints | CLDR-Name | Vorkommen |", "| --- | --- | --- | --- |"]
    for record in records:
        lines.append(
            f"| {record.glyph} | {record.codepoints} | {record.name} | {record.count} |"
        )
    return "\n".join(lines)


def build_report(records: List[EmojiRecord], per_file: Dict[str, Dict[str, int]], files: List[Path]) -> Dict:
    total = sum(record.count for record in records)
    unique = len(records)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": [str(path) for path in files],
        "totals": {
            "unique": unique,
            "occurrences": total,
        },
        "emojis": [
            {
                "emoji": record.glyph,
                "name": record.name,
                "codepoints": record.codepoints,
                "asset_slug": record.asset_slug,
                "count": record.count,
                "files": sorted(
                    (
                        {"path": path, "count": count}
                        for path, count in per_file[record.glyph].items()
                    ),
                    key=lambda entry: entry["path"],
                ),
            }
            for record in records
        ],
    }


def pick_samples(records: List[EmojiRecord], limit: int = 6) -> List[str]:
    if not records:
        return ["🙂", "🚀", "⚙"][:limit]
    result: List[str] = []
    for record in records:
        if record.glyph not in result:
            result.append(record.glyph)
        if len(result) >= limit:
            break
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sources",
        nargs="*",
        default=DEFAULT_SOURCES,
        help="Directories to scan recursively for Markdown files.",
    )
    parser.add_argument(
        "--output",
        default="build/emoji-report.json",
        help="Path to the JSON report (default: build/emoji-report.json)",
    )
    parser.add_argument(
        "--samples-output",
        default="build/emoji-samples.json",
        help="Where to store helper samples for the harness.",
    )
    args = parser.parse_args()

    files = discover_markdown_files(args.sources)
    per_file = collect_emojis(files)
    records = build_records(per_file)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(build_report(records, per_file, files), indent=2), encoding="utf-8")

    samples = {
        "samples": pick_samples(records, limit=6),
        "inline": " ".join(pick_samples(records, limit=4)),
    }
    Path(args.samples_output).write_text(json.dumps(samples, indent=2), encoding="utf-8")

    print(
        f"Gefundene Emojis: {len(records)} einzigartig, {sum(r.count for r in records)} insgesamt."
    )


if __name__ == "__main__":
    main()
