from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from gitbook_worker.tools.logging_config import get_logger

from .smart_font_stack import SmartFontError, prepare_runtime_font_loader

logger = get_logger(__name__)


def _parse_args(argv: Optional[List[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GitBook Worker font utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser(
        "sync", help="Download and cache fonts referenced by fonts.yml/publish.yml"
    )
    sync_parser.add_argument(
        "--manifest",
        type=Path,
        help="Optional publish.yml path providing manifest-level font overrides",
    )
    sync_parser.add_argument(
        "--config",
        type=Path,
        help="Optional fonts.yml path (defaults to gitbook_worker/defaults/fonts.yml)",
    )
    sync_parser.add_argument(
        "--cache-dir",
        type=Path,
        help="Override the font cache directory",
    )
    sync_parser.add_argument(
        "--repo-root",
        type=Path,
        help="Explicit repository root used for resolving relative font paths",
    )
    sync_parser.add_argument(
        "--search-path",
        action="append",
        type=Path,
        default=[],
        help="Additional directories to scan for already available fonts",
    )
    sync_parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Continue even if some fonts are missing (for diagnostics)",
    )

    return parser.parse_args(argv)


def _load_manifest_fonts(manifest_path: Path) -> List[Dict[str, str]]:
    with manifest_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    fonts_section = data.get("fonts")
    if not isinstance(fonts_section, list):
        return []

    manifest_dir = manifest_path.parent
    resolved: List[Dict[str, str]] = []
    for entry in fonts_section:
        if isinstance(entry, dict):
            candidate: Dict[str, str] = {}
            name = entry.get("name")
            if isinstance(name, str) and name.strip():
                candidate["name"] = name.strip()
            raw_path = entry.get("path")
            if raw_path:
                path_obj = Path(str(raw_path))
                if not path_obj.is_absolute():
                    path_obj = (manifest_dir / path_obj).resolve()
                candidate["path"] = str(path_obj)
            raw_url = entry.get("url")
            if isinstance(raw_url, str) and raw_url.strip():
                candidate["url"] = raw_url.strip()
        else:
            path_obj = Path(str(entry))
            if not path_obj.is_absolute():
                path_obj = (manifest_dir / path_obj).resolve()
            candidate = {"path": str(path_obj)}
        if candidate:
            resolved.append(candidate)
    return resolved


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)

    if args.command != "sync":  # pragma: no cover - defensive
        logger.error("Unsupported command: %s", args.command)
        return 2

    manifest_fonts = _load_manifest_fonts(args.manifest) if args.manifest else None

    try:
        result = prepare_runtime_font_loader(
            manifest_fonts=manifest_fonts,
            extra_search_paths=args.search_path or None,
            cache_dir=args.cache_dir,
            config_path=args.config,
            repo_root=args.repo_root,
            allow_partial=args.allow_partial,
        )
    except SmartFontError as exc:
        logger.error("Font-Synchronisation fehlgeschlagen: %s", exc)
        return 1

    for resolved in result.resolved_fonts:
        logger.info(
            "✓ %s (%s) -> %s",
            resolved.name,
            resolved.source,
            ", ".join(path.as_posix() for path in resolved.paths),
        )

    logger.info("Font-Synchronisation abgeschlossen (%d Downloads)", result.downloads)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
