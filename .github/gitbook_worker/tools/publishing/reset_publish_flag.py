#!/usr/bin/env python3
"""DEPRECATED: Use tools.utils.smart_manage_publish_flags.reset_publish_flags()"""
import sys, warnings
from pathlib import Path
warnings.warn("tools.publishing.reset_publish_flag deprecated", DeprecationWarning)
from tools.utils.smart_manage_publish_flags import reset_publish_flags
import argparse
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--publish-file", default=None)
    p.add_argument("--path", default=None)
    p.add_argument("--out", default=None)
    p.add_argument("--index", type=int, default=None)
    p.add_argument("--multi", action="store_true")
    p.add_argument("--error-on-no-match", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--debug", action="store_true")
    a = p.parse_args()
    try:
        r = reset_publish_flags(manifest_path=Path(a.publish_file) if a.publish_file else None, path=a.path, out=a.out, index=a.index, multi=a.multi, error_on_no_match=a.error_on_no_match, dry_run=a.dry_run, debug=a.debug)
        return 0
    except SystemExit as e: return e.code if isinstance(e.code, int) else 1
    except Exception as exc: print(f"ERROR: {exc}",file=sys.stderr); return 1
if __name__ == "__main__": sys.exit(main())
