# GitBook Worker package

GitBook Worker is a standalone Python package (v1.0.2) that automates PDF
publishing, conversion utilities, and QA checks for GitBook projects. Install it
from the repository root and use the CLI locally or in CI.

## Installation

```bash
python -m pip install --upgrade pip
pip install -e .
```

The package exposes the console script `gitbook-worker` and the module entry
point `python -m gitbook_worker.tools.workflow_orchestrator`.

## Components

- `tools/workflow_orchestrator/` – orchestrator CLI that wires together the
  publishing steps defined in `publish.yml`.
- `tools/publishing/` – PDF build pipeline, front matter helpers, font handling.
- `tools/converter/` – CSV to Markdown/chart helpers for GitBook assets.
- `tools/emoji/` and `tools/quality/` – emoji completeness checks and link/source
  auditing.
- `tools/docker/` – Dockerfiles and helper scripts to mirror the CI environment.
- `defaults/` – baseline YAML configuration shipped with the package.
- `scripts/` – thin wrappers for Docker orchestration and local convenience.

## Running the orchestrator

```bash
# Use default profile defined in publish.yml
python -m gitbook_worker.tools.workflow_orchestrator --profile default --manifest publish.yml

# Use the installed console script
gitbook-worker --profile local --manifest publish.yml
```

## Tests

Run the pytest suite from repository root so the package and fixtures resolve
correctly:

```bash
pytest -q
```
