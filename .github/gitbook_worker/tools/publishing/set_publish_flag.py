#!/usr/bin/env python3
"""DEPRECATED: Use tools.utils.smart_manage_publish_flags.set_publish_flags()"""
import sys, warnings
from pathlib import Path

warnings.warn("tools.publishing.set_publish_flag deprecated", DeprecationWarning)
from tools.utils.smart_manage_publish_flags import set_publish_flags
import argparse


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--publish", default=None)
    p.add_argument(
        "--publish-file", dest="publish", default=None
    )  # Accept both old and new arg names
    p.add_argument("--commit", default="HEAD")
    p.add_argument("--base", default=None)
    p.add_argument("--reset-others", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--debug", action="store_true")
    a = p.parse_args()
    try:
        r = set_publish_flags(
            manifest_path=Path(a.publish) if a.publish else None,
            commit=a.commit,
            base=a.base,
            reset_others=a.reset_others,
            dry_run=a.dry_run,
            debug=a.debug,
        )
        return 0 if r["any_build_true"] else 2
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
