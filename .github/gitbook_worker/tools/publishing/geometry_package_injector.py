#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List

import yaml

from tools.publishing.paper_info import get_valid_paper_measurements
from tools.logging_config import get_logger

logger = get_logger(__name__)

# zusätzliche Pakete/Settings, die wir in header-includes pflegen
HEADER_INCLUDES_LINES: List[str] = [
    r"\usepackage{calc}",
    r"\usepackage{enumitem}",
    r"\setlistdepth{20}",
    r"\usepackage{longtable}",
    r"\usepackage{ltablex}",
    r"\usepackage{booktabs}",
    r"\usepackage{array}",
    r"\keepXColumns",
    r"\setlength\LTleft{0pt}",
    r"\setlength\LTright{0pt}",
]

# ---------- Hilfen: Front-Matter parsen/serialisieren ----------
_FRONT_RE = re.compile(r"^---\s*\n", re.MULTILINE)


def _split_front_matter(text: str) -> tuple[dict, str]:
    """
    Versucht YAML-Front-Matter am Dokumentanfang zu lesen.
    Gibt (meta, body) zurück; meta ist {} wenn keins vorhanden ist.
    """
    if not text.startswith("---"):
        return {}, text
    # nach zweitem '---' suchen
    parts = text.split("\n", 2)
    # schnelles split, falls sehr kurz
    if len(parts) < 3:
        return {}, text
    # generisch: suche nächste Zeile mit alleinstehendem '---'
    lines = text.splitlines()
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        # „kaputter“ Header → ignorieren, neu schreiben
        return {}, text
    head = "\n".join(lines[1:end_idx])
    body = "\n".join(lines[end_idx + 1 :])  # noqa: E203
    try:
        meta = yaml.safe_load(head) or {}
        if not isinstance(meta, dict):
            meta = {}
    except Exception:
        meta = {}
    return meta, body


def _dump_front_matter(meta: dict) -> str:
    # sort_keys=False → Reihenfolge stabiler; allow_unicode=True für Umlaute
    y = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True)
    return f"---\n{y}---\n\n"


# ---------- Public: add_geometry_package ----------
def add_geometry_package(text: str, paper_format: str = "a4") -> str:
    """
    Erzwingt die für das Rendern benötigten Pakete/Settings und setzt die
    Papier-Geometrie über den Pandoc-YAML-Header (Top-Level `geometry:`),
    basierend auf der paper_format-Philosophie (z. B. 'a4', 'a4-landscape',
    'a3', ...).

    - Wenn bereits Front-Matter existiert: wird aktualisiert (idempotent).
    - Wenn kein/kaputter Header existiert: wird ein korrekter erzeugt.
    """
    logger.info(
        "Injecting geometry package/settings for " f"paper_format {paper_format} ..."
    )
    paper_info = get_valid_paper_measurements(paper_format)
    pw, ph = paper_info.size_mm
    left, top, right, bottom = paper_info.margins_mm

    # 1) Front-Matter holen
    meta, body = _split_front_matter(text)

    # 2) GEOMETRY top-level setzen (Pandoc-konform)
    #    -> Liste von Strings, damit Pandoc sauber Optionen füttert
    meta["geometry"] = [
        f"paperwidth={pw}mm",
        f"paperheight={ph}mm",
        f"left={left}mm",
        f"right={right}mm",
        f"top={top}mm",
        f"bottom={bottom}mm",
    ]

    # 3) header-includes pflegen (ohne \usepackage{geometry},
    # da geometry via top-level kommt)
    hi = list(meta.get("header-includes") or [])

    # flache Duplikat-Prüfung auf exakte Zeilen
    def _ensure(line: str):
        if line not in hi:
            hi.append(line)

    for line in HEADER_INCLUDES_LINES:
        _ensure(line)

    # evtl. vorhandene, widersprüchliche Geometry-Zeilen herausnehmen
    # (falls jemand früher \usepackage[...]{geometry} eingetragen hat)
    hi = [
        line
        for line in hi
        if not line.strip().startswith(r"\usepackage{geometry}")  # noqa: E501
    ]
    meta["header-includes"] = hi

    # 4) Neues Front-Matter rendern + Body anhängen
    return _dump_front_matter(meta) + body


if __name__ == "__main__":

    def main(argv: list[str] | None = None) -> int:
        parser = argparse.ArgumentParser(
            description="Inject LaTeX geometry packages and settings into a Markdown file."  # noqa: E501
        )
        parser.add_argument(
            "input", help="Input Markdown file (use '-' for stdin)."  # noqa: E501
        )
        parser.add_argument(
            "-o",
            "--output",
            help="Output file (default: overwrite input; or stdout if input is '-')",  # noqa: E501
        )
        parser.add_argument(
            "--paper-format",
            default="a4",
            choices=[
                "a4",
                "a4-landscape",
                "a3",
                "a3-landscape",
                "a2",
                "a2-landscape",
                "a1",
                "a1-landscape",
            ],
            help="Paper format to apply (default: a4).",
        )

        args = parser.parse_args(argv)

        # 1. Text einlesen
        if args.input == "-":
            text = sys.stdin.read()
        else:
            path_in = Path(args.input)
            if not path_in.is_file():
                sys.stderr.write(f"Error: input file {path_in} not found\n")
                return 1
            text = path_in.read_text(encoding="utf-8")

        # 2. Geometrie einfügen
        try:
            out_text = add_geometry_package(
                text, paper_format=args.paper_format
            )  # noqa: E501
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            return 1

        # 3. Ausgabe schreiben
        if args.output:
            Path(args.output).write_text(out_text, encoding="utf-8")
        elif args.input == "-":
            sys.stdout.write(out_text)
        else:
            Path(args.input).write_text(out_text, encoding="utf-8")

        return 0
