---
version: 0.1.0
date: 2026-01-13
history:
  - version: 0.1.0
    date: 2026-01-13
    description: Record of release-procedure verification runs for v2.1.0 (no version bump)
---

# Release procedure run log (v2.1.0)

Goal: Follow [gitbook_worker/docs/how-to-release/release-procedure.md](../how-to-release/release-procedure.md) for verification steps, while explicitly staying on `2.1.0` (no version bump, no tagging).

## Snapshot commit

- Commit: `15c00ff` — "Hexagonal: add PDF TOC port/use-case/adapter"

## Step 2 — Local orchestrator runs

Executed:

- `python -m gitbook_worker.tools.workflow_orchestrator run --root C:\gitbook-worker --content-config content.yaml --lang de --profile local`
- `python -m gitbook_worker.tools.workflow_orchestrator run --root C:\gitbook-worker --content-config content.yaml --lang en --profile local`

Optional TOC verification:

- `python -m gitbook_worker.tools.utils.pdf_toc_extractor --pdf de/publish/das-erda-buch.pdf --format text`
- `python -m gitbook_worker.tools.utils.pdf_toc_extractor --pdf en/publish/the-erda-book.pdf --format text`

Result:

- Local runs completed successfully and PDFs were generated.

## Step 3 — Docker-based orchestrator run

Note:

- The repo root `content.yaml` does not include `customer-de`; it only includes `de`, `en`, `ua`.
- Therefore, the Docker run must use `customer-de/content.yaml` as `--content-config`.
- This is for *verification only*; no customer content/config was committed as part of this release-run log.

Executed:

- `python -m gitbook_worker.tools.docker.run_docker orchestrator --use-dynamic --profile default --content-config customer-de/content.yaml --lang customer-de --isolated --logs-dir logs/docker`

Result:

- Command completed successfully.
- TeX output contained expected `Overfull \hbox` warnings and some "Missing character" warnings for non-Latin scripts; build still succeeded.

## Step 4 — Tests

Executed:

- `python -m pytest gitbook_worker/tests -m "not slow" -q`

Result:

- `387 passed, 11 skipped, 10 deselected`
- Warnings: 4× `DeprecationWarning` about `pathlib.Path.__enter__()` being deprecated in Python 3.13 (from `gitbook_worker/tools/publishing/publisher.py`).

## Step 6 — Pip install smoke test

Executed:

- `python -m build`
- Fresh venv `.venv-smoke` created
- Installed wheel from `dist/` and ran:
  - `python -m gitbook_worker.tools.workflow_orchestrator --help`

Result:

- Wheel install succeeded and `--help` exited successfully.

## Deviations / notes

- Stayed on `2.1.0` intentionally: no version bump, no release notes file added under `docs/releases/`, and no tag created.
- Any manual PDF quality review remains a human step.
