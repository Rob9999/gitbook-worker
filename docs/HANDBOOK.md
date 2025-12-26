---
version: 1.2.0
date: 2025-12-07
history: Added font fallback reporting and abort semantics for PDF builds.
---

# GitBook Worker Handbook

This handbook replaces the sprawling legacy tree (now archived under
`gitbook_worker/docs/archive/legacy-package/`) with a concise,
maintained reference. The legacy archive remains read-only for deep dives.

## Package layout at a glance
- `content.yaml` lists all languages (currently `de/` live, `en/` staging, `ua/` remote) and feeds the CLI via `--lang`.
- Per-language content lives under `<lang>/` (`de/` already contains `content/`, `book.json`, `publish/`, etc.).
- Python package lives at repository root under `gitbook_worker/` and exposes the `gitbook-worker` console script.
- Tests reside in `tests/` and cover publishing, orchestrator flows, and emoji/font QA.
- CI workflows under `.github/workflows/` mirror local usage by building the Docker image and invoking the same CLI entrypoints.
- User-facing docs belong in `docs/`, engineering/sprint notes in `gitbook_worker/docs/` (per `AGENTS.md`).

## Local development essentials
- Install dependencies with `pip install -r requirements.txt` and run quick checks via `pytest -q` from the repository root.
- When editing YAML planning docs, keep the front matter (`version`, `date`, `history`) in sync with the change.
- The deprecated `tools/` shim exists only for legacy imports—prefer `gitbook_worker.*` everywhere else.
- Remote Sprachbäume mit `type: git` werden automatisch nach `.gitbook-content/<id>` geklont; setze die in `credentialRef` genannte Env-Variable auf einen SSH-Key (Pfad oder Inhalt), sonst schlägt der Build fehl.

## Contributor quickstart
- Install in editable mode: `pip install -e .` from the repository root.
- Validate manifests quickly: `gitbook-worker validate --lang de` (does not run the pipeline).
- Run a local build: `./gitbook_worker/scripts/build-pdf.sh --profile local --manifest de/publish.yml` or `gitbook-worker run --lang de --profile default`.
- Execute targeted tests during iterations: `pytest tests/test_publisher.py tests/test_orchestrator_validate.py` (fixtures now resolve the default language via `content.yaml`).

### Adding or updating language trees
- Copy the structure from `de/` (or an existing language) and adjust `content/`, `book.json`, `publish/`, and attribution/licensing files for the new locale.
- Append the new entry to `content.yaml` with a unique `id`, `type`, and `uri`; remote repos require a `credentialRef` so secrets remain outside git.
- Keep shared defaults in sync: `gitbook_worker/defaults/frontmatter.yml`, `fonts.yml`, and `readme.yml` should match across languages to avoid divergent PDFs/HTML.
- Reference assets that all languages consume (fonts, templates, logos) from shared folders instead of duplicating them per language; update the contributor how-to (`docs/contributor-new-language.md`) whenever the process changes.
- Verify the addition with `gitbook-worker validate --lang <id>` followed by a targeted `pytest -k <id>` run if you introduced locale-specific tests.

## Troubleshooting
- If PDF output misses images, ensure the source directory is covered by Pandoc `--resource-path` (handled automatically by the publisher helper) and that assets live under `assets/` or `.gitbook/assets/`.
- For font issues, confirm Twemoji/ERDA fonts are installed in the Docker image; the dynamic Dockerfile bundles them by default.
- Enable verbose orchestrator analytics by reviewing log entries containing `Orchestrator analytics` after failures.

## CI guardrails
- Unit tests enforce coverage via `pytest ... --cov=gitbook_worker --cov-fail-under=45` and publish `coverage.xml` as an artifact.
- A dedicated `type-check` job runs `mypy` against the package on Python 3.12 with project dependencies installed.
- Integration tests validate PDF rendering inside the Docker image and confirm Twemoji + ERDA CJK fonts are present before running slow suites.

## Publishing and fonts (field notes)
- The dynamic Docker build installs TeX Live and Pandoc, then applies font setup driven by repository configuration rather than hardcoded fonts.
- If integration tests report missing emoji or CJK fonts, ensure Twemoji and ERDA CC-BY CJK are available in the runner or rebuild the Docker image so the font check passes.
- Repository builds now keep vendor fonts out of git: `fonts-storage/` (ignored) is populated automatically by `gitbook_worker.tools.publishing.font_storage.FontStorageBootstrapper` during `fonts sync` and orchestrator runs. Delete the folder to force a refresh or set `GITBOOK_WORKER_DISABLE_FONT_STORAGE_BOOTSTRAP=1` when developing offline.

### PDF font fallback behavior

1. Missing glyph detection and reporting
The PDF build shall detect whenever a glyph required by the document cannot be rendered by the configured primary fonts. For all such cases, the build shall produce a clear, detailed report listing:
- the affected code points (and, if possible, their Unicode names),
- the fonts that were attempted,
- and the fact that they could not provide a valid glyph (i.e. the result would be a .notdef / empty box).
This report shall be written to the build log for troubleshooting.

2. Use of the mainfontfallback stack
The `mainfontfallback` stack exists to prevent missing-glyph boxes, not just to check font availability. For every glyph that the primary fonts cannot render, the PDF build shall try each font in the `mainfontfallback` stack in order and use the first fallback font that can provide a proper glyph (e.g. a regular text glyph, emoji glyph, etc.). As long as every required glyph can be rendered either by a primary font or by at least one font in the `mainfontfallback` stack, the PDF build shall succeed and no .notdef / empty box glyphs shall appear in the output.

3. Abort condition
The PDF build shall abort only if, after trying all configured primary fonts and all fonts in the `mainfontfallback` stack, there remains at least one required glyph that would still be rendered as a missing-glyph box (.notdef). In that case, the pipeline shall fail and emit the detailed missing-glyph report described in (1), instead of silently producing a PDF with empty boxes.

Control: In `publish.yml` you can disable aborting while still logging the report via `pdf_options.abort_if_missing_glyph: false` (default: true).

4. Central font configuration
a) All fonts, including the primary ones and the `mainfontfallback` ones, shall be configured exclusively in `gitbook_worker/defaults/fonts.yml`. 
b) In the unique book project `publish.yml` then is defined which fonts finally shall be used for the book project; e.g. as main font, as, sans font, as ... font, as mainfont fallback. 
c) The publishing header shall apply the configured fallback stack automatically; individual documents shall not configure their own font fallback behavior.


## Docker usage paths
- Prefer the dynamic image (`gitbook_worker/tools/docker/Dockerfile.dynamic`) for CI and local runs—it keeps font and LaTeX packages aligned with the publishing defaults.
- The static image (`gitbook_worker/tools/docker/Dockerfile`) remains available for air-gapped hosts; pass `--no-build` to wrapper scripts only when the desired image tag already exists.

### Running builds in Docker
**Local execution (NO Docker)**:
```bash
# Runs on your local machine (uses local TeX Live, Python, fonts)
python -m gitbook_worker.tools.workflow_orchestrator run --lang de --profile local
```

**Docker execution (isolated container)**:
```bash
# Builds Docker image and runs orchestrator INSIDE container
python -m gitbook_worker.tools.docker.run_docker orchestrator --profile default --use-dynamic --rebuild

# Or with convenience script
./gitbook_worker/scripts/run-in-docker.sh --lang de --profile default
```

**Key difference**: The `run_docker.py` module builds the Docker image, starts a container, mounts your workspace to `/workspace`, and executes `workflow_orchestrator` inside the container. The `workflow_orchestrator` has a `--profile docker` option but this is just a profile name—it does NOT trigger Docker execution.

## Migration pointers
- Treat `gitbook_worker/docs/archive/legacy-package/` as historical background; copy only distilled details back into this handbook.
- Prefer small, reviewable commits with a short rationale alongside notable behavior changes.
