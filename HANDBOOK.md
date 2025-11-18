---
version: 1.0.0
date: 2025-05-30
history: Condensed root-level handbook derived from legacy docs and current CI setup.
---

# GitBook Worker Handbook

This handbook replaces the sprawling `.github/gitbook_worker/docs/` tree with a concise,
maintained reference. The legacy archive remains read-only for deep dives.

## Package layout at a glance
- Python package lives at repository root under `gitbook_worker/` and exposes the `gitbook-worker` console script.
- Tests reside in `tests/` and cover publishing, orchestrator flows, and emoji/font QA.
- CI workflows under `.github/workflows/` mirror local usage by building the Docker image and invoking the same CLI entrypoints.

## Local development essentials
- Install dependencies with `pip install -r requirements.txt` and run quick checks via `pytest -q` from the repository root.
- When editing YAML planning docs, keep the front matter (`version`, `date`, `history`) in sync with the change.
- The deprecated `tools/` shim exists only for legacy imports—prefer `gitbook_worker.*` everywhere else.

## CI guardrails
- Unit tests enforce coverage via `pytest ... --cov=gitbook_worker --cov-fail-under=45` and publish `coverage.xml` as an artifact.
- A dedicated `type-check` job runs `mypy` against the package on Python 3.12 with project dependencies installed.
- Integration tests validate PDF rendering inside the Docker image and confirm Twemoji + ERDA CJK fonts are present before running slow suites.

## Publishing and fonts (field notes)
- The dynamic Docker build installs TeX Live and Pandoc, then applies font setup driven by repository configuration rather than hardcoded fonts.
- If integration tests report missing emoji or CJK fonts, ensure Twemoji and ERDA CC-BY CJK are available in the runner or rebuild the Docker image so the font check passes.

## Migration pointers
- Treat `.github/gitbook_worker/docs/` as historical background; copy only distilled details back into this handbook.
- Prefer small, reviewable commits with a short rationale alongside notable behavior changes.
