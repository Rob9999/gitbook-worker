---
version: 1.0.5
date: 2025-06-01
history: Completed sprint items (validation CLI, PDF stability, Docker docs, analytics, handbook refresh).
---

# Sprint: Publishing stability & documentation automation

## Goals
- Harden PDF and HTML outputs to be reproducible across CI runners.
- Add lightweight runtime checks for the orchestrator CLI and publish manifest.
- Automate handbook updates to reflect the package-first layout.

## Work items
1. ☑ Stabilise font embedding and image handling in the PDF builder; add a smoke test in `tests/`.
2. ☑ Introduce a fast CLI validation command (e.g., `gitbook-worker validate --manifest publish.yml`) wired into CI.
3. ☑ Extend the handbook with a contributor quickstart and troubleshooting section aligned with `gitbook_worker/` entrypoints.
4. ☑ Document Docker usage paths (dynamic vs. static images) and ensure build scripts reference current Dockerfiles.
5. ☑ Capture failure analytics in logs for orchestrated jobs to simplify debugging.

## Risks / notes
- PDF reproducibility depends on system fonts; ensure the Docker image pins font packages or bundles required assets.
- CLI validation should remain fast (<10s) to keep CI loops tight; avoid contacting external services.
- Handbook automation must not diverge from README; prefer shared snippets or scripts to sync sections.
