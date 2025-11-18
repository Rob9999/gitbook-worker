# `.github` Project

Automation and publishing toolkit that powers this repository.  Treat this
folder as its own Python package; install dependencies inside `.github/.venv`
and run entry points via `python -m …` so the same commands work locally and in
GitHub Actions.

## Getting started

### Windows PowerShell

```powershell
cd .github
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

### macOS / Linux

```bash
cd .github
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Layout

* `gitbook_worker/tools/` – Python sources grouped by module (see
  [`gitbook_worker/tools/README.md`](gitbook_worker/tools/README.md) for an
  index and module links).
* `gitbook_worker/tests/` – pytest suites that exercise the orchestrator,
  publishing pipeline and helper scripts.
* `workflows/` – GitHub Actions definitions.
* `.vscode/` – recommended local run configurations targeting the local virtual
  environment.
* `fonts/` – CC BY 4.0 fallback font for the licence translations plus the
  generator script used to rebuild it.

## Workflow orchestrator

The canonical entry point is `python -m tools.workflow_orchestrator`.  It reads
`publish.yml`, resolves the selected profile and executes the configured steps.
Common invocations:

```bash
# Run the full publishing pipeline using the default profile
python -m tools.workflow_orchestrator --profile default --reset-others

# Minimal local run without touching GHCR
python -m tools.workflow_orchestrator --profile local --dry-run
```

Additional arguments are passed to downstream scripts with repeated
`--publisher-arg`, `--converter-arg`, etc.

## Docker images & GHCR

`orchestrator.yml` builds the publishing container and pushes it to GitHub
Container Registry (`ghcr.io/<owner>/<repo>/publisher`).  Private repositories
build the image on-demand without pushing.  Buildx cache is enabled to speed up
subsequent runs.

## Testing

Run `pytest` from within the `.github` directory or trigger the
`python-package` workflow manually via `workflow_dispatch`.  Tests for the
orchestrator live under `tests/workflow_orchestrator/`; converter and publishing
coverage resides in their respective subdirectories.

## Documentation

Reviews, sprint notes and publishing reports live under
`.github/gitbook_worker/project/docs/`.  Use the `reviews/` folder for post-run
analysis and the `sprints/` folder for forward-looking planning.
