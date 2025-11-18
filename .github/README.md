# `.github` Project

This folder now focuses on CI entrypoints and shared assets. The Python package
`gitbook_worker` lives at repository root and should be installed from there
(e.g. `pip install -e .`).

## Layout

- `workflows/` – GitHub Actions definitions that call the packaged CLI.
- `fonts/` – Legacy font assets used by the publishing pipeline.
- `gitbook_worker/docs/` – Historical documentation and sprint notes retained for reference; new docs live alongside the package at repository root.

## Local testing

Run tests from the repository root so the new package layout is discovered:

```bash
python -m pip install --upgrade pip
pip install -e .
pytest -q
```

For workflow debugging use `python -m gitbook_worker.tools.workflow_orchestrator` or
the console script `gitbook-worker`.
