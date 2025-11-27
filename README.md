# GitBook Worker (v2.0.0)

GitBook Worker now ships the multi-language 2.0.0 release. The Python package still
installs via `pip install -e .`, but the publishing pipeline is driven by
`content.yaml`, which lists every language tree (e.g., `de/`, `en/`). The CLI picks a
language via `--lang` and then runs the usual orchestration/publishing steps for that
content root.

## Quick start

```bash
python -m pip install --upgrade pip
pip install -e .

# Run the orchestrator against the German book
gitbook-worker run --lang de --profile default

# Validate a manifest without running the pipeline
gitbook-worker validate --lang de

# Pick a different language (if defined in content.yaml)
gitbook-worker run --lang en --step publisher
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

## Remote content sources

- Entries with `type: git` are cloned automatically into `.gitbook-content/<lang-id>`
  whenever you run `gitbook-worker ... --lang <id>`.
- Provide credentials through the environment variable named in `credentialRef`. The
  variable can contain either an absolute path to an SSH private key or the key contents
  themselves. Inline keys are written to `.gitbook-content/keys/<lang>.key` with
  restrictive permissions and used via `GIT_SSH_COMMAND`.
- If the credential is missing, the CLI aborts with a clear error so secrets never leak
  into manifests.
- To reuse an existing checkout (for example a CI cache), set `GITBOOK_CONTENT_ROOT` to
  the path of the prepared language tree and the CLI will skip cloning.

## Add another language tree

1. Duplicate the structure from `de/` (or start from an empty remote repo) so the new
  language has `content/`, `book.json`, `publish/`, and optional assets.
2. Append an entry to `content.yaml` with the new language `id`, `type`, and `uri`. For
  remote sources, define a `credentialRef` and store the secret outside git.
3. Sync shared defaults (front matter, fonts, README snippets) from
  `gitbook_worker/defaults/` so PDF/HTML output matches the other languages.
4. Run `gitbook-worker validate --lang <id>` (or `run`) to ensure manifests and publish
  targets resolve.
5. Document any special steps in `docs/contributor-new-language.md` so the rest of the
  team can reproduce the setup.

The dedicated contributor walkthrough lives in `docs/contributor-new-language.md`.

## Repository layout

- `content.yaml` – lists every language/content source plus credential handles.
- `<lang>/` (e.g., `de/`, `en/`) – self-contained GitBook trees containing `content/`,
  `book.json`, `publish/`, `CITATION.cff`, etc. `de/` currently holds the full ERDA book.
- `gitbook_worker/` – Python package with publishing, conversion, QA, and Docker helpers.
- `docs/` – user-facing guides (e.g., `docs/multilingual-content-guide.md`,
  `docs/contributor-new-language.md`, `docs/releases/v2.0.0.md`).
- `gitbook_worker/docs/` – engineering docs such as sprint plans, migrations, RFCs, and
  the archived legacy package snapshot under `gitbook_worker/docs/archive/`.
- `tests/` – pytest suites covering publishing, orchestration, and emoji QA.
- `.github/workflows/` – CI entrypoints using the packaged CLI.
- `tools/` – deprecated import shim for legacy `tools.*` paths (kept for compatibility).

## GitHub Actions templates

Workflows under `.github/workflows/` build the Docker image from
`gitbook_worker/tools/docker/Dockerfile.dynamic` and call the same orchestrator
entrypoint used locally. Copy or extend these workflows to integrate the package
into other repositories. The static image (`gitbook_worker/tools/docker/Dockerfile`)
remains available for air-gapped runners; the helper scripts default to the
dynamic variant so font and LaTeX dependencies stay in sync with CI.

## Development

- Add dependencies to `setup.cfg` and keep `__version__` in `gitbook_worker/__init__.py` in sync
  with the packaged release (currently 2.0.0).
- Run tests locally with `pytest -q` from the repository root; language-specific fixtures live
  under `de/` so CI can mount each tree independently.
- Preferred entrypoints: `python -m gitbook_worker.tools.workflow_orchestrator ...` or the
  console script `gitbook-worker` with `--lang <id>`.
- Remote languages are cached under `.gitbook-content/` so repeated runs reuse the same
  checkout while still pulling updates.
- Repository-wide conventions live in the root `AGENTS.md`; there are no nested overrides.
- Documentation placement: user docs in `docs/`, engineering docs in `gitbook_worker/docs/`.
