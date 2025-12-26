"""Central exit-code registry and CLI helper.

This module serves two purposes:
- Provide a single source of truth for exit codes, their messages, and healing steps.
- Offer a `--help exit-codes` style output that other CLIs can delegate to or embed.

Keep this file in sync with gitbook_worker/docs/attentions/exit-codes.md.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from textwrap import dedent
from typing import Iterable, Iterator, Optional, Sequence


@dataclass(frozen=True)
class ExitCodeInfo:
    code: int
    component: str
    summary: str
    healing: str
    trigger: str


# Minimal curated set covering current CLIs. Extend as new codes are added.
_EXIT_CODES: tuple[ExitCodeInfo, ...] = (
    ExitCodeInfo(
        code=2,
        component="workflow_orchestrator",
        summary="Keine Ziele zu veröffentlichen",
        healing="Angepasste base/commit oder Publish-Flags setzen, damit Ziel(e) auf true stehen.",
        trigger="Publish-Flag-Check ergab keine geänderten Ziele",
    ),
    ExitCodeInfo(
        code=43,
        component="workflow_orchestrator|publisher",
        summary="Fonts fehlen oder LuaTeX-Cache nicht bereit",
        healing="'gitbook-worker-fonts sync --manifest publish.yml --search-path .github/fonts' ausführen, danach luaotfload-tool --update --force.",
        trigger="Font-Synchronisation fehlgeschlagen (Smart Font Stack)",
    ),
    ExitCodeInfo(
        code=2,
        component="publisher",
        summary="publish.yml nicht gefunden",
        healing="Mit --manifest Pfad angeben oder publish.yml ins Repo-Root legen.",
        trigger="Manifest-Auflösung via detect_repo_root/resolve_manifest fehlgeschlagen",
    ),
    ExitCodeInfo(
        code=3,
        component="publisher",
        summary="Ungültige oder nicht unterstützte Manifest-Version",
        healing="version in publish.yml auf kompatible SemVer anheben (gleiche Major wie Tool; siehe docs).",
        trigger="Manifest-Version fehlt/ungültig/nicht kompatibel",
    ),
    ExitCodeInfo(
        code=5,
        component="smart_manage_publish_flags",
        summary="Manifest konnte nicht geladen werden",
        healing="publish.yml prüfen/validieren; Syntaxfehler beheben.",
        trigger="YAML-Parsing/Schemafehler in publish.yml",
    ),
    ExitCodeInfo(
        code=6,
        component="smart_manage_publish_flags",
        summary="Kein Eintrag passt zur Auswahl",
        healing="Pfad/Pattern im Aufruf prüfen oder --multi nutzen, falls mehrere Treffer erwartet sind.",
        trigger="Auswahlkriterien matchen keine publish-Einträge",
    ),
    ExitCodeInfo(
        code=7,
        component="smart_manage_publish_flags",
        summary="Mehrere Einträge gefunden, aber --multi fehlt",
        healing="--multi ergänzen oder Auswahl einschränken.",
        trigger="Mehrfach-Treffer bei gesetztem Einzelmodus",
    ),
    ExitCodeInfo(
        code=8,
        component="smart_manage_publish_flags",
        summary="Ungültige Änderung der Publish-Flags",
        healing="Flags/Transitions prüfen; ungültige Kombinationen vermeiden.",
        trigger="Übergebene Zielwerte verletzen interne Konsistenz",
    ),
)


def iter_exit_codes() -> Iterator[ExitCodeInfo]:
    return iter(_EXIT_CODES)


def get_exit_info(code: int, component: Optional[str] = None) -> list[ExitCodeInfo]:
    matches = [info for info in _EXIT_CODES if info.code == code]
    if component:
        matches = [
            info for info in matches if component.lower() in info.component.lower()
        ]
    return matches


def _format_table(infos: Iterable[ExitCodeInfo]) -> str:
    rows = [
        ["Code", "Component", "Summary", "Healing", "Trigger"],
    ]
    for info in infos:
        rows.append(
            [
                str(info.code),
                info.component,
                info.summary,
                info.healing,
                info.trigger,
            ]
        )

    # simple fixed-width table
    col_widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    lines: list[str] = []
    for idx, row in enumerate(rows):
        line_parts = [row[i].ljust(col_widths[i]) for i in range(len(row))]
        lines.append(" | ".join(line_parts).rstrip())
        if idx == 0:
            lines.append("-+-".join("-" * w for w in col_widths))
    return "\n".join(lines)


def print_exit_codes_table(
    filter_code: int | None = None, component: str | None = None
) -> str:
    infos = list(iter_exit_codes())
    if filter_code is not None:
        infos = [info for info in infos if info.code == filter_code]
    if component:
        infos = [info for info in infos if component.lower() in info.component.lower()]
    table = _format_table(infos)
    print(table)
    return table


def add_exit_code_help(parser: argparse.ArgumentParser) -> None:
    """Attach a --help-exit-codes flag to an argparse parser."""

    parser.add_argument(
        "--help-exit-codes",
        action="store_true",
        help="Exit-Codes als Tabelle ausgeben und beenden",
    )


def handle_exit_code_help(
    args: argparse.Namespace, *, component: str | None = None
) -> None:
    """If the parsed args request exit-code help, print it and exit."""

    if getattr(args, "help_exit_codes", False):
        print_exit_codes_table(component=component)
        raise SystemExit(0)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Exit-Code Übersicht",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent(
            """
            Beispiele:
              python -m gitbook_worker.tools.exit_codes --exit-codes
              python -m gitbook_worker.tools.exit_codes --code 43
              python -m gitbook_worker.tools.exit_codes --component publisher
            """
        ),
    )
    parser.add_argument(
        "--exit-codes",
        action="store_true",
        help="Tabellarische Übersicht aller bekannten Exit-Codes ausgeben",
    )
    parser.add_argument(
        "--code",
        type=int,
        help="Nach konkretem Exit-Code filtern",
    )
    parser.add_argument(
        "--component",
        help="Nach Komponente filtern (Teilstring)",
    )
    add_exit_code_help(parser)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not args.exit_codes and args.code is None and args.component is None:
        parser.print_help()
        return 0

    print_exit_codes_table(filter_code=args.code, component=args.component)
    return 0


if __name__ == "__main__":
    sys.exit(main())
