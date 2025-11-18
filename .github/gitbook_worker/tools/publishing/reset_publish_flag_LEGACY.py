#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setzt das build-Flag eines spezifischen publish-Eintrags auf false.

Nutzung (mind. EIN Kriterium angeben):
  python .github/gitbook_worker/tools/publishing/reset-publish-flag.py --path documents
  python .github/gitbook_worker/tools/publishing/reset-publish-flag.py --out sphere-space.pdf
  python .github/gitbook_worker/tools/publishing/reset-publish-flag.py --index 0

Optionen:
  --multi              Setzt bei mehreren Treffern ALLE auf false (Default: Fehler bei >1 Treffer)
  --error-on-no-match  Exit != 0, wenn kein Eintrag gefunden wurde
  --publish-file       Pfad zu publish.yaml|yml (Default: Repo-Root)
  --dry-run            Keine Änderungen schreiben
  --debug              Zusätzliche Logs
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from tools.logging_config import get_logger
from tools.utils.smart_manifest import (
    SmartManifestError,
    detect_repo_root,
    resolve_manifest,
)

logger = get_logger(__name__)

try:
    import yaml  # PyYAML
except ImportError:
    logger.error(
        "PyYAML nicht installiert. Bitte `pip install pyyaml` im Workflow ausführen."
    )
    sys.exit(2)


def find_publish_file(explicit: str = None) -> Path:
    cwd = Path.cwd()
    repo_root = detect_repo_root(cwd)
    try:
        manifest_path = resolve_manifest(explicit=explicit, cwd=cwd, repo_root=repo_root)
    except SmartManifestError as exc:
        logger.error(str(exc))
        sys.exit(3)
    return manifest_path


def load_publish(publish_path: str) -> Dict[str, Any]:
    with open(publish_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if "publish" not in data or not isinstance(data["publish"], list):
        logger.error(
            "Ungültiges publish.yaml-Format: Top-Level-Schlüssel 'publish' (Liste) fehlt."
        )
        sys.exit(5)
    return data


def save_publish(publish_path: str, data: Dict[str, Any]) -> None:
    with open(publish_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def match_indices(
    entries: List[Dict[str, Any]], path: str, out: str, index: int, debug: bool
) -> List[int]:
    hits: List[int] = []
    for i, e in enumerate(entries):
        if index is not None and i == index:
            hits.append(i)
            continue
        if path is not None and str(e.get("path", "")).strip() == path:
            hits.append(i)
            continue
        if out is not None and str(e.get("out", "")).strip() == out:
            hits.append(i)
            continue
    if debug:
        logger.debug(
            "Match-Kandidaten (path=%r, out=%r, index=%s): %s", path, out, index, hits
        )
    return sorted(set(hits))


def main():
    ap = argparse.ArgumentParser(
        description="Setzt ein bestimmtes build-Flag in publish.yaml|yml auf false."
    )
    ap.add_argument("--path", help="Pfad (wie im publish-Eintrag unter 'path')")
    ap.add_argument(
        "--out", help="Output-Dateiname (wie im publish-Eintrag unter 'out')"
    )
    ap.add_argument("--index", type=int, help="0-basierter Index des publish-Eintrags")
    ap.add_argument(
        "--multi",
        action="store_true",
        help="Bei mehreren Treffern ALLE zurücksetzen (statt Fehler)",
    )
    ap.add_argument(
        "--error-on-no-match",
        action="store_true",
        help="Exit mit Fehler, wenn kein Eintrag gefunden",
    )
    ap.add_argument(
        "--publish-file", help="Pfad zu publish.yaml|yml (Default: im Repo-Root)"
    )
    ap.add_argument(
        "--dry-run", action="store_true", help="Nur anzeigen, nicht schreiben"
    )
    ap.add_argument("--debug", action="store_true", help="Debug-Ausgaben")
    args = ap.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.path is None and args.out is None and args.index is None:
        logger.error("Bitte --path, --out oder --index angeben.")
        sys.exit(1)

    publish_path = find_publish_file(args.publish_file)
    data = load_publish(str(publish_path))
    entries: List[Dict[str, Any]] = data["publish"]

    # Index-Grenzen prüfen (falls übergeben)
    if args.index is not None and (args.index < 0 or args.index >= len(entries)):
        logger.error(
            "--index %s liegt außerhalb des Bereichs [0..%d].",
            args.index,
            len(entries) - 1,
        )
        sys.exit(6)

    matches = match_indices(entries, args.path, args.out, args.index, args.debug)

    if not matches:
        msg = "Kein publish-Eintrag gefunden, der den Kriterien entspricht."
        if args.error_on_no_match:
            logger.error(msg)
            sys.exit(7)
        else:
            logger.info(msg)
            outputs = {
                "reset_count": 0,
                "matched_indices": [],
                "matched_paths": [],
                "matched_outs": [],
                "changed": [],
            }
            logger.info("::group::reset_publish_flag.outputs")
            logger.info(json.dumps(outputs, ensure_ascii=False))
            logger.info("::endgroup::")
            return

    if len(matches) > 1 and not args.multi:
        logger.error(
            "Mehrere Einträge passen %s, aber --multi wurde nicht gesetzt.", matches
        )
        sys.exit(8)

    changed: List[Dict[str, Any]] = []
    for i in matches:
        entry = entries[i]
        before = bool(entry.get("build", False))
        after = False
        if before != after:
            entry["build"] = after
            changed.append(
                {
                    "index": i,
                    "path": entry.get("path"),
                    "out": entry.get("out"),
                    "from": before,
                    "to": after,
                }
            )
        else:
            # Stelle sicher, dass der Schlüssel existiert
            entry["build"] = False

    if args.dry_run:
        logger.info("[DRY-RUN] Änderungen würden geschrieben werden.")
    else:
        save_publish(str(publish_path), data)

    logger.info("publish file: %s", publish_path)
    if changed:
        logger.info("zurückgesetzte build-Flags:")
        for c in changed:
            logger.info(
                "  - index=%s path=%s out=%s : %s -> %s",
                c["index"],
                c.get("path"),
                c.get("out"),
                c["from"],
                c["to"],
            )
    else:
        logger.info("Keine tatsächlichen Änderungen (build war bereits false).")

    outputs = {
        "reset_count": len(matches),
        "matched_indices": matches,
        "matched_paths": [entries[i].get("path") for i in matches],
        "matched_outs": [entries[i].get("out") for i in matches],
        "changed": changed,
    }

    logger.info("::group::reset_publish_flag.outputs")
    logger.info(json.dumps(outputs, ensure_ascii=False))
    logger.info("::endgroup::")

    gh_out = os.getenv("GITHUB_OUTPUT")
    if gh_out:
        try:
            with open(gh_out, "a", encoding="utf-8") as f:
                f.write(f"reset_count={outputs['reset_count']}\n")
                f.write(
                    f"matched_indices={json.dumps(outputs['matched_indices'], ensure_ascii=False)}\n"
                )
                f.write(
                    f"matched_paths={json.dumps(outputs['matched_paths'], ensure_ascii=False)}\n"
                )
                f.write(
                    f"matched_outs={json.dumps(outputs['matched_outs'], ensure_ascii=False)}\n"
                )
                f.write(
                    f"changed={json.dumps(outputs['changed'], ensure_ascii=False)}\n"
                )
        except Exception as e:
            logger.warning("Konnte GITHUB_OUTPUT nicht schreiben: %s", e)


if __name__ == "__main__":
    main()
