"""High-level orchestrator for the ERDA book publishing toolchain.

The individual helper scripts inside ``tools.publishing`` remain executable on
their own, but GitHub Actions previously had to invoke them from separate jobs,
materialising intermediate state on disk.  ``pipeline.py`` streamlines the
process so a single workflow job can prepare metadata, refresh GitBook assets
and run the PDF publisher inside one container invocation.

Usage examples
--------------
Run the full pipeline with default settings::

    python gitbook_worker/tools/publishing/pipeline.py \
        --commit "$GITHUB_SHA" --base "${{ github.event.before }}"

Skip GitBook renaming for a debugging session::

    python gitbook_worker/tools/publishing/pipeline.py --no-gitbook-rename

Forward custom arguments to ``publisher.py`` (for example to keep the combined
Markdown file)::

    python gitbook_worker/tools/publishing/pipeline.py \
        --publisher-args "--keep-combined"

The script intentionally shells out to the helper tools instead of importing
internal functions.  This guarantees identical logging/CLI behaviour and keeps
the orchestration lightweight.
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping, Sequence

from gitbook_worker.tools.logging_config import get_logger
from gitbook_worker.tools.utils.language_context import (
    build_language_env,
    resolve_language_context,
)
from gitbook_worker.tools.utils.smart_manage_publish_flags import set_publish_flags
from gitbook_worker.tools.exit_codes import add_exit_code_help, handle_exit_code_help
from gitbook_worker.tools.utils.smart_manifest import detect_repo_root

LOGGER = get_logger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class PipelineOptions:
    """Options controlling the pipeline run."""

    root: Path
    manifest: Path
    commit: str | None
    base: str | None
    reset_others: bool
    run_set_flag: bool
    run_gitbook_rename: bool
    run_gitbook_summary: bool
    run_publisher: bool
    gitbook_use_git: bool
    publisher_args: tuple[str, ...]
    dry_run: bool
    language_id: str
    language_env: Mapping[str, str]


class CommandError(RuntimeError):
    """Raised when a subprocess exits with a non-zero status."""


def _build_env(
    language_env: Mapping[str, str], extra: Mapping[str, str] | None = None
) -> MutableMapping[str, str]:
    env: MutableMapping[str, str] = os.environ.copy()
    env.update(language_env)
    if extra:
        env.update(extra)
    return env


def _format_cmd(cmd: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


def _run_command(
    cmd: Sequence[str],
    *,
    options: PipelineOptions,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess:
    display = _format_cmd(cmd)
    LOGGER.info("→ %s", display)
    result = subprocess.run(
        list(cmd),
        cwd=str(cwd) if cwd else None,
        env=_build_env(options.language_env, env),
        text=True,
    )
    if check and result.returncode != 0:
        raise CommandError(
            f"Command failed with exit status {result.returncode}: {display}"
        )
    return result


def _resolve_options(args: argparse.Namespace) -> PipelineOptions:
    repo_root = detect_repo_root(args.root)
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
    manifest = language_ctx.require_manifest()
    language_env = build_language_env(language_ctx)
    publisher_args = tuple(args.publisher_args or ())
    return PipelineOptions(
        root=language_ctx.root,
        manifest=manifest,
        commit=args.commit,
        base=args.base,
        reset_others=args.reset_others,
        run_set_flag=not args.no_set_flag,
        run_gitbook_rename=not args.no_gitbook_rename,
        run_gitbook_summary=not args.no_gitbook_summary,
        run_publisher=not args.no_publish,
        gitbook_use_git=not args.gitbook_no_git,
        publisher_args=publisher_args,
        dry_run=args.dry_run,
        language_id=language_ctx.language_id,
        language_env=language_env,
    )


def _build_python_cmd(script: Path, *extra: str) -> tuple[str, ...]:
    return (sys.executable or "python", str(script), *extra)


def _run_set_publish_flag(options: PipelineOptions) -> None:
    """Update publish flags without spawning the deprecated helper CLI."""

    result = set_publish_flags(
        manifest_path=options.manifest,
        commit=options.commit or "HEAD",
        base=options.base,
        reset_others=options.reset_others,
        dry_run=options.dry_run,
    )
    LOGGER.info(
        "set_publish_flags touched %d entries (any_build_true=%s)",
        len(result.get("modified_entries", [])),
        result.get("any_build_true", False),
    )


def _run_gitbook_steps(options: PipelineOptions) -> None:
    script = SCRIPT_DIR / "gitbook_style.py"
    if options.run_gitbook_rename:
        rename_args = ["rename", "--root", str(options.root)]
        if not options.gitbook_use_git:
            rename_args.append("--no-git")
        _run_command(
            _build_python_cmd(script, *rename_args),
            cwd=options.root,
            options=options,
        )
    if options.run_gitbook_summary:
        summary_args = ["summary", "--root", str(options.root)]
        if not options.gitbook_use_git:
            summary_args.append("--no-git")
        summary_args.extend(["--document-manifest", str(options.manifest)])
        if options.language_id:
            summary_args.extend(["--locale", options.language_id])
        # If the manifest requests appendices to be moved to the end, forward
        # the flag to the gitbook summary command so the initial SUMMARY
        # regeneration (run by the pipeline) uses the same option the
        # publisher later receives.
        try:
            manifest_text = (options.manifest).read_text(encoding="utf-8")
        except OSError:
            manifest_text = ""
        if "summary_appendices_last" in manifest_text:
            # crude detection: check for a truthy setting in the manifest
            for line in manifest_text.splitlines():
                line_strip = line.strip()
                if line_strip.startswith("summary_appendices_last"):
                    # Accept formats like 'summary_appendices_last: true' (yaml)
                    if ":" in line_strip:
                        _, val = line_strip.split(":", 1)
                        if val.strip().lower() in ("true", "yes", "y", "1"):
                            summary_args.append("--summary-appendices-last")
                    break
        _run_command(
            _build_python_cmd(script, *summary_args),
            cwd=options.root,
            options=options,
        )


def _run_publisher(options: PipelineOptions) -> None:
    script = SCRIPT_DIR / "publisher.py"
    cmd = list(_build_python_cmd(script, "--manifest", str(options.manifest)))
    cmd.extend(options.publisher_args)
    _run_command(cmd, cwd=options.root, options=options)


def run_pipeline(options: PipelineOptions) -> None:
    LOGGER.info(
        "Starte Publishing-Pipeline (root=%s, manifest=%s)",
        options.root,
        options.manifest,
    )
    if options.dry_run:
        LOGGER.info("Dry-Run aktiviert – Befehle werden nicht ausgeführt.")
        return

    if options.run_set_flag:
        _run_set_publish_flag(options)

    _run_gitbook_steps(options)

    if options.run_publisher:
        _run_publisher(options)


def _split_publisher_args(raw: Iterable[str] | None) -> tuple[str, ...]:
    if not raw:
        return ()
    result: list[str] = []
    for value in raw:
        result.extend(shlex.split(value))
    return tuple(result)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the ERDA selective publishing pipeline",
    )
    add_exit_code_help(parser)
    parser.add_argument(
        "--root",
        type=Path,
        help="Repository root (default: automatisch über smart manifest Regeln)",
    )
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
        type=Path,
        help="Path to publish.yml/yaml (defaults to --root / publish.yml)",
    )
    parser.add_argument("--commit", help="Target commit for change detection")
    parser.add_argument(
        "--base",
        help="Base commit for change detection (e.g. github.event.before)",
    )
    parser.add_argument(
        "--reset-others",
        action="store_true",
        help="Reset non-touched manifest entries when setting flags",
    )
    parser.add_argument(
        "--no-set-flag",
        action="store_true",
        help="Skip set_publish_flag step",
    )
    parser.add_argument(
        "--no-gitbook-rename",
        action="store_true",
        help="Skip GitBook rename step",
    )
    parser.add_argument(
        "--no-gitbook-summary",
        action="store_true",
        help="Skip SUMMARY.md regeneration",
    )
    parser.add_argument(
        "--gitbook-no-git",
        action="store_true",
        help="Disable git integration for GitBook steps",
    )
    parser.add_argument(
        "--no-publish",
        action="store_true",
        help="Skip the PDF publisher",
    )
    parser.add_argument(
        "--publisher-args",
        action="append",
        help="Extra arguments forwarded to publisher.py (repeat for multiple)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the commands without executing them",
    )
    namespace = parser.parse_args(list(argv) if argv is not None else None)
    handle_exit_code_help(namespace)
    if namespace.root is None:
        namespace.root = detect_repo_root(Path.cwd())
    else:
        namespace.root = detect_repo_root(namespace.root.resolve())
    namespace.publisher_args = _split_publisher_args(namespace.publisher_args)
    return namespace


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(argv)
    options = _resolve_options(args)
    run_pipeline(options)


if __name__ == "__main__":
    main()
