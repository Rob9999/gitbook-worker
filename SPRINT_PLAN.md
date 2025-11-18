---
version: 1.0.3
date: 2025-05-30
history: Added CI guardrails (coverage, mypy) and started handbook migration.
---

# Sprint: Package relocation & docs refresh

## Goals
- Finalise root-level Python package layout (`gitbook_worker/`).
- Update CI workflows to consume the packaged CLI.
- Refresh documentation for the new structure and entrypoints.

## Work items
1. ✅ Move package code to `gitbook_worker/` and expose console script `gitbook-worker`.
2. ✅ Relocate tests to repository root and update imports to `gitbook_worker.*`.
3. ✅ Refresh README files and agent guidance for the new layout.
4. ✅ Add coverage gating and type-checking to CI.
5. ✅ Trim and migrate legacy docs from `.github/gitbook_worker/docs/` into a
   concise root-level handbook.

## Risks / notes
- Legacy documentation still references the old `.github/gitbook_worker` paths;
  cross-links will be updated incrementally.
- Docker images now build from `gitbook_worker/tools/docker/Dockerfile.dynamic`.
