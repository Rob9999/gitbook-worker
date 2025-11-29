"""Convenience launcher to rebuild every ERDA CC-BY font.

Usage
-----
python build_all.py [--refresh-cache ...]

Any additional arguments are forwarded verbatim to each individual
``build_*_font.py`` script living in this directory.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _discover_scripts(root: Path) -> list[Path]:
    scripts = sorted(root.glob("build_*_font.py"))
    return [script for script in scripts if script.name != "build_all.py"]


def _run(script: Path, forwarded_args: list[str]) -> None:
    cmd = [sys.executable, str(script), *forwarded_args]
    display = " ".join(cmd)
    print(f"→ {display}")
    subprocess.run(cmd, check=True)


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent
    scripts = _discover_scripts(root)
    if not scripts:
        print("Keine build_*_font.py Skripte gefunden.")
        return 1

    # argparse with REMAINDER keeps a leading "--"; strip it for cleanliness.
    forwarded = list(argv) if argv is not None else sys.argv[1:]

    for script in scripts:
        _run(script, forwarded)

    print("Alle Fonts erfolgreich gebaut.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
