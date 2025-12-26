---
version: 0.4.0
date: 2025-11-25
history: Contributor-Workflow ergänzt, Shared-Asset-Sync dokumentiert, Frontmatter korrigiert.
---

# Multilingual Content Guide

This guide explains how we maintain, configure, and build multiple language variants of the book in parallel.

## Überblick
- Each language has its own folder (`<lang-id>/`) at the repository root. `de/` already holds the production book content (including `content/`, `book.json`, `publish/`).
- A central `content.yaml` in the root lists all language variants so scripts like `gitbook_worker` automatically know which content exists and where it lives.
- Credentials for external sources (for example Git repositories) are **not** stored in the YAML file; they are referenced via environment variables or secret stores (`credentialRef`).

## content.yaml
```yaml
version: 1.0.0
default: de
contents:
  - id: de
    uri: de/
    type: local
    description: German baseline content
  - id: en
    uri: en/
    type: local
    description: English content (WIP)
  - id: ua
    uri: github.com:rob9999@democratic-social-wins
    type: git
    description: Book about democratic society of Ukraine
    credentialRef: GITBOOK_CONTENT_UA_DEPLOY_KEY
```
**Felder**
- `version`: Schema version to keep future extensions migratable.
- `default`: Language built when no parameter is provided.
- `contents[]`: List of language definitions.
  - `id`: Short name, used for CLI flags (`--lang de`) and credential lookups.
  - `uri`: Root path (local) or remote source (Git/HTTP).
  - `type`: `local`, `git`, `archive`, etc., so the loader knows how to handle `uri`.
  - `description`: Short description for CLI output/docs.
  - `credentialRef`: Optional name of an environment variable or secret handle for protected sources.

## Language folder layout
```
repo/
  |- de/
  |   |- book.json
  |   |- content/
  |   |- CITATION.cff
  |   |- LICENSE
  |   |- publish/
  |   \- assets/ (optional)
  |- en/
  |- ua/
  |- gitbook_worker/
  |- tests/
  \- content.yaml
```
- `content/`: Markdown entries for the book (chapters, appendices, templates).
- `book.json`: Build settings for GitBook/CLI.
- `citation.cff`, `license/`, `publish/`: Artefacts shipped per language.
- Shared scripts/packages stay at the root (`gitbook_worker/`, `tests/`).

## Credential strategy
1. Store secrets per language in `.env.local` (for developers) or directly in CI (for example GitHub Secrets, Azure Key Vault).
2. Name the variable identically to the `credentialRef` from `content.yaml` (for example `GITBOOK_CONTENT_UA_DEPLOY_KEY`).
3. The CLI layer reads `content.yaml`, sees `credentialRef`, and loads the secret when needed. The value may be **a path** to a private SSH key or the **key content** itself. Inline keys are written to `.gitbook-content/keys/<lang>.key` with restrictive permissions. If the secret is missing, the build fails with a clear error message.

## Remote content and cache
- `type: git` entries are cloned automatically into `.gitbook-content/<lang-id>`. Subsequent runs update those checkouts rather than cloning from scratch.
- The secret from `credentialRef` is injected as `GIT_SSH_COMMAND` so deploy keys work without extra wrappers.
- If an external checkout already exists (for example a CI cache), set `GITBOOK_CONTENT_ROOT` to that path and the CLI skips the clone step.
 
## Contributor workflow (short version)
1. **Copy a structure or connect a remote** – duplicate `de/` as a template or connect an existing Git source via `type: git`.
2. **Extend `content.yaml`** – add a new `id`, `uri`, `type`, optionally `credentialRef`; change `default` only if another language should become the default build.
3. **Synchronise shared assets** – align front matter/fonts/README snippets across all languages (`gitbook_worker/defaults/*`).
4. **Validate and test** – `gitbook-worker validate --lang <id>` plus focused Pytests (`pytest -k <id>`), then extend the CI matrix.
5. **Update documentation** – capture changes in `docs/contributor-new-language.md` so the process stays traceable.

The detailed step-by-step guide lives in `docs/contributor-new-language.md`.

## Shared assets and templates
- `gitbook_worker/defaults/frontmatter.yml` – base metadata for PDF/Markdown; keep translations aligned so release banners and attribution match.
- `gitbook_worker/defaults/fonts.yml` – font configuration used by all language pipelines; test new fonts in one language before updating globally.
- `gitbook_worker/defaults/readme.yml` and `smart.yml` – define which files are combined during publish; add new chapters/appendices to all languages at the same time.
- Shared assets (logos, fonts, templates) should not be duplicated in individual language folders. Derive them from `gitbook_worker/defaults/` or `gitbook_worker/tools/assets/` and document exceptions.

## Open points / next steps
- CI matrix across all languages (including a smoke PDF per language) plus expanded tests for credential failure scenarios.
