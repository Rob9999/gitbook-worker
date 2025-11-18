<!-- License: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) -->
# Tooling Migration Review

## Executive summary

- The legacy `tools/gitbook-worker` package has been retired; the remaining emoji analysis helper now lives in `.github/gitbook_worker/tools/emoji/report.py`, and link audits reside under `.github/gitbook_worker/tools/quality`. This document keeps historical context for the migration rationale.【F:.github/gitbook_worker/tools/emoji/report.py†L1-L116】【F:.github/gitbook_worker/tools/quality/staatenprofil_links.py†L1-L78】
- The standalone workflow suite under `.github/gitbook_worker/tools` already provides a structured orchestration layer, selective publishing pipeline, and developer helpers that are ready for reuse by GitHub Actions and local contributors.【F:.github/gitbook_worker/tools/README.md†L1-L156】【F:.github/gitbook_worker/tools/workflow_orchestrator/orchestrator.py†L1-L134】
- The legacy `tools/gitbook-worker` package duplicates many of those responsibilities, carries packaging quirks (hyphenated module name) and mixes unrelated CLIs, which prevents it from being imported cleanly in CI and makes maintenance costly.【F:tools/gitbook-worker/src/gitbook-worker/__init__.py†L12-L103】【F:tools/gitbook-worker/src/gitbook-worker/__main__.py†L36-L200】
- Migrating the unique capabilities (AI-assisted reference repair, source extraction, link checks) into dedicated subpackages inside `.github/gitbook_worker/tools` lets the Actions workflows depend on a single toolbox while retiring the root-level project.

## Findings

### `.github/gitbook_worker/tools` workflow suite

- The README documents three coherent pillars—workflow orchestration, publishing utilities, and developer helpers—along with clear entry points (`python -m tools.workflow_orchestrator`, `publishing/pipeline.py`, CSV converter).【F:.github/gitbook_worker/tools/README.md†L7-L114】
- `workflow_orchestrator/orchestrator.py` resolves `publish.yml` profiles, composes steps such as `check_if_to_publish`, `converter`, and `publisher`, and standardises environment setup, so new functionality only needs to implement another step script.【F:.github/gitbook_worker/tools/workflow_orchestrator/orchestrator.py†L1-L134】
- Helper modules already cover Docker lifecycle management and subprocess execution (`utils/docker_runner.py`, `utils/run.py`) in a cross-platform, well-logged manner, which we can leverage instead of maintaining parallel code paths.【F:.github/gitbook_worker/tools/utils/docker_runner.py†L1-L120】【F:.github/gitbook_worker/tools/utils/run.py†L9-L29】
- The publishing package owns Pandoc orchestration, Markdown preprocessing, GitBook summary maintenance, and manifest flag handling, so we should reuse these primitives rather than rebuild them elsewhere.【F:.github/gitbook_worker/tools/publishing/publisher.py†L1-L198】【F:.github/gitbook_worker/tools/publishing/preprocess_md.py†L1-L200】

### `tools/gitbook-worker` package

- The package directory is named `gitbook-worker`, forcing a compatibility shim that injects `gitbook_worker.src.gitbook_worker` into `sys.modules` to satisfy imports, a pattern that breaks packaging conventions and triggered the earlier `ModuleNotFoundError` in CI.【F:tools/gitbook-worker/src/gitbook-worker/__init__.py†L12-L103】
- The monolithic CLI (`__main__.py`) couples cloning, Docker invocation, PDF generation, linting, AI-powered citation repair, link checking, readability reports, and spellchecking behind dozens of flags, making the code hard to test or reuse piecemeal.【F:tools/gitbook-worker/src/gitbook-worker/__main__.py†L36-L200】
- Utility modules implement their own subprocess runner, Docker checks, and Pandoc command builders even though richer implementations already exist in `.github/gitbook_worker/tools`, leading to drift and duplicated bug fixes.【F:tools/gitbook-worker/src/gitbook-worker/utils.py†L25-L107】【F:tools/gitbook-worker/src/gitbook-worker/docker_tools.py†L11-L94】【F:tools/gitbook-worker/src/gitbook-worker/pandoc_utils.py†L7-L107】
- Several features are still valuable—AI-backed citation validation (`ai_tools.py`), structured source extraction (`source_extract.py`), HTTP/image link scanning (`linkcheck.py`), and Git repo cloning helpers (`repo.py`)—but they live in the legacy package and are inaccessible to the Actions tooling today.【F:tools/gitbook-worker/src/gitbook-worker/ai_tools.py†L17-L198】【F:tools/gitbook-worker/src/gitbook-worker/source_extract.py†L1-L120】【F:tools/gitbook-worker/src/gitbook-worker/linkcheck.py†L8-L93】【F:tools/gitbook-worker/src/gitbook-worker/repo.py†L22-L71】

## Migration proposal

1. **Create a `.github/gitbook_worker/tools/quality` package.**
   - Port `source_extract.py` and `linkcheck.py` into focused modules (e.g. `quality/sources.py`, `quality/link_audit.py`) that rely on `tools.logging_config` and `utils.run` for consistent logging/output.【F:tools/gitbook-worker/src/gitbook-worker/source_extract.py†L1-L120】【F:tools/gitbook-worker/src/gitbook-worker/linkcheck.py†L8-L93】【F:.github/gitbook_worker/tools/utils/run.py†L9-L29】
   - Reimplement the CLI as small entry points (`python -m tools.quality.link_audit`) so the workflow orchestrator can call them as dedicated steps.

2. **Move AI-assisted reference tooling.**
   - Translate `ai_tools.py` into `.github/gitbook_worker/tools/quality/ai_references.py`, keeping the JSON parsing, retry handling, and prompt schema logic while swapping to repository-wide logging helpers and environment configuration.【F:tools/gitbook-worker/src/gitbook-worker/ai_tools.py†L17-L198】【F:.github/gitbook_worker/tools/logging_config.py†L1-L80】
   - Break the legacy `CitationFixer` flow into importable primitives—`load_reference_tasks`, `call_model`, and `apply_fixes`—so that both CLI usage and automated workflows can stitch together the same behaviour without going through argparse plumbing.【F:tools/gitbook-worker/src/gitbook-worker/ai_tools.py†L32-L198】
   - Expose a thin `python -m tools.quality.ai_references` entry point that mirrors the existing `--ai-reference-repair` flag, accepting a manifest path and emitting a machine-readable report (JSON or SARIF) in addition to STDOUT so Actions can surface annotations.
   - Support both OpenAI-compatible APIs and locally hosted inference backends by resolving credentials from the orchestrator's environment section and letting callers override the base URL/model via kwargs, matching the flexibility already present in other `.github/gitbook_worker/tools` modules.【F:.github/gitbook_worker/tools/workflow_orchestrator/orchestrator.py†L71-L118】
   - Add orchestrator support for an optional `ai-reference-check` step that feeds manifest-selected Markdown files into the new module, allowing CI opt-in without touching legacy code paths.【F:.github/gitbook_worker/tools/workflow_orchestrator/orchestrator.py†L29-L125】
   - Document migration guidance in the README: deprecate `tools/gitbook-worker --ai-reference-repair`, point consumers to the new module, and outline how to configure API keys in local `.env` files so contributors retain feature parity after the move.【F:.github/gitbook_worker/tools/README.md†L115-L156】

3. **Consolidate repository and Docker helpers.**
   - Stand up `.github/gitbook_worker/tools/utils/git.py` with `clone_or_update_repo`, `checkout_branch`, and `remove_tree`, rewritten to use the shared logging-aware runner so Git flows behave the same in CI and locally without the interactive prompts that complicate workflow automation.【F:tools/gitbook-worker/src/gitbook-worker/repo.py†L9-L71】【F:.github/gitbook_worker/tools/utils/run.py†L9-L29】
   - Update the workflow orchestrator and the in-flight quality modules to import the new Git helpers, replacing the legacy `gitbook_worker` entry points and keeping Actions functional once the `github_worker` shim is removed.【F:tools/gitbook-worker/src/gitbook-worker/__main__.py†L244-L284】【F:.github/gitbook_worker/tools/workflow_orchestrator/orchestrator.py†L63-L122】
   - Wrap `tools/gitbook-worker/repo.py` and `docker_tools.py` around the new utilities with deprecation warnings so existing consumers keep working until the retirement window closes, then schedule their deletion alongside the `github_worker` shutdown.【F:tools/gitbook-worker/src/gitbook-worker/repo.py†L22-L71】【F:tools/gitbook-worker/src/gitbook-worker/docker_tools.py†L11-L94】
   - Replace `ensure_docker_image`/`ensure_docker_desktop` with orchestrator-facing adapters that call `utils/docker_runner.py`, ensuring consistent daemon checks, image builds, and OS-specific handling across every entry point before we drop the legacy package.【F:tools/gitbook-worker/src/gitbook-worker/docker_tools.py†L11-L94】【F:.github/gitbook_worker/tools/utils/docker_runner.py†L1-L118】

4. **Retire duplicate Pandoc glue.**
   1. **Inventory and diff functionality.**
       - Catalogue every helper in `pandoc_utils.py` (local CLI wrapper, Docker entry point, argument normalisers, logging helpers) and map them to their closest equivalents inside `tools.publishing`.【F:tools/gitbook-worker/src/gitbook-worker/pandoc_utils.py†L7-L107】【F:.github/gitbook_worker/tools/publishing/publisher.py†L665-L779】
      - Build a comparison matrix of command-line flags and Lua filters to confirm which options (`--toc-depth`, `--pdf-engine`, geometry overrides, filters) are already wired through `_run_pandoc` and which need to be ported.
      - Flag deprecated or redundant knobs (e.g. duplicated verbosity toggles) so the unified path stays focused on the options we actually exercise in manifests.
   2. **Merge missing switches into the maintained path.**
      - Extend `_run_pandoc` (and the higher-level `convert_*` helpers) to accept any missing arguments surfaced by the diff, ensuring we preserve compatibility for book builds, standalone PDFs, and any CI automation that depends on custom templates.【F:.github/gitbook_worker/tools/publishing/publisher.py†L86-L284】
      - Add regression coverage in `.github/tests/publishing` that asserts Pandoc receives the expected flag set for representative invocations (PDF with defaults, PDF with runtime overrides, JSON-configured defaults) before deleting the legacy helper.【F:.github/tests/test_publisher.py†L1-L420】
      - Update the publishing README or docstrings to advertise the new parameters so downstream callers can switch without spelunking through git history.【F:.github/gitbook_worker/tools/README.md†L115-L156】
   3. **Document the single-container contract.**
      - Keep `_run_pandoc` focused on the host binary; the orchestrator-provided Docker image or the developer's local environment is responsible for ensuring Pandoc and LaTeX are present so we never spawn containers from inside `publisher.py`.
      - Describe in the README which workflows supply Pandoc (GitHub-hosted runners, `.github/gitbook_worker/tools` Docker image, local installs) and surface the new `ERDA_PANDOC_DEFAULTS_JSON`/`ERDA_PANDOC_DEFAULTS_FILE` hooks for tweaking default flags without editing the codebase.【F:.github/gitbook_worker/tools/README.md†L64-L123】【F:.github/gitbook_worker/tools/publishing/publisher.py†L93-L224】
      - Provide migration guidance for callers that previously relied on `tools/gitbook-worker`'s Docker helpers, pointing them to the orchestrator profiles if they need a containerised run.
   4. **Fold specialised preprocessing into the shared pipeline.**
      - Redirect consumers of `wrap_wide_tables` and related markdown mungers to the canonical preprocessing flow (`preprocess_md.py`) or lift any missing transformations into that module so we have a single, ordered set of mutations.【F:tools/gitbook-worker/src/gitbook-worker/utils.py†L175-L260】【F:.github/gitbook_worker/tools/publishing/preprocess_md.py†L303-L355】
      - While migrating, add fixtures that reproduce the table/layout edge cases the legacy helper solved to ensure the consolidated pipeline keeps the same rendering guarantees.
   5. **Remove the duplicate module.**
      - Deprecate `pandoc_utils.py` with a short-lived shim that imports and re-exports the new functions, log a warning on use, and schedule its deletion once all callers have been flipped.
      - As a final verification, run representative book builds (HTML, PDF, summary-only) through the orchestrator to confirm the combined preprocessing, Lua filters, and single-container execution produce identical artefacts before deleting the shim.

5. **Plan the shutdown of `tools/gitbook-worker`.**
   - Once the above modules are migrated and wired into the orchestrator, delete the legacy package, keep only lightweight wrappers (e.g. CLI stubs) if external automation still imports `gitbook_worker`, and update the repository documentation to mark the root-level `tools/` folder as deprecated.【F:tools/gitbook-worker/src/gitbook-worker/__init__.py†L12-L103】【F:.github/gitbook_worker/tools/README.md†L147-L156】
   - Add regression tests inside `.github/tests` for the new quality modules to mirror the existing coverage pattern for publishing helpers.【F:.github/tests/README.md†L1-L72】

This approach lets GitHub Actions ignore the root `tools/` tree, keeps publishing and Docker topics within the already mature workflow suite, and focuses future maintenance on a single Python project.
