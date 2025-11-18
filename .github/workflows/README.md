# GitHub Actions Workflows

Continuous integration and publishing workflows for GitBook Worker.

## Active workflows

### `orchestrator.yml`
- Builds `gitbook_worker/tools/docker/Dockerfile.dynamic`.
- Runs the packaged orchestrator via `gitbook-worker --profile <profile>`.
- Profiles are read from `publish.yml` in the repository root.

### `test.yml`
- Builds the same Docker image and executes the pytest suites under `tests/`.
- Supports `unit`, `integration`, `emoji-harness`, `qa`, and `all` test suites.

## Local equivalents

```bash
# Install package
yarn install --frozen-lockfile  # if docs/assets are needed
pip install -e .

# Run orchestrator locally
python -m gitbook_worker.tools.workflow_orchestrator --profile default --manifest publish.yml

# Run tests
pytest -q
```

## Migration notes

The Python package previously lived under `.github/gitbook_worker/`. All tools and
workflows now target the root-level package. The legacy documentation archive is
kept in `.github/gitbook_worker/docs/` for reference.
