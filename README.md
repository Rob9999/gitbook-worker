# GitBook Worker (v1.0.2)

GitBook Worker is a streamlined automation toolkit for GitBook-based projects. The
package lives at the repository root, installs with `pip install -e .`, and ships a
CLI for running the publishing pipeline locally or in CI.

## Quick start

```bash
python -m pip install --upgrade pip
pip install -e .

# Run the orchestrator with the default profile
python -m gitbook_worker.tools.workflow_orchestrator --profile default --manifest publish.yml

# Validate a manifest without running the pipeline
gitbook-worker validate --manifest publish.yml
```

## Repository layout

- `gitbook_worker/` – Python package with publishing, conversion, QA, and Docker helpers.
- `tests/` – pytest suites covering publishing, orchestration, and emoji QA.
- `.github/workflows/` – CI entrypoints using the packaged CLI.
- `tools/` – deprecated import shim for legacy `tools.*` paths.
- `.github/gitbook_worker/docs/` – legacy documentation archive retained for reference.

## GitHub Actions templates

Workflows under `.github/workflows/` build the Docker image from
`gitbook_worker/tools/docker/Dockerfile.dynamic` and call the same orchestrator
entrypoint used locally. Copy or extend these workflows to integrate the package
into other repositories. The static image (`gitbook_worker/tools/docker/Dockerfile`)
remains available for air-gapped runners; the helper scripts default to the
dynamic variant so font and LaTeX dependencies stay in sync with CI.

## Development

- Add dependencies to `setup.cfg` and keep `__version__` in `gitbook_worker/__init__.py` in sync.
- Run tests locally with `pytest -q` from the repository root.
- Preferred entrypoints: `python -m gitbook_worker.tools.workflow_orchestrator ...` or the
  console script `gitbook-worker`.
- Repository-wide conventions live in the root `AGENTS.md`; there are no nested overrides,
  so the file is the single source of truth for automation and documentation expectations.
