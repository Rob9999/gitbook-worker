#!/usr/bin/env python3
"""Print publish.yml entries as JSON.

Uses helper functions from `set_publish_flag.py` and `publisher.py`
so that the publish manifest is located and parsed consistently
with the rest of the tooling.

Examples:
  python gitbook_worker/tools/publishing/dump_publish.py
  python gitbook_worker/tools/publishing/dump_publish.py --all
  python gitbook_worker/tools/publishing/dump_publish.py --manifest publish.yml
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from gitbook_worker.tools.utils.smart_manage_publish_flags import load_publish_manifest
from publisher import get_publish_list
from gitbook_worker.tools.utils.language_context import (
    build_language_env,
    resolve_language_context,
)
from gitbook_worker.tools.utils.smart_manifest import detect_repo_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Dump publish.yml entries as JSON")
    parser.add_argument("--root", type=Path, help="Repository root (Default: cwd)")
    parser.add_argument(
        "--content-config",
        type=Path,
        help="Pfad zu content.yaml (Default: Repository-Root)",
    )
    parser.add_argument(
        "--lang",
        "--language",
        dest="language",
        help="Sprach-ID aus content.yaml",
    )
    parser.add_argument(
        "--manifest",
        help="Path to publish.yml/yaml (defaults to repository root)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Include entries with build=false (default: only build=true)",
    )
    args = parser.parse_args()

    raw_root = args.root.resolve() if args.root else Path.cwd()
    repo_root = detect_repo_root(raw_root)
    language_ctx = resolve_language_context(
        repo_root=repo_root,
        language=args.language,
        manifest=args.manifest,
        content_config=args.content_config,
        allow_missing_config=True,
        allow_remote_entries=True,
        require_manifest=True,
        fetch_remote=True,
    )
    os.environ.update(build_language_env(language_ctx))
    manifest_path = language_ctx.require_manifest()

    if args.all:
        data = load_publish_manifest(manifest_path)
        entries = data.get("publish", [])
    else:
        entries = get_publish_list(str(manifest_path))

    json.dump(entries, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
