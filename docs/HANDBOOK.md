---
version: 1.1.0
date: 2025-06-01
history: Added contributor quickstart, troubleshooting, and Docker image guidance.
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

## Docker usage paths
- Prefer the dynamic image (`gitbook_worker/tools/docker/Dockerfile.dynamic`) for CI and local runs—it keeps font and LaTeX packages aligned with the publishing defaults.
- The static image (`gitbook_worker/tools/docker/Dockerfile`) remains available for air-gapped hosts; pass `--no-build` to wrapper scripts only when the desired image tag already exists.

## Migration pointers
- Treat `gitbook_worker/docs/archive/legacy-package/` as historical background; copy only distilled details back into this handbook.
- Prefer small, reviewable commits with a short rationale alongside notable behavior changes.
