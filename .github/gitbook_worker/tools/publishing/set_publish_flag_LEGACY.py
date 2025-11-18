#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI wrapper for set_publish_flag functionality.

DEPRECATED: This file is a compatibility wrapper.
New code should import from tools.utils.smart_manage_publish_flags instead.

This wrapper will be removed in a future version.

Legacy usage:
  python .github/gitbook_worker/tools/publishing/set_publish_flag.py --commit <SHA> [--base <BASE_SHA>] [--reset-others] [--dry-run]

Typical GitHub Actions calls:
  # Push: compare before and after
  python .github/gitbook_worker/tools/publishing/set_publish_flag.py --commit "$GITHUB_SHA" --base "${{ github.event.before }}" --reset-others

  # PR: compare base and head
  python .github/gitbook_worker/tools/publishing/set_publish_flag.py --commit "${{ github.event.pull_request.head.sha }}" --base "${{ github.event.pull_request.base.sha }}" --reset-others
"""
import argparse
import sys
import warnings
from pathlib import Path

# Issue deprecation warning
warnings.warn(
    "tools.publishing.set_publish_flag is deprecated. "
    "Use tools.utils.smart_manage_publish_flags.set_publish_flags() instead.",
    DeprecationWarning,
    stacklevel=2,
)

from tools.utils.smart_manage_publish_flags import set_publish_flags

try:
    import yaml  # PyYAML
except ImportError:
    logger.error(
        "PyYAML nicht installiert. Bitte `pip install pyyaml` im Workflow ausführen."
    )
    sys.exit(2)


def run(cmd: List[str]) -> Tuple[int, str, str]:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err


def find_publish_file(explicit: str = None) -> Path:
    cwd = Path.cwd()
    repo_root = detect_repo_root(cwd)
    try:
        manifest_path = resolve_manifest(
            explicit=explicit, cwd=cwd, repo_root=repo_root
        )
    except SmartManifestError as exc:
        logger.error(str(exc))
        sys.exit(3)
    return manifest_path


def normalize_posix(path_str: str) -> str:
    # Git gibt immer forward slashes aus -> POSIX-Style beibehalten
    # Entferne führendes './' und normalisiere Mehrfach-Slashes.
    p = path_str.replace("\\", "/")
    p = p.lstrip("./")
    return posixpath.normpath(p)


def get_entry_type(entry: Dict[str, Any]) -> str:
    value = entry.get("source_type") or entry.get("type") or "auto"
    if isinstance(value, str):
        return value.strip().lower()
    return str(value).strip().lower()


def resolve_entry_path(entry_path: str, publish_dir: str, repo_root: str) -> str:
    full_entry_path = os.path.normpath(os.path.join(publish_dir, entry_path))
    try:
        rel_path = os.path.relpath(full_entry_path, repo_root)
    except ValueError:
        rel_path = full_entry_path
    return normalize_posix(rel_path)


def is_match(
    entry_path: str, entry_type: str, changed_file: str, content_root: str = None
) -> bool:
    """Check if changed file matches publish entry.

    Args:
        entry_path: Original entry path from publish.yml
        entry_type: Type of entry ("file", "folder", "auto")
        changed_file: Changed file path from git
        content_root: Optional content root from book.json (overrides entry_path for matching)

    Returns:
        True if file matches entry, False otherwise
    """
    # Use content_root if provided (from book.json), otherwise use entry_path
    match_path = content_root if content_root else entry_path

    ep = normalize_posix(match_path)
    cf = normalize_posix(changed_file)

    # Handle root path explicitly (. or ./)
    if ep in (".", ""):
        # Root path matches everything
        return True

    if entry_type == "folder":
        # Treffer, wenn Datei im Ordner (oder der Ordner selbst) liegt
        return cf == ep or cf.startswith(ep + "/")
    elif entry_type == "file":
        return cf == ep
    else:
        # "auto": heuristisch – Ordner wenn kein Punkt im letzten Segment und Pfad existiert/ist Dir,
        # sonst Datei. Fallback: Datei.
        last = posixpath.basename(ep)
        if os.path.isdir(ep) or (("." not in last) and not posixpath.splitext(last)[1]):
            return cf == ep or cf.startswith(ep + "/")
        return cf == ep


def git_changed_files(commit: str, base: str = None) -> List[str]:
    """Return the list of changed files between ``base`` and ``commit``.

    GitHub Actions checkouts often use ``fetch-depth=1`` which means the
    provided base revision might not exist locally. When that happens the
    initial ``git diff`` call fails with errors such as ``bad revision``.  In
    that case we fall back to analysing the single commit so that publishing
    decisions still work instead of aborting the workflow.
    """

    def _diff_tree_single(target_commit: str) -> Tuple[int, str, str]:
        return run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", target_commit]
        )

    if base:
        code, out, err = run(["git", "diff", "--name-only", base, commit])
        ctx = f"{base}..{commit}"
        if code != 0:
            lowered_error = err.lower()
            missing_base = any(
                token in lowered_error
                for token in (
                    "bad revision",
                    "unknown revision",
                    "ambiguous argument",
                    "not a valid object name",
                    "bad object",
                    "invalid upstream",
                    "invalid revision",
                    "no merge base",
                )
            )
            if missing_base:
                logger.warning(
                    "Konnte Basis-Commit %s nicht finden (fetch-depth?). Fallback auf Einzel-Commit.",
                    base,
                )
                code, out, err = _diff_tree_single(commit)
                ctx = commit
            else:
                logger.warning(
                    "Git-Diff %s schlug fehl (%s). Fallback auf Einzel-Commit.",
                    ctx,
                    err.strip() or f"Exit-Code {code}",
                )
                code, out, err = _diff_tree_single(commit)
                ctx = commit
    else:
        # Einzel-Commit
        code, out, err = _diff_tree_single(commit)
        ctx = commit

    if code != 0:
        logger.warning(
            "Git-Aufruf fehlgeschlagen (%s): %s",
            ctx,
            err.strip() or f"Exit-Code {code}",
        )

        # Versuche als Fallback alle Dateien des Ziel-Commits zu listen. Das ist
        # zwar konservativ (alles gilt als verändert), verhindert aber, dass der
        # Workflow komplett fehlschlägt, nur weil die Historie in Shallow-Clones
        # unvollständig ist.
        ls_code, ls_out, ls_err = run(
            ["git", "ls-tree", "--full-tree", "-r", "--name-only", commit]
        )
        if ls_code == 0:
            logger.warning(
                "Fallback auf ls-tree(%s). %d Dateien werden als geändert behandelt.",
                commit,
                len(ls_out.splitlines()),
            )
            return [
                normalize_posix(line) for line in ls_out.splitlines() if line.strip()
            ]

        logger.error(
            "Auch der Fallback ls-tree(%s) schlug fehl: %s", commit, ls_err.strip()
        )
        return []

    files = [normalize_posix(line) for line in out.splitlines() if line.strip()]
    return files


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
    # Hinweis: PyYAML formatiert neu; falls Format/Kommentare erhalten bleiben sollen -> ruamel.yaml verwenden.
    with open(publish_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def main():
    parser = argparse.ArgumentParser(
        description="Setzt build-Flags in publish.yaml basierend auf Git-Änderungen."
    )
    parser.add_argument(
        "--commit",
        default=os.getenv("GITHUB_SHA", "HEAD"),
        help="Ziel-Commit (default: GITHUB_SHA oder HEAD)",
    )
    parser.add_argument(
        "--base",
        help="Basis-Commit zum Vergleichen (z. B. github.event.before oder PR-Base-SHA)",
    )
    parser.add_argument("--branch", help="optionaler Branch-Name (nur Logging)")
    parser.add_argument(
        "--publish-file", help="Pfad zu publish.yaml/yml (default: Repo-Root)"
    )
    parser.add_argument(
        "--reset-others",
        action="store_true",
        help="Nicht betroffene Einträge explizit auf false setzen",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Nur anzeigen, keine Datei schreiben"
    )
    parser.add_argument("--debug", action="store_true", help="Debug-Ausgaben")
    args = parser.parse_args()

    publish_path = find_publish_file(args.publish_file)
    publish_dir = publish_path.parent
    repo_root_path = detect_repo_root(publish_dir)

    changed_files = git_changed_files(args.commit, args.base)
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Changed files (%d):", len(changed_files))
        for c in changed_files:
            logger.debug("  - %s", c)

    # Load publish targets using smart module
    try:
        targets = load_publish_targets(publish_path, only_build=False)
        logger.info(
            "Loaded %d publish target(s) using smart_publish_target", len(targets)
        )
    except Exception as exc:
        logger.error("Failed to load targets with smart module: %s", exc)
        logger.info("Falling back to legacy manifest loading")
        targets = []

    # Fallback to legacy loading if smart module failed
    data = load_publish(str(publish_path))
    entries = data["publish"]

    touched_entries = []
    for idx, entry in enumerate(entries):
        ep = entry.get("path")
        etype = get_entry_type(entry)
        if not ep:
            logger.warning("publish[%d] ohne 'path' – übersprungen.", idx)
            continue

        # Try to get content root from smart target
        content_root_path = None
        if idx < len(targets):
            target = targets[idx]
            try:
                content_root = get_target_content_root(target)
                # Convert to relative path for matching
                try:
                    content_root_path = normalize_posix(
                        os.path.relpath(content_root, repo_root_path)
                    )
                    logger.debug(
                        "Target %d: Using content_root=%s (from book.json: %s)",
                        idx,
                        content_root_path,
                        target.book_config is not None,
                    )
                except ValueError:
                    # Paths on different drives on Windows
                    content_root_path = None
            except Exception as exc:
                logger.debug("Failed to get content_root for target %d: %s", idx, exc)

        resolved_ep = resolve_entry_path(ep, str(publish_dir), str(repo_root_path))

        # Use content_root_path for matching if available (book.json aware)
        hit = any(
            is_match(resolved_ep, etype, cf, content_root=content_root_path)
            for cf in changed_files
        )

        # Baue altes/newes Flag
        old_build = bool(entry.get("build", False))
        new_build = True if hit else (False if args.reset_others else old_build)

        if old_build != new_build:
            entry["build"] = new_build
            touched_entries.append(
                {"path": ep, "type": etype, "from": old_build, "to": new_build}
            )
        else:
            # Stelle sicher, dass build-Schlüssel existiert
            entry["build"] = new_build

    # Outputs (für GitHub Actions)
    outputs = {
        "changed_files": changed_files,
        "modified_entries": touched_entries,
        "any_build_true": any(e.get("build", False) for e in entries),
    }

    # Schreiben
    if args.dry_run:
        logger.info("[DRY-RUN] Änderungen würden geschrieben werden.")
    else:
        save_publish(str(publish_path), data)

    # Menschlich lesbares Log
    logger.info("publish file: %s", publish_path)
    logger.info(
        "commit: %s%s%s",
        args.commit,
        f" | base: {args.base}" if args.base else "",
        f" | branch: {args.branch}" if args.branch else "",
    )
    if touched_entries:
        logger.info("geänderte build-Flags:")
        for t in touched_entries:
            logger.info(
                "  - %s (%s): %s -> %s", t["path"], t["type"], t["from"], t["to"]
            )
    else:
        logger.info("keine build-Flag-Änderungen.")

    # Maschine-lesbar (JSON auf stdout ans Ende hängen, damit von anderen Steps geparst werden kann)
    logger.info("::group::set_publish_flag.outputs")
    logger.info(json.dumps(outputs, ensure_ascii=False))
    logger.info("::endgroup::")

    # Zusätzlich GitHub-Outputs schreiben, falls verfügbar
    gh_out = os.getenv("GITHUB_OUTPUT")
    if gh_out:
        try:
            with open(gh_out, "a", encoding="utf-8") as f:
                f.write(
                    f"changed_files={json.dumps(changed_files, ensure_ascii=False)}\n"
                )
                f.write(
                    f"modified_entries={json.dumps(touched_entries, ensure_ascii=False)}\n"
                )
                f.write(
                    f"any_build_true={'true' if outputs['any_build_true'] else 'false'}\n"
                )
        except Exception as e:
            logger.warning("Konnte GITHUB_OUTPUT nicht schreiben: %s", e)


if __name__ == "__main__":
    main()
