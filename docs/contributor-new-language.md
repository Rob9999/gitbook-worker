---
version: 0.1.0
date: 2025-11-25
history: Erste Ausgabe mit Schritt-für-Schritt-Anleitung zum Hinzufügen neuer Sprachen.
---

# Contributor How-To: Neue Sprache anlegen

This how-to describes the full process from scaffolding a new language version to validation in CI. It complements the `README` and the Multilingual Guide with concrete checklists.

## Prerequisites
- Working `pip install -e .` environment and access to the repository root.
- Decide upfront whether the language lives locally in the repo or is delivered via an external Git repository (for example with private deploy keys).
- Ensure you can access shared assets (`gitbook_worker/defaults/*`), as these must stay synchronised across all languages.

## Step 1 – Duplicate a structure or connect a remote
1. Local variant: copy `de/` to `<lang-id>/` (example: `cp -R de en`). Remove chapters you do not need and translate content gradually.
2. Remote variant (`type: git`): ensure the target repository contains `content/`, `book.json`, `publish/`, and any optional assets. The Git URI must work without a protocol prefix (for example `github.com:owner/repo`).

## Step 2 – Extend `content.yaml`
1. Open `content.yaml` and extend `contents` with an entry such as:
   ```yaml
   - id: fr
     type: local
     uri: fr/
     description: French pilot content
   ```
2. For remote sources set `type: git`, `uri` (SSH/HTTPS), and a `credentialRef`, for example:
   ```yaml
   - id: ua
     type: git
     uri: github.com:rob9999@democratic-social-wins
     credentialRef: GITBOOK_CONTENT_UA_DEPLOY_KEY
   ```
3. Adjust `default` only if another language should be built automatically.

## Step 3 – Provide credentials (optional)
1. Create a secret or local environment variable using the name from `credentialRef`.
2. Accepted values:
   - absolute path to a private SSH key (`C:\Keys\gitbook_ua`), or
   - the key content itself (including `-----BEGIN OPENSSH PRIVATE KEY-----`).
3. Inline values are written automatically to `.gitbook-content/keys/<lang>.key` and used via `GIT_SSH_COMMAND`. The key is created with read access for the current user only.
4. Check with `gitbook-worker validate --lang <id>` to confirm cloning works without a password prompt. On failure the CLI provides a targeted message.

## Step 4 – Synchronise shared assets
1. Carry over changes from `gitbook_worker/defaults/frontmatter.yml`, `fonts.yml`, and `readme.yml` into your new language (for example translated titles but the same structure).
2. Keep `gitbook_worker/defaults/smart.yml` and global templates consistent so the publish process generates identical artefacts per language.
3. Shared logos, fonts, or macros do not belong in individual language folders. Refer to existing files or add new assets centrally instead.

## Step 5 – Local validation
1. Run `gitbook-worker validate --lang <id>` to check the manifest, fonts, and publish options.
2. Optional: `gitbook-worker run --lang <id> --profile default` generates the publish set directly under `<lang>/publish/` (or the cloned cache).
3. Adapt tests if you need language-specific fixtures. Example:
   ```powershell
   pytest gitbook_worker/tests/test_pipeline.py -k <id>
   ```

## Step 6 – Update CI and documentation
1. Add new languages to workflow matrices (for example `matrix.lang` in GitHub Actions) and ensure required secrets are present.
2. Update `docs/multilingual-content-guide.md` and this how-to if the process changes or additional assets must be synchronised.
3. Record special considerations (for example external tools, glossaries) in `docs/HANDBOOK.md` so the onboarding team is informed.

## References
- `README.md` – overview of the repository structure and remote source rules.
- `docs/multilingual-content-guide.md` – detailed description of `content.yaml`, credential strategies, and the overall workflow.
- `gitbook_worker/tools/utils/language_context.py` – source of the logic that loads `content.yaml` and caches remote repositories.
