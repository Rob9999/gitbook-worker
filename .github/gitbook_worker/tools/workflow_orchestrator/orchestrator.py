"""High-level orchestrator that mirrors the GitHub workflow chain.

The module glues together the existing helper scripts so the full publishing
pipeline can run either locally or inside GitHub Actions.  Profiles configured
in ``publish.yml`` decide which steps are executed and whether a pre-built
Docker image from GHCR should be used.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Iterable, Mapping, MutableMapping, Sequence

import yaml

from tools.logging_config import get_logger
from tools.publishing.frontmatter_config import FrontMatterConfigLoader
from tools.publishing.readme_config import ReadmeConfigLoader
from tools.utils import git as git_utils
from tools.utils.smart_manifest import (
    SmartManifestError,
    detect_repo_root,
    resolve_manifest,
)
from tools.utils.smart_manage_publish_flags import set_publish_flags

LOGGER = get_logger(__name__)

_DEFAULT_STEPS = (
    "check_if_to_publish",
    "ensure_readme",
    "update_citation",
    "converter",
    "engineering-document-formatter",
    "publisher",
)

_SKIP_DIRS = {
    ".git",
    ".github",
    ".venv",
    "__pycache__",
    "node_modules",
    "simulations",
}

README_FILENAMES = ("README.md", "readme.md", "Readme.md")


@dataclass(frozen=True)
class DockerSettings:
    """Docker related configuration for a profile."""

    use_registry: bool
    image: str | None
    cache: bool


@dataclass(frozen=True)
class OrchestratorProfile:
    """Resolved profile information loaded from ``publish.yml``."""

    name: str
    steps: tuple[str, ...]
    docker: DockerSettings
    description: str | None = None
    env: Mapping[str, str] | None = None


@dataclass(frozen=True)
class OrchestratorConfig:
    """Immutable runtime options for the orchestrator."""

    root: Path
    manifest: Path
    profile: OrchestratorProfile
    repo_visibility: str
    repository: str | None
    commit: str | None
    base: str | None
    reset_others: bool
    publisher_args: tuple[str, ...]
    dry_run: bool
    steps_override: tuple[str, ...] | None = None


class RuntimeContext:
    """Mutable helper carrying derived runtime values."""

    def __init__(
        self, config: OrchestratorConfig, manifest_data: dict | None = None
    ) -> None:
        self.config = config
        self.root = config.root
        self.python = sys.executable or "python"
        self._manifest_data = manifest_data or {}
        self._frontmatter_loader: FrontMatterConfigLoader | None = None
        self._readme_loader: ReadmeConfigLoader | None = None
        github_dir = self.root / ".github"
        worker_dir = github_dir / "gitbook_worker"
        worker_tools_dir = worker_dir / "tools"
        legacy_tools_dir = github_dir / "tools"
        if worker_tools_dir.exists():
            self.tools_dir = worker_tools_dir
        elif legacy_tools_dir.exists():
            self.tools_dir = legacy_tools_dir
        else:
            # Fallback to the new layout so relative paths remain stable even
            # when the directory is initialised later during the run.
            self.tools_dir = worker_tools_dir
        python_paths = [str(self.root), str(github_dir)]
        if worker_dir.exists():
            python_paths.append(str(worker_dir))
        if legacy_tools_dir.exists():
            python_paths.append(str(legacy_tools_dir))
        if worker_tools_dir.exists():
            python_paths.append(str(worker_tools_dir))
        # Ensure the selected tools directory is always part of PYTHONPATH,
        # even if it does not yet exist on disk (for example in a clean clone
        # that only vendors the new package).
        python_paths.append(str(self.tools_dir))
        unique_python_paths = list(dict.fromkeys(python_paths))
        self.python_path = os.pathsep.join(unique_python_paths)

    # --- Git helpers -------------------------------------------------

    def clone_or_update_repo(
        self,
        repo_url: str,
        destination: Path,
        *,
        branch_name: str | None = None,
        force: bool = False,
    ) -> None:
        """Clone or update *repo_url* into *destination* using shared helpers."""
        git_utils.clone_or_update_repo(
            repo_url,
            destination,
            branch_name=branch_name,
            force=force,
        )

    def checkout_branch(self, repo_dir: Path, branch_name: str) -> None:
        """Checkout *branch_name* in *repo_dir* with fast-forward semantics."""
        git_utils.checkout_branch(repo_dir, branch_name)

    def remove_tree(self, path: Path) -> None:
        """Remove *path* recursively using the shared helper."""
        git_utils.remove_tree(path)

    def env(self, extra: Mapping[str, str] | None = None) -> MutableMapping[str, str]:
        env: MutableMapping[str, str] = os.environ.copy()
        env["PYTHONPATH"] = self.python_path
        if self.config.repository:
            env.setdefault("GITHUB_REPOSITORY", self.config.repository)
        env.setdefault("ORCHESTRATOR_PROFILE", self.config.profile.name)
        env.setdefault("ORCHESTRATOR_REPO_VISIBILITY", self.config.repo_visibility)
        if self.config.profile.env:
            env.update(self.config.profile.env)
        if extra:
            env.update(extra)
        return env

    def run_command(
        self,
        cmd: Sequence[str],
        *,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        display = " ".join(shlex.quote(part) for part in cmd)
        LOGGER.info("→ %s", display)
        if self.config.dry_run:
            LOGGER.info("Dry-run aktiv – Befehl wird übersprungen.")
            return subprocess.CompletedProcess(cmd, 0)
        result = subprocess.run(
            list(cmd),
            cwd=str(cwd or self.root),
            env=self.env(env),
            check=check,
            text=True,
        )
        return result

    def git_last_commit_date(self, path: Path) -> str:
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%cs", str(path.relative_to(self.root))],
                cwd=str(self.root),
                capture_output=True,
                text=True,
                check=False,
            )
            value = (result.stdout or "").strip()
            return value or "1970-01-01"
        except Exception:
            return "1970-01-01"

    def get_frontmatter_loader(self) -> FrontMatterConfigLoader:
        """Lazy-load and cache the front matter configuration loader."""
        if self._frontmatter_loader is None:
            try:
                self._frontmatter_loader = FrontMatterConfigLoader()
            except FileNotFoundError:
                LOGGER.warning(
                    "Front matter configuration not found, using default (disabled)"
                )
                # Create a minimal default config
                from tools.publishing.frontmatter_config import (
                    FrontMatterConfig,
                    FrontMatterPatterns,
                )

                self._frontmatter_loader = type(
                    "DefaultFrontMatterConfigLoader",
                    (),
                    {
                        "config": FrontMatterConfig(
                            enabled=False,
                            patterns=FrontMatterPatterns(include=[], exclude=[]),
                            template={},
                        ),
                        "matches_patterns": lambda *args, **kwargs: False,
                        "merge_with_override": lambda override: self._frontmatter_loader.config,
                    },
                )()
        return self._frontmatter_loader

    def get_frontmatter_override(self) -> dict | None:
        """Extract frontmatter override from publish.yml manifest."""
        return self._manifest_data.get("frontmatter")

    def get_readme_loader(self) -> ReadmeConfigLoader:
        """Lazy-load and cache the README configuration loader."""
        if self._readme_loader is None:
            try:
                self._readme_loader = ReadmeConfigLoader(repo_root=self.root)
            except FileNotFoundError:
                LOGGER.warning(
                    "README configuration not found, using default (enabled)"
                )
                # Create a minimal default loader
                from tools.publishing.readme_config import (
                    ReadmeConfig,
                    ReadmePatterns,
                    ReadmeTemplate,
                    ReadmeLogging,
                )

                # Use a simple fallback configuration
                self._readme_loader = type(
                    "DefaultReadmeConfigLoader",
                    (),
                    {
                        "config": ReadmeConfig(
                            enabled=True,
                            patterns=ReadmePatterns(include=(), exclude=()),
                            template=ReadmeTemplate(
                                use_directory_name=True,
                                header_level=1,
                                footer="",
                            ),
                            readme_variants=("README.md", "readme.md", "Readme.md"),
                            logging=ReadmeLogging(
                                level="info",
                                log_skipped=False,
                                log_created=True,
                            ),
                        ),
                        "repo_root": self.root,
                        "matches_patterns": lambda *args, **kwargs: True,
                        "has_readme": lambda directory: False,
                        "generate_readme_content": lambda directory: f"# {directory.name}\n",
                        "merge_with_override": lambda override: self._readme_loader.config,
                    },
                )()
        return self._readme_loader

    def get_readme_override(self) -> dict | None:
        """Extract readme override from publish.yml manifest."""
        return self._manifest_data.get("readme")


def _as_bool(value: object, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        text = value.strip().lower()
        return text in {"1", "true", "yes", "on", "y"}
    return default


def _expand_template(value: object, variables: Mapping[str, str]) -> object:
    if isinstance(value, str):
        return Template(value).safe_substitute(variables)
    if isinstance(value, list):
        return type(value)(_expand_template(v, variables) for v in value)
    if isinstance(value, dict):
        return {k: _expand_template(v, variables) for k, v in value.items()}
    return value


def _load_manifest(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data


def _resolve_profile(
    manifest: dict,
    profile_name: str,
    variables: Mapping[str, str],
) -> OrchestratorProfile:
    profiles = manifest.get("profiles") or {}
    if not profiles:
        docker = DockerSettings(use_registry=False, image=None, cache=False)
        return OrchestratorProfile(
            name="default",
            steps=_DEFAULT_STEPS,
            docker=docker,
            description=None,
            env=None,
        )

    raw = profiles.get(profile_name)
    if raw is None:
        if profile_name != "default" and "default" not in profiles:
            available = ", ".join(sorted(profiles)) or "<none>"
            raise KeyError(
                f"Profil '{profile_name}' nicht gefunden. Verfügbare Profile: {available}"
            )
        LOGGER.warning(
            "Profil '%s' nicht gefunden – fallback auf 'default'", profile_name
        )
        raw = profiles.get("default")
        profile_name = "default"

    raw = _expand_template(raw or {}, variables)
    steps_raw = raw.get("steps")
    if not steps_raw:
        steps = _DEFAULT_STEPS
    else:
        steps = tuple(str(step).strip() for step in steps_raw if str(step).strip())

    docker_raw = raw.get("docker") or {}
    docker = DockerSettings(
        use_registry=_as_bool(docker_raw.get("use_registry")),
        image=str(docker_raw.get("image")) if docker_raw.get("image") else None,
        cache=_as_bool(docker_raw.get("cache")),
    )

    env = raw.get("env")
    if env and not isinstance(env, Mapping):
        raise TypeError("Profile 'env' erwartet ein Mapping")

    description = raw.get("description")
    if description is not None:
        description = str(description)

    return OrchestratorProfile(
        name=profile_name,
        steps=steps,
        docker=docker,
        description=description,
        env=env,
    )


def _detect_repo_visibility(explicit: str) -> str:
    if explicit != "auto":
        return explicit

    override = os.getenv("ORCHESTRATOR_REPO_VISIBILITY")
    if override:
        return override

    event_path = os.getenv("GITHUB_EVENT_PATH")
    if event_path and Path(event_path).is_file():
        try:
            payload = json.loads(Path(event_path).read_text(encoding="utf-8"))
            repo_info = payload.get("repository") or {}
            if repo_info.get("private"):
                return "private"
            return "public"
        except Exception:
            LOGGER.debug("Konnte GITHUB_EVENT_PATH nicht auswerten", exc_info=True)

    return "public"


def _resolve_paths(root: Path, manifest: Path | None) -> tuple[Path, Path]:
    repo_root = detect_repo_root(root.resolve())
    try:
        manifest_path = resolve_manifest(
            explicit=manifest,
            cwd=Path.cwd(),
            repo_root=repo_root,
        )
    except SmartManifestError as exc:
        raise FileNotFoundError(str(exc)) from exc
    return repo_root, manifest_path


def _split_publisher_args(values: Iterable[str] | None) -> tuple[str, ...]:
    if not values:
        return ()
    result: list[str] = []
    for value in values:
        if not value:
            continue
        for part in shlex.split(value):
            result.append(part)
    return tuple(result)


def build_config(args: argparse.Namespace) -> OrchestratorConfig:
    root, manifest = _resolve_paths(args.root, args.manifest)
    repository = args.repository or os.getenv("GITHUB_REPOSITORY")
    repository_template = repository.lower() if repository else ""
    variables = {
        "repo": repository_template,
        "profile": args.profile,
        "visibility": args.repo_visibility,
    }
    manifest_data = _load_manifest(manifest)
    profile = _resolve_profile(manifest_data, args.profile, variables)
    repo_visibility = _detect_repo_visibility(args.repo_visibility)
    publisher_args = _split_publisher_args(args.publisher_arg)
    steps_override = tuple(args.step) if args.step else None
    return OrchestratorConfig(
        root=root,
        manifest=manifest,
        profile=profile,
        repo_visibility=repo_visibility,
        repository=repository,
        commit=args.commit,
        base=args.base,
        reset_others=args.reset_others,
        publisher_args=publisher_args,
        dry_run=args.dry_run,
        steps_override=steps_override,
    )


def run(config: OrchestratorConfig) -> None:
    # Load manifest data for access to frontmatter and other settings
    manifest_data = _load_manifest(config.manifest)
    ctx = RuntimeContext(config, manifest_data)
    steps = config.steps_override or config.profile.steps
    LOGGER.info(
        "Starte Orchestrator-Profil '%s' mit Schritten: %s",
        config.profile.name,
        ", ".join(steps) or "<none>",
    )
    for step in steps:
        handler = STEP_HANDLERS.get(step)
        if handler is None:
            raise KeyError(f"Unbekannter Schritt: {step}")
        LOGGER.info("Schritt '%s' starten", step)
        handler(ctx)
    LOGGER.info("Orchestrator abgeschlossen")


def _step_check_if_to_publish(ctx: RuntimeContext) -> None:
    """Check which targets need to be published based on changed files.

    Uses smart_manage_publish_flags directly instead of deprecated wrapper.
    """
    LOGGER.info("Checking publish flags using smart_manage_publish_flags...")

    try:
        result = set_publish_flags(
            manifest_path=ctx.config.manifest,
            commit=ctx.config.commit or "HEAD",
            base=ctx.config.base,
            reset_others=ctx.config.reset_others,
            dry_run=False,
            debug=False,
        )

        if result["any_build_true"]:
            modified_count = len(result["modified_entries"])
            LOGGER.info("Found %d modified target(s) to publish", modified_count)
            for entry in result["modified_entries"]:
                LOGGER.info(
                    "  - %s: %s -> %s", entry["path"], entry["from"], entry["to"]
                )
        else:
            LOGGER.warning("No targets to publish - exiting")
            sys.exit(2)  # Exit code 2 = nothing to publish

    except Exception as exc:
        LOGGER.error("Failed to check publish flags: %s", exc, exc_info=True)
        raise


def _step_ensure_readme(ctx: RuntimeContext) -> None:
    """Ensure all directories have a README file.

    Uses smart configuration from readme.yml (with overrides from publish.yml).
    - Only creates README.md in directories without ANY readme variant
    - Case-insensitive check for existing READMEs
    - Respects include/exclude patterns from configuration
    - Never overwrites existing files

    Configuration hierarchy:
        1. publish.yml (readme: section) - highest priority
        2. readme.yml (project root)
        3. .github/gitbook_worker/defaults/readme.yml - default
    """
    # Load README configuration
    readme_loader = ctx.get_readme_loader()

    # Merge with overrides from publish.yml
    override = ctx.get_readme_override()
    config = readme_loader.merge_with_override(override)

    # Check if README generation is enabled
    if not config.enabled:
        LOGGER.info("README auto-generation is disabled in configuration")
        return

    created: list[Path] = []
    skipped_existing: int = 0
    skipped_pattern: int = 0

    # Walk through all directories in repository
    # Use iterdir + recursion to avoid expensive is_dir() checks on large repos
    def walk_dirs(base: Path) -> list[Path]:
        """Recursively collect directories, skipping hidden ones early."""
        dirs = []
        try:
            for item in base.iterdir():
                # Skip hidden items (starting with .) except root
                if item.name.startswith(".") and item != ctx.root:
                    continue
                if item.is_dir():
                    dirs.append(item)
                    # Recurse into subdirectory
                    dirs.extend(walk_dirs(item))
        except (OSError, PermissionError):
            # Skip directories we can't read
            pass
        return dirs

    for directory in walk_dirs(ctx.root):
        # Skip root directory itself
        if directory == ctx.root:
            continue

        rel = directory.relative_to(ctx.root)

        # Check pattern matching (smart exclude/include)
        if not readme_loader.matches_patterns(directory, ctx.root):
            skipped_pattern += 1
            if config.logging.log_skipped:
                LOGGER.debug("Skipped (pattern): %s", rel)
            continue

        # Check if directory already has a README (case-insensitive)
        if readme_loader.has_readme(directory):
            skipped_existing += 1
            if config.logging.log_skipped:
                LOGGER.debug("Skipped (has README): %s", rel)
            continue

        # Generate README content from template
        content = readme_loader.generate_readme_content(directory)
        target = directory / "README.md"

        # Final safety check: Don't overwrite if file somehow exists
        if target.exists():
            LOGGER.warning("SAFETY: Skipping %s - target exists unexpectedly", target)
            skipped_existing += 1
            continue

        created.append(target)

        # Dry-run mode: just log what would be done
        if ctx.config.dry_run:
            if config.logging.log_created:
                LOGGER.info("Would create: %s", rel / "README.md")
            continue

        # Create the README file
        try:
            target.write_text(content, encoding="utf-8")
            if config.logging.log_created:
                LOGGER.info("Created: %s", rel / "README.md")
        except OSError as exc:
            LOGGER.error("Failed to create %s: %s", target, exc)

    # Summary
    if created:
        LOGGER.info(
            "README generation: %d created, %d skipped (existing), %d skipped (pattern)",
            len(created),
            skipped_existing,
            skipped_pattern,
        )
    else:
        LOGGER.info(
            "README generation: No new READMEs needed (%d existing, %d excluded)",
            skipped_existing,
            skipped_pattern,
        )


def _step_update_citation(ctx: RuntimeContext) -> None:
    """Update citation.cff in publish/ directory and copy to root (for Zenodo/GitHub)."""
    citation_publish = ctx.root / "publish" / "CITATION.cff"
    if not citation_publish.exists():
        LOGGER.info("Keine CITATION.cff gefunden – Schritt wird übersprungen")
        return
    today = _dt.datetime.now(tz=_dt.timezone.utc).date().isoformat()
    version_line = f"version: The_zenodo_release_on_{today}"
    date_line = f"date-released: '{today}'"
    text = citation_publish.read_text(encoding="utf-8").splitlines()
    changed = False
    for idx, line in enumerate(text):
        if line.startswith("version:") and line != version_line:
            text[idx] = version_line
            changed = True
        elif line.startswith("date-released:") and line != date_line:
            text[idx] = date_line
            changed = True
    if not changed:
        LOGGER.info("citation.cff ist bereits aktuell")
    else:
        LOGGER.info("Aktualisiere citation.cff auf %s", today)
    if ctx.config.dry_run:
        return

    # Write updated content to publish/CITATION.cff
    if changed:
        citation_publish.write_text("\n".join(text) + "\n", encoding="utf-8")

    # Copy to root for GitHub/Zenodo integration
    citation_root = ctx.root / "CITATION.cff"
    import shutil

    shutil.copy2(citation_publish, citation_root)
    LOGGER.info("CITATION.cff nach Repository-Root kopiert")


def _step_ai_reference_check(ctx: RuntimeContext) -> None:
    script = ctx.tools_dir / "quality" / "ai_references.py"
    if not script.exists():
        LOGGER.warning("ai_references.py nicht gefunden – Schritt wird übersprungen")
        return
    report = ctx.root / ".github" / "reports" / "ai_reference_report.json"
    cmd = [
        ctx.python,
        str(script),
        "--root",
        str(ctx.root),
        "--manifest",
        str(ctx.config.manifest),
        "--json-report",
        str(report),
        "--no-progress",
    ]
    ctx.run_command(cmd)


def _step_converter(ctx: RuntimeContext) -> None:
    dump_script = ctx.tools_dir / "publishing" / "dump_publish.py"
    convert_script = ctx.tools_dir / "converter" / "convert_assets.py"
    if not dump_script.exists() or not convert_script.exists():
        LOGGER.warning("Konverter-Skripte nicht gefunden – Schritt wird übersprungen")
        return
    ctx.run_command(
        [
            ctx.python,
            str(dump_script),
            "--manifest",
            str(ctx.config.manifest),
        ]
    )
    # Run the converter as a module (so relative imports inside it work).
    # Pass the manifest path so the converter computes paths from the manifest
    # parent directory rather than using hardcoded paths.
    ctx.run_command(
        [
            ctx.python,
            "-m",
            "tools.converter.convert_assets",
            "--manifest",
            str(ctx.config.manifest),
        ]
    )


def _format_yaml_value(value: object) -> str:
    """Format a Python value as a YAML-compatible string.

    Args:
        value: Python value (str, int, bool, list, dict, None)

    Returns:
        YAML-compatible string representation
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        if not value:
            return "[]"
        # Simple list formatting
        return "[" + ", ".join(_format_yaml_value(v) for v in value) + "]"
    if isinstance(value, dict):
        if not value:
            return "{}"
        # Simple dict formatting (not used in our templates typically)
        return str(value)
    # Default: string value
    if not isinstance(value, str):
        value = str(value)
    # Quote strings that contain special characters or are empty
    if not value or any(
        c in value
        for c in [
            ":",
            "#",
            "[",
            "]",
            "{",
            "}",
            ",",
            "&",
            "*",
            "!",
            "|",
            ">",
            "'",
            '"',
            "%",
            "@",
            "`",
        ]
    ):
        return f'"{value}"'
    return value


def _ensure_yaml_header(path: Path, template: dict, ctx: RuntimeContext) -> bool:
    """Ensure a markdown file has YAML front matter according to the template.

    Args:
        path: Path to the markdown file
        template: Front matter template dictionary
        ctx: Runtime context

    Returns:
        True if file was modified, False otherwise
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    changed = False
    if not lines:
        lines = []

    # Replace {{date}} placeholder with actual git commit date
    resolved_template = {}
    for key, value in template.items():
        if isinstance(value, str) and value == "{{date}}":
            resolved_template[key] = ctx.git_last_commit_date(path)
        else:
            resolved_template[key] = value

    if not lines or lines[0].strip() != "---":
        # No front matter exists, create it
        header = ["---"]
        for key, value in resolved_template.items():
            header.append(f"{key}: {_format_yaml_value(value)}")
        header.extend(["---", ""])
        lines = header + lines
        changed = True
    else:
        # Front matter exists, check for missing fields
        end_idx = None
        for idx, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                end_idx = idx
                break
        if end_idx is None:
            # No closing ---, add it
            lines.append("---")
            lines.append("")
            end_idx = len(lines) - 2
            changed = True

        header_lines = lines[1:end_idx]
        existing = {
            entry.split(":", 1)[0].strip() for entry in header_lines if ":" in entry
        }
        missing = [key for key in resolved_template.keys() if key not in existing]
        if missing:
            insert = [
                f"{key}: {_format_yaml_value(resolved_template[key])}"
                for key in missing
            ]
            lines = (
                [lines[0]]
                + header_lines
                + insert
                + [lines[end_idx]]
                + lines[end_idx + 1 :]
            )
            changed = True

    if changed and not ctx.config.dry_run:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed


def _step_engineering_docs(ctx: RuntimeContext) -> None:
    """Apply front matter to markdown files according to configuration."""
    frontmatter_loader = ctx.get_frontmatter_loader()

    # Merge with per-publication overrides from publish.yml
    override = ctx.get_frontmatter_override()
    config = frontmatter_loader.merge_with_override(override)

    if not config.enabled:
        LOGGER.info("Front matter injection disabled in configuration")
        return

    if not config.template:
        LOGGER.warning("Front matter enabled but no template defined, skipping")
        return

    changed_files: list[Path] = []
    skipped_pattern: list[Path] = []

    for path in ctx.root.rglob("*.md"):
        rel = path.relative_to(ctx.root)

        # Skip directories that should always be excluded
        if any(part in _SKIP_DIRS for part in rel.parts):
            continue

        # Use smart pattern matching from configuration
        if not frontmatter_loader.matches_patterns(path, ctx.root):
            skipped_pattern.append(path)
            continue

        if _ensure_yaml_header(path, config.template, ctx):
            changed_files.append(path)

    if changed_files:
        LOGGER.info("YAML front matter updated for %d files", len(changed_files))
    else:
        LOGGER.info("All matching files already have valid front matter")

    if skipped_pattern:
        LOGGER.debug("Skipped %d files (pattern exclusion)", len(skipped_pattern))


def _step_publisher(ctx: RuntimeContext) -> None:
    pipeline = ctx.tools_dir / "publishing" / "pipeline.py"
    if not pipeline.exists():
        LOGGER.warning("pipeline.py nicht gefunden – Schritt wird übersprungen")
        return
    cmd: list[str] = [
        ctx.python,
        str(pipeline),
        "--root",
        str(ctx.root),
        "--manifest",
        str(ctx.config.manifest),
    ]
    if ctx.config.commit:
        cmd.extend(["--commit", ctx.config.commit])
    if ctx.config.base:
        cmd.extend(["--base", ctx.config.base])
    if ctx.config.reset_others:
        cmd.append("--reset-others")
    for arg in ctx.config.publisher_args:
        cmd.extend(["--publisher-args", arg])
    ctx.run_command(cmd)


STEP_HANDLERS = {
    "check_if_to_publish": _step_check_if_to_publish,
    "ensure_readme": _step_ensure_readme,
    "update_citation": _step_update_citation,
    "ai-reference-check": _step_ai_reference_check,
    "converter": _step_converter,
    "engineering-document-formatter": _step_engineering_docs,
    "publisher": _step_publisher,
}


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the ERDA workflow orchestrator",
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Pfad zu publish.yml (Standard: --root/publish.yml)",
    )
    parser.add_argument(
        "--profile",
        default="default",
        help="Profilname aus publish.yml",
    )
    parser.add_argument(
        "--repo-visibility",
        choices=("auto", "public", "private"),
        default="auto",
        help="Sichtbarkeit des Repositories",
    )
    parser.add_argument(
        "--repository",
        help="Repository-Slug (owner/name) für Template-Substitution",
    )
    parser.add_argument("--commit", help="Commit-SHA für Änderungsdetektion")
    parser.add_argument("--base", help="Basis-SHA für Änderungsdetektion")
    parser.add_argument(
        "--reset-others",
        action="store_true",
        help="Beim Setzen der Publish-Flags andere Einträge zurücksetzen",
    )
    parser.add_argument(
        "--publisher-arg",
        action="append",
        dest="publisher_arg",
        help="Zusätzliche Argumente für pipeline.py (mehrfach möglich)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Nur anzeigen, welche Schritte ausgeführt würden",
    )
    parser.add_argument(
        "--step",
        action="append",
        help="Überschreibt die im Profil definierten Schritte",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(argv)
    config = build_config(args)
    run(config)


__all__ = [
    "DockerSettings",
    "OrchestratorProfile",
    "OrchestratorConfig",
    "build_config",
    "parse_args",
    "run",
    "main",
]
