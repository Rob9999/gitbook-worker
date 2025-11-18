"""Utilities for maintaining GitBook compatible structures.

This module exposes two commands used by the ``gitbook-style`` GitHub Action:

``rename``
    Normalises file and directory names to the GitBook style by converting them
    to lower case and replacing whitespace with ``-``. Renaming happens via
    ``git mv`` when possible to preserve history, with a graceful fallback to a
    standard filesystem rename when the repository context is unavailable.

``summary``
    Regenerates ``SUMMARY.md`` based on ``book.json`` configuration. The
    resulting structure mirrors the inline Python that historically lived inside
    the workflow definition, but it is now testable and reusable.

The functions contain the actual logic so that unit tests can exercise the
behaviour without shelling out to Git. The command-line interface is a thin
wrapper around those functions.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from tools.publishing import summary_generator
from tools.logging_config import get_logger

SKIP_DIRS: set[str] = {
    ".git",
    ".github",
    "node_modules",
    "__pycache__",
    ".venv",
    "simulations",
}
MD_EXTENSIONS: set[str] = {".md"}
DEFAULT_MANUAL_MARKER = "<!-- SUMMARY: MANUAL -->"
VALID_SUMMARY_MODES = {
    "gitbook",
    "unsorted",
    "alpha",
    "title",
    "manifest",
    "manual",
}

# Map GitBook modes to summary_generator modes
SUMMARY_MODE_MAP = {
    "gitbook": summary_generator.SummaryMode.GITBOOK_STYLE.value,
    "unsorted": summary_generator.SummaryMode.ORDERED_BY_FILESYSTEM.value,
    "alpha": summary_generator.SummaryMode.ORDERED_BY_ALPHANUMERIC.value,
    "manifest": summary_generator.SummaryMode.GITBOOK_STYLE.value,
    "manual": summary_generator.SummaryMode.MANUAL.value,
}

logger = get_logger(__name__)


def _is_tracked(root: Path, rel_path: Path, *, is_dir: bool = False) -> bool:
    """Return True if *rel_path* is tracked in the Git repository rooted at ``root``."""

    try:
        if is_dir:
            cmd = ["git", "-C", str(root), "ls-files", "-z", rel_path.as_posix()]
        else:
            cmd = [
                "git",
                "-C",
                str(root),
                "ls-files",
                "--error-unmatch",
                rel_path.as_posix(),
            ]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        logger.debug(
            "git executable not available – treating %s as untracked", rel_path
        )
        return False

    if is_dir:
        return bool(result.stdout)
    return result.returncode == 0


def _normalise_name(name: str) -> str:
    """Convert ``name`` to the canonical GitBook style."""

    cleaned = re.sub(r"[^a-z0-9.-]+", "-", name.lower()).strip("-")
    return cleaned or name


def _remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink(missing_ok=True)


def safe_git_mv(src: Path, dst: Path, *, use_git: bool = True) -> None:
    """Move ``src`` to ``dst`` preserving Git history when possible.

    Handles case-insensitive filesystems (Windows) where src and dst differ only in case.
    """

    if src == dst:
        return

    # Check if this is a case-only rename (README.md -> readme.md)
    # We need to compare case-insensitively
    if str(src).lower() == str(dst).lower() and str(src) != str(dst):
        # This is a case-only rename which is problematic on Windows/in Docker
        # Skip it completely - the file already exists with the correct content
        logger.debug(
            f"Skipping case-only rename (cross-platform incompatible): {src} -> {dst}"
        )
        return

    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.exists() and src.resolve() != dst.resolve():
        if use_git:
            subprocess.run(
                ["git", "rm", "-r", "--cached", str(dst)],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        if dst.exists():
            _remove_path(dst)

    if use_git:
        result = subprocess.run(
            ["git", "mv", str(src), str(dst)],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return

        # Check if this is a "bad source" error (case-sensitivity issue)
        if "fatal: bad source" in result.stderr:
            logger.debug(
                f"Skipping case-only rename: {src} -> {dst} (case-insensitive FS)"
            )
            return

    # Only rename if source still exists and is different from destination
    if src.exists() and src.resolve() != dst.resolve():
        src.rename(dst)


def is_appendix_line(line: str) -> bool:
    """Check if a line represents an appendix entry."""
    # Match common appendix patterns in both German and English
    patterns = [
        r"^\s*\*+\s*\[(?:Anhang|[A-Z]\. |Appendix).*\]",  # For "Anhang", "A. ", "B. ", etc. and "Appendix"
        r"^\s*\*+\s*\[.+\]\(anhang-.*\.md\)",  # For files/folders starting with "anhang-"
        r"^\s*\*+\s*\[.+\]\(appendix-.*\.md\)",  # For files/folders starting with "appendix-"
    ]
    return any(re.match(pattern, line) for pattern in patterns)


def rename_to_gitbook_style(root: Path, *, use_git: bool = True) -> None:
    """Rename files and directories below ``root`` to match GitBook style."""

    logger.info(f"Renaming files in {root} to GitBook style")
    for current_root, dirs, files in os.walk(root, topdown=True):
        current_path = Path(current_root)
        rel = current_path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            dirs[:] = []
            continue

        for index, directory in enumerate(list(dirs)):
            try:
                logger.debug(f"Processing directory: '{directory}'")
                if directory in SKIP_DIRS or directory.startswith(".git"):
                    dirs.remove(directory)
                    logger.debug(f"Skipping directory: '{directory}'")
                    continue

                new_name = _normalise_name(directory)
                if new_name != directory:
                    src = current_path / directory
                    dst = current_path / new_name
                    rel_dir = (current_path / directory).relative_to(root)
                    if use_git and not _is_tracked(root, rel_dir, is_dir=True):
                        logger.debug("Skipping untracked directory '%s'", rel_dir)
                        dirs.remove(directory)
                        continue
                    safe_git_mv(src, dst, use_git=use_git)
                    logger.info(f"Renamed directory: '{src}' to '{dst}'")
                    dirs[index] = new_name
            except Exception as ex:  # pragma: no cover - best effort
                logger.warning(f"Failed to rename directory '{directory}': {ex}")
                dirs.remove(directory)

        for file_name in files:
            try:
                logger.debug(f"Processing file: '{file_name}'")
                if file_name.startswith(".") or file_name.endswith(".py"):
                    logger.debug(f"Skipping file: '{file_name}'")
                    continue
                new_name = _normalise_name(file_name)
                if new_name != file_name:
                    src = current_path / file_name
                    dst = current_path / new_name
                    rel_file = (current_path / file_name).relative_to(root)
                    if use_git and not _is_tracked(root, rel_file):
                        logger.debug("Skipping untracked file '%s'", rel_file)
                        continue
                    safe_git_mv(src, dst, use_git=use_git)
                    logger.info(f"Renamed file: '{src}' to '{dst}'")
            except Exception as ex:  # pragma: no cover - best effort
                logger.warning(f"Failed to rename file '{file_name}': {ex}")
    logger.info("Renaming complete")


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


@dataclass(frozen=True)
class SummaryContext:
    base_dir: Path
    root_dir: Path
    summary_path: Path


def _find_book_base(base_dir: Path) -> Path | None:
    """Locate the directory containing ``book.json`` starting from ``base_dir``.

    The search walks up the directory tree so tools can run inside nested
    folders while still re-using the repository level metadata.
    """

    for candidate in [base_dir, *base_dir.parents]:
        if (candidate / "book.json").exists():
            return candidate
    return None


def _build_summary_context(base_dir: Path) -> SummaryContext:
    base_dir = base_dir.resolve()
    book_base = _find_book_base(base_dir) or base_dir
    book_path = book_base / "book.json"
    book = read_json(book_path) if book_path.exists() else {}
    root_dir = (book_base / book.get("root", ".")).resolve()
    structure = book.get("structure") or {}
    summary_rel = structure.get("summary")

    if not summary_rel:
        for candidate in ("SUMMARY.md", "summary.md"):
            if (root_dir / candidate).exists():
                summary_rel = candidate
                break
        else:
            summary_rel = "SUMMARY.md"

    summary_path = (root_dir / summary_rel).resolve()
    return SummaryContext(
        base_dir=book_base, root_dir=root_dir, summary_path=summary_path
    )


def get_summary_layout(base_dir: Path) -> SummaryContext:
    """Return the resolved GitBook summary layout for ``base_dir``."""

    return _build_summary_context(base_dir)


def _resolve_manifest_path(
    manifest: Optional[Path], context: SummaryContext
) -> Optional[Path]:
    if manifest is None:
        return None
    if manifest.is_absolute():
        return manifest
    candidate = (context.root_dir / manifest).resolve()
    return candidate


def _build_summary_options(
    context: SummaryContext,
    *,
    mode: Optional[str],
    manifest: Optional[Path],
    manual_marker: Optional[str],
    appendices_last: bool = False,
) -> tuple[str, str]:
    """Build summary options and return (mode, submode)."""
    resolved_mode = (mode or "gitbook").strip().lower() or "gitbook"
    if resolved_mode not in VALID_SUMMARY_MODES:
        logger.warning(
            "Unbekannter summary_mode '%s' – fallback auf 'gitbook'", resolved_mode
        )
        resolved_mode = "gitbook"

    # Get the corresponding summary_generator mode from module-level map
    gen_mode = SUMMARY_MODE_MAP.get(
        resolved_mode, summary_generator.SummaryMode.GITBOOK_STYLE.value
    )

    # Determine submode
    gen_submode = (
        summary_generator.SubMode.APPENDIX_LAST.value
        if appendices_last
        else summary_generator.SubMode.NONE.value
    )

    return gen_mode, gen_submode


def _normalise_manifest_key(value: str) -> str:
    cleaned = value.replace("\\", "/").strip()
    cleaned = re.sub(r"/+", "/", cleaned)
    if cleaned.startswith("./"):
        cleaned = cleaned[2:]
    cleaned = cleaned.strip("/")
    return cleaned.lower()


def _parse_manifest_lines(text: str) -> List[str]:
    entries: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            stripped = stripped[2:].strip()
        hash_index = stripped.find("#")
        if hash_index != -1 and (hash_index == 0 or stripped[hash_index - 1].isspace()):
            stripped = stripped[:hash_index].strip()
        if not stripped:
            continue
        entries.append(stripped)
    return entries


def _manifest_entries_from_data(data: object) -> List[str]:
    entries: List[str] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                entries.append(item)
            elif isinstance(item, dict):
                path_value = item.get("path") or item.get("file") or item.get("src")
                if isinstance(path_value, str):
                    entries.append(path_value)
    elif isinstance(data, dict):
        for key in ("order", "summary", "chapters", "items"):
            nested = data.get(key)
            if isinstance(nested, (list, dict)):
                entries.extend(_manifest_entries_from_data(nested))
        if not entries:
            for value in data.values():
                if isinstance(value, str):
                    entries.append(value)
    return entries


def _load_manifest_order(path: Path) -> Dict[str, int]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Summary-Order-Manifest nicht gefunden: %s", path)
        return {}
    except Exception as exc:
        logger.warning(
            "Summary-Order-Manifest %s konnte nicht gelesen werden: %s", path, exc
        )
        return {}

    entries: List[str] = []
    data: object = None

    try:
        import yaml  # type: ignore

        try:
            data = yaml.safe_load(text)
        except Exception as exc:  # pragma: no cover - best effort
            logger.warning("Konnte YAML aus %s nicht parsen: %s", path, exc)
    except Exception:
        data = None

    if data is None:
        try:
            data = json.loads(text)
        except Exception:
            data = None

    if data is not None:
        entries = _manifest_entries_from_data(data)

    if not entries:
        entries = _parse_manifest_lines(text)

    manifest: Dict[str, int] = {}
    for index, raw in enumerate(entries):
        if not isinstance(raw, str):
            continue
        key = _normalise_manifest_key(raw)
        if not key:
            continue
        manifest.setdefault(key, index)
    return manifest


def ensure_clean_summary(
    base_dir: Path,
    *,
    run_git: bool = True,
    summary_mode: Optional[str] = None,
    summary_order_manifest: Optional[Path] = None,
    manual_marker: Optional[str] = DEFAULT_MANUAL_MARKER,
    summary_appendices_last: bool = False,
) -> bool:
    """Regenerate SUMMARY.md from book.json structure.
    Returns True if the file was changed.
    """
    logger.info(f"Ensuring clean SUMMARY.md in {base_dir}")
    context = get_summary_layout(base_dir)

    manifest_path = _resolve_manifest_path(summary_order_manifest, context)
    manifest_order: Optional[Dict[str, int]] = None
    if manifest_path is not None:
        manifest_order = _load_manifest_order(manifest_path)
        logger.info(
            "summary manifest resolved to %s with %d entries",
            manifest_path,
            len(manifest_order),
        )
    elif summary_mode and summary_mode.strip().lower() == "manifest":
        logger.warning(
            "summary_mode 'manifest' gewählt, aber keine Manifest-Datei angegeben"
        )

    # Get mode from module-level map
    mode = SUMMARY_MODE_MAP.get(
        summary_mode or "gitbook", summary_generator.SummaryMode.GITBOOK_STYLE.value
    )

    # Determine submode
    submode = (
        summary_generator.SubMode.APPENDIX_LAST.value
        if summary_appendices_last
        else summary_generator.SubMode.NONE.value
    )

    logger.info(
        "ensure_clean_summary: summary_appendices_last=%s, mode=%s, summary_path=%s",
        summary_appendices_last,
        mode,
        context.summary_path,
    )

    if mode == summary_generator.SummaryMode.MANUAL.value:
        if context.summary_path.exists():
            logger.info(
                "summary_mode 'manual' – bestehende SUMMARY.md wird nicht verändert"
            )
        else:
            logger.info(
                "summary_mode 'manual' – keine SUMMARY.md vorhanden, übersprungen"
            )
        return False

    context.summary_path.parent.mkdir(parents=True, exist_ok=True)

    # Read existing content and check for manual marker
    old_content = ""
    if context.summary_path.exists():
        try:
            old_content = context.summary_path.read_text(encoding="utf-8")
            if old_content:
                lines = old_content.splitlines()
                head = "\n".join(lines[:6])
                tail = "\n".join(lines[-6:])
                logger.info("SUMMARY preview (head):\n%s", head)
                logger.info("SUMMARY preview (tail):\n%s", tail)

            if manual_marker and manual_marker in old_content:
                logger.info(
                    "SUMMARY.md enthält manuellen Marker (%s) – Datei bleibt unverändert",
                    manual_marker,
                )
                return False
        except Exception:
            old_content = ""

    # Generate new summary content using the tree-based generator
    try:
        new_lines = summary_generator.generate_summary(
            root_dir=context.root_dir,
            mode=mode,
            submode=submode,
            manual_order=manifest_order,
        )
        new_content = "\n".join(new_lines).rstrip() + "\n"
    except Exception as e:
        logger.error(f"Failed to generate summary: {e}")
        return False

    if old_content == new_content:
        logger.info(f"No changes to {context.summary_path}")
        return False

    context.summary_path.write_text(new_content, encoding="utf-8")
    if run_git:
        subprocess.run(["git", "add", str(context.summary_path)], check=False)
    logger.info(f"Updated {context.summary_path}")
    return True


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GitBook style utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    rename_parser = subparsers.add_parser(
        "rename", help="Rename files to GitBook style"
    )
    rename_parser.add_argument(
        "--root", type=Path, default=Path("."), help="Directory to process"
    )
    rename_parser.add_argument(
        "--no-git", action="store_true", help="Disable git integration (for tests)"
    )

    summary_parser = subparsers.add_parser(
        "summary", help="Ensure SUMMARY.md matches book.json"
    )
    summary_parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Base directory containing book.json",
    )
    summary_parser.add_argument(
        "--no-git", action="store_true", help="Do not stage files with git"
    )
    summary_parser.add_argument(
        "--summary-mode",
        choices=sorted(VALID_SUMMARY_MODES),
        default="gitbook",
        help=(
            "Steuerung der Kapitelreihenfolge: gitbook, unsorted, alpha, title, "
            "manifest oder manual"
        ),
    )
    summary_parser.add_argument(
        "--summary-order-manifest",
        type=Path,
        help="Optionale Manifest-Datei (YAML/JSON) mit expliziter Kapitelreihenfolge",
    )
    summary_parser.add_argument(
        "--summary-manual-marker",
        default=DEFAULT_MANUAL_MARKER,
        help="Marker, der eine manuell gepflegte SUMMARY kennzeichnet (leer = aus)",
    )

    summary_parser.add_argument(
        "--summary-appendices-last",
        action="store_true",
        help="Setze Anhänge (Anhang/Appendix) ans Ende der SUMMARY-Reihenfolge",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    logger.info(f"GitBook style utility (args={argv})")
    args = parse_args(argv)

    if args.command == "rename":
        rename_to_gitbook_style(args.root.resolve(), use_git=not args.no_git)
        return 0

    if args.command == "summary":
        changed = ensure_clean_summary(
            args.root.resolve(),
            run_git=not args.no_git,
            summary_mode=args.summary_mode,
            summary_order_manifest=args.summary_order_manifest,
            manual_marker=args.summary_manual_marker,
            summary_appendices_last=getattr(args, "summary_appendices_last", False),
        )
        print("SUMMARY.MD UPDATED" if changed else "SUMMARY.MD OK")
        return 0

    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
