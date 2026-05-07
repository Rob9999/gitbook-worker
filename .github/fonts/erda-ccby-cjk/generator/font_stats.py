"""TTF statistics and target checks for ERDA CC-BY fallback fonts."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from fontTools.ttLib import TTFont

from coverage_targets import (
    STAT_RANGES,
    TARGET_REQUIREMENTS,
    target_cjk_long_section_chars,
    target_cjk_long_sample_chars,
)

GENERATOR_DIR = Path(__file__).resolve().parent
DEFAULT_FONT_DIR = GENERATOR_DIR.parent / "true-type"


@dataclass(frozen=True)
class TargetResult:
    range_name: str
    actual: int
    minimum: int
    passed: bool


@dataclass(frozen=True)
class FontStats:
    path: str
    family_name: str | None
    full_name: str | None
    version: str | None
    maxp_num_glyphs: int
    glyph_order_count: int
    cmap_codepoints: int
    range_counts: dict[str, int]
    target_results: list[TargetResult]

    @property
    def passed_targets(self) -> bool:
        return all(result.passed for result in self.target_results)


def default_font_paths() -> list[Path]:
    return sorted(DEFAULT_FONT_DIR.glob("*.ttf"))


def _name(font: TTFont, name_id: int) -> str | None:
    value = font["name"].getDebugName(name_id)
    return str(value) if value else None


def _count_codes(codes: Iterable[int], ranges: tuple[tuple[int, int], ...]) -> int:
    return sum(
        1 for code in codes if any(start <= code <= end for start, end in ranges)
    )


def inspect_font(font_path: Path) -> FontStats:
    font = TTFont(str(font_path))
    cmap = font.getBestCmap()
    codes = tuple(cmap.keys())
    range_counts = {
        range_name: _count_codes(codes, codepoint_ranges)
        for range_name, codepoint_ranges in STAT_RANGES.items()
    }
    requirements = TARGET_REQUIREMENTS.get(font_path.name, {})
    target_results = [
        TargetResult(
            range_name=range_name,
            actual=range_counts.get(range_name, 0),
            minimum=minimum,
            passed=range_counts.get(range_name, 0) >= minimum,
        )
        for range_name, minimum in requirements.items()
    ]
    if font_path.name == "erda-ccby-cjk.ttf":
        sample_codes = {ord(char) for char in target_cjk_long_sample_chars()}
        if sample_codes:
            actual_sample_codes = len(sample_codes.intersection(codes))
            target_results.append(
                TargetResult(
                    range_name="cjk_long_sample_blocks",
                    actual=actual_sample_codes,
                    minimum=len(sample_codes),
                    passed=actual_sample_codes == len(sample_codes),
                )
            )
        section_codes = {ord(char) for char in target_cjk_long_section_chars()}
        if section_codes:
            actual_section_codes = len(section_codes.intersection(codes))
            target_results.append(
                TargetResult(
                    range_name="cjk_long_text_section",
                    actual=actual_section_codes,
                    minimum=len(section_codes),
                    passed=actual_section_codes == len(section_codes),
                )
            )

    return FontStats(
        path=str(font_path),
        family_name=_name(font, 1),
        full_name=_name(font, 4),
        version=_name(font, 5),
        maxp_num_glyphs=int(font["maxp"].numGlyphs),
        glyph_order_count=len(font.getGlyphOrder()),
        cmap_codepoints=len(cmap),
        range_counts=range_counts,
        target_results=target_results,
    )


def stats_to_dict(stats: FontStats) -> dict[str, object]:
    payload = asdict(stats)
    payload["passed_targets"] = stats.passed_targets
    return payload


def format_stats(stats_items: Iterable[FontStats]) -> str:
    lines: list[str] = []
    for stats in stats_items:
        lines.append(Path(stats.path).name)
        lines.append(f"  family: {stats.family_name or '<unknown>'}")
        lines.append(f"  version: {stats.version or '<unknown>'}")
        lines.append(f"  maxp.numGlyphs: {stats.maxp_num_glyphs}")
        lines.append(f"  glyphOrder: {stats.glyph_order_count}")
        lines.append(f"  cmap codepoints: {stats.cmap_codepoints}")
        lines.append("  range counts:")
        for range_name, count in stats.range_counts.items():
            if count:
                lines.append(f"    {range_name}: {count}")
        if stats.target_results:
            lines.append("  release targets:")
            for result in stats.target_results:
                status = "PASS" if result.passed else "FAIL"
                lines.append(
                    f"    {status} {result.range_name}: {result.actual}/{result.minimum}"
                )
        lines.append("")
    return "\n".join(lines).rstrip()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--font",
        action="append",
        type=Path,
        help="TTF path to inspect; repeatable. Defaults to ../true-type/*.ttf",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    parser.add_argument(
        "--fail-on-targets",
        action="store_true",
        help="Return exit code 1 if a known ERDA font misses release targets",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    font_paths = args.font or default_font_paths()
    stats_items = [inspect_font(path) for path in font_paths]

    if args.json:
        print(json.dumps([stats_to_dict(stats) for stats in stats_items], indent=2))
    else:
        print(format_stats(stats_items))

    if args.fail_on_targets and not all(stats.passed_targets for stats in stats_items):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
