---
version: 2.0.0
date: 2025-11-24
history: Initial sprint plan for multi-language GitBook Worker release.
---

# Sprint: Multilingual GitBook Worker 2.0.0

## Goals
- Finalise the multi-language repository layout (per-language roots, shared tooling) and keep `content.yaml` authoritative.
- Refactor the GitBook Worker CLI/pipeline so every step runs against a selected language without manual path overrides.
- Provide credential-aware handling for remote content sources and keep secrets outside of manifest/config files.
- Update docs, automation, and release artefacts so contributors and CI can build and publish every language variant consistently.

## Work items
1. ☐ **Baseline repo hygiene** – ensure `de/` hosts the current book, wire `content.yaml` into README/docs, and add scaffolding/tests for future `en/`, `ua/` trees.
2. ☐ **Smart content loader** – finish `smart_content.py` integration across CLI entrypoints (orchestrator, pipeline, publisher) + environment variables for downstream scripts.
3. ☐ **Pipeline + publisher refactor** – make `dump_publish`, converter, and publisher compute paths relative to the selected language root and update tests/fixtures accordingly.
4. ☐ **Remote source + credential flow** – teach the orchestrator to clone/fetch `type: git` entries using `credentialRef` handles (env/secret store) and document the workflow.
5. ☐ **Docs & DX updates** – refresh README, handbook, and `docs/multilingual-content-guide.md`; add contributor how-to for adding a new language and syncing shared assets.
6. ☐ **Release readiness** – bump package metadata to `2.0.0`, extend CI (matrix by language), run the full pytest suite + smoke builds, and draft release notes/changelog.

## Risks / notes
- Multiple languages multiply build time; enforce incremental builds and allow per-language selection in CI to keep runtime acceptable.
- Credential sourcing must never leak secrets into logs; validate failure modes and add unit tests for missing/invalid credentials.
- Publisher refactor touches path handling heavily—plan for regression tests (Git repo harness + PDF smoke) before tagging 2.0.0.
- README/docs now reference per-language paths; ensure automation keeps `de/` authoritative so future languages inherit correct defaults.
