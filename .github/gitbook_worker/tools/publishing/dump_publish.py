#!/usr/bin/env python3
"""Print publish.yml entries as JSON.

Uses helper functions from `set_publish_flag.py` and `publisher.py`
so that the publish manifest is located and parsed consistently
with the rest of the tooling.

Examples:
  python .github/gitbook_worker/tools/publishing/dump_publish.py
  python .github/gitbook_worker/tools/publishing/dump_publish.py --all
  python .github/gitbook_worker/tools/publishing/dump_publish.py --manifest publish.yml
"""

from __future__ import annotations
import argparse
import json
import sys

from tools.utils.smart_manage_publish_flags import (
    find_publish_file,
    load_publish_manifest,
)
from publisher import get_publish_list


def main() -> None:
    parser = argparse.ArgumentParser(description="Dump publish.yml entries as JSON")
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

    manifest_path = find_publish_file(args.manifest)

    if args.all:
        data = load_publish_manifest(manifest_path)
        entries = data.get("publish", [])
    else:
        entries = get_publish_list(manifest_path)

    json.dump(entries, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
