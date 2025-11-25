# GitBook Worker (v2.0.0-dev)

GitBook Worker now targets a multi-language 2.0.0 release. The Python package still
installs via `pip install -e .`, but the publishing pipeline is driven by
`content.yaml`, which lists every language tree (e.g., `de/`, `en/`). The CLI picks a
language via `--lang` and then runs the usual orchestration/publishing steps for that
content root.

## Quick start

```bash
python -m pip install --upgrade pip
pip install -e .

# Run the orchestrator against the German book
gitbook-worker run --lang de --manifest de/publish.yml --profile default

# Validate a manifest without running the pipeline
gitbook-worker validate --lang de --manifest de/publish.yml

# Pick a different language (if defined in content.yaml)
gitbook-worker run --lang en --manifest en/publish.yml --step publisher
```

`content.yaml` is the single source of truth for available languages:

```yaml
version: 1.0.0
default: de
contents:
  - id: de
    type: local
    uri: de/
    description: German baseline content
  - id: ua
    type: git
    uri: github.com:rob9999@democratic-social-wins
    credentialRef: GITBOOK_CONTENT_UA_DEPLOY_KEY
```

The orchestrator reads this file automatically; remote entries will later use
`credentialRef` to fetch private content via env secrets or CI secret stores.

## Repository layout

- `content.yaml` – lists every language/content source plus credential handles.
- `<lang>/` (e.g., `de/`, `en/`) – self-contained GitBook trees containing `content/`,
  `book.json`, `publish/`, `CITATION.cff`, etc. `de/` currently holds the full ERDA book.
- `gitbook_worker/` – Python package with publishing, conversion, QA, and Docker helpers.
- `docs/` – user-facing guides (e.g., `docs/multilingual-content-guide.md`).
- `gitbook_worker/docs/` – engineering docs such as sprint plans, migrations, and RFCs.
- `tests/` – pytest suites covering publishing, orchestration, and emoji QA.
- `.github/workflows/` – CI entrypoints using the packaged CLI.
- `tools/` – deprecated import shim for legacy `tools.*` paths (kept for compatibility).
- `.github/gitbook_worker/docs/` – legacy documentation archive retained for reference.

## GitHub Actions templates

Workflows under `.github/workflows/` build the Docker image from
`gitbook_worker/tools/docker/Dockerfile.dynamic` and call the same orchestrator
entrypoint used locally. Copy or extend these workflows to integrate the package
into other repositories. The static image (`gitbook_worker/tools/docker/Dockerfile`)
remains available for air-gapped runners; the helper scripts default to the
dynamic variant so font and LaTeX dependencies stay in sync with CI.

## Development

- Add dependencies to `setup.cfg` and keep `__version__` in `gitbook_worker/__init__.py` in sync
  when we tag 2.0.0.
- Run tests locally with `pytest -q` from the repository root; language-specific fixtures live
  under `de/` so CI can mount each tree independently.
- Preferred entrypoints: `python -m gitbook_worker.tools.workflow_orchestrator ...` or the
  console script `gitbook-worker` with `--lang <id>`.
- Repository-wide conventions live in the root `AGENTS.md`; there are no nested overrides.
- Documentation placement: user docs in `docs/`, engineering docs in `gitbook_worker/docs/`.
