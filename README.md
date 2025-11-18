# GitBook Worker (v1.0.2)

Automation toolkit for GitBook-based projects. The Python package now lives at
repository root, can be installed via `pip install -e .`, and ships a CLI for
running the publishing pipeline locally or inside CI.

## Quick start

```bash
python -m pip install --upgrade pip
pip install -e .

# Run the orchestrator with the default profile
python -m gitbook_worker.tools.workflow_orchestrator --profile default --manifest publish.yml
```

## Repository layout

- `gitbook_worker/` – Python package with publishing, conversion, QA and Docker helpers.
- `tests/` – pytest suites covering publishing, orchestration and emoji QA.
- `.github/workflows/` – CI entrypoints using the packaged CLI.
- `tools/` – deprecated import shim for legacy `tools.*` paths.
- `.github/gitbook_worker/docs/` – legacy documentation archive (kept for history).

## GitHub Actions templates

The workflows under `.github/workflows/` build the Docker image from
`gitbook_worker/tools/docker/Dockerfile.dynamic` and run the same orchestrator
entrypoint used locally. Copy or extend these workflows to integrate the
package into other repositories.

## Development

- Add dependencies to `setup.cfg` and keep `__version__` in `gitbook_worker/__init__.py` in sync.
- Run tests locally with `pytest -q` from the repository root.
- CLI entrypoint: `python -m gitbook_worker.tools.workflow_orchestrator ...` or the
  installed console script `gitbook-worker`.
