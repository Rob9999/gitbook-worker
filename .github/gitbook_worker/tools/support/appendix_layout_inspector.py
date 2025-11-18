"""Inspect the GitBook summary configuration for appendix ordering.

This module replaces the ad-hoc `_test_appendix_check.py` helper with a tested
and reusable interface.  It can be executed as a CLI or imported from tests to
assert the ordering behaviour of the GitBook summary generation code.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from tools.publishing import gitbook_style, summary_generator


@dataclass(frozen=True)
class AppendixLayoutReport:
    """Summary of the resolved GitBook layout."""

    base_dir: Path
    summary_path: Path
    mode: summary_generator.SummaryMode
    submode: summary_generator.SubMode
    top_level_titles: list[str]
    appendix_titles: list[str]



def inspect_appendix_layout(
    base_dir: Path, *, appendices_last: bool = True
) -> AppendixLayoutReport:
    """Return information about the appendix ordering for ``base_dir``."""

    context = gitbook_style.get_summary_layout(base_dir)
    mode_value, submode_value = gitbook_style._build_summary_options(  # type: ignore[attr-defined]
        context,
        mode=None,
        manifest=None,
        manual_marker=gitbook_style.DEFAULT_MANUAL_MARKER,
        appendices_last=appendices_last,
    )
    mode = summary_generator.SummaryMode(mode_value)
    submode = summary_generator.SubMode(submode_value)

    tree = summary_generator.build_summary_tree(context.root_dir, mode, submode)
    top_level_titles = [node.title for node in tree.root.children]
    appendix_titles = [node.title for node in tree.root.children if node.is_appendix]

    return AppendixLayoutReport(
        base_dir=base_dir,
        summary_path=context.summary_path,
        mode=mode,
        submode=submode,
        top_level_titles=top_level_titles,
        appendix_titles=appendix_titles,
    )



def _format_report(report: AppendixLayoutReport) -> str:
    lines = [
        f"Base directory   : {report.base_dir}",
        f"Summary path     : {report.summary_path}",
        f"Summary mode     : {report.mode.value}",
        f"Summary submode  : {report.submode.value}",
        "Top level entries:",
    ]
    lines.extend(f"  - {title}" for title in report.top_level_titles)

    if report.appendix_titles:
        lines.append("Appendix entries:")
        lines.extend(f"  - {title}" for title in report.appendix_titles)
    else:
        lines.append("Appendix entries: <none>")

    return "\n".join(lines)



def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the CLI."""

    parser = argparse.ArgumentParser(
        description="Inspect the GitBook summary configuration for appendix ordering.",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory that contains book.json or SUMMARY.md",
    )
    parser.add_argument(
        "--appendices-last",
        action="store_true",
        help="Enable appendix-last submode when inspecting the layout.",
    )
    parser.add_argument(
        "--no-appendices-last",
        dest="appendices_last",
        action="store_false",
        help="Disable appendix-last submode when inspecting the layout.",
    )
    parser.set_defaults(appendices_last=True)

    args = parser.parse_args(list(argv) if argv is not None else None)

    report = inspect_appendix_layout(args.base_dir, appendices_last=args.appendices_last)
    print(_format_report(report))
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
