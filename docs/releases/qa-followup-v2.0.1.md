---
version: 2.0.1
date: 2025-12-29
history:
  - date: 2025-12-29
    change: Documented QA feedback resolution for v2.0.1
---

# QA Follow-up for v2.0.1

**Source report**: [qa-customer-feedback/qa-report-gitbook-worker-2.0.0.md](qa-customer-feedback/qa-report-gitbook-worker-2.0.0.md)

## Issues reported
- Orchestrator resolved repo root to site-packages and missed `tools/`/`pipeline.py` → steps skipped.
- Tools should be package data and referenced package-relatively; fail-fast instead of silent skips.
- Need safe-mode/dry-run before destructive GitBook renames.
- Pipeline aborted on missing `project.license` without early validation.

## Actions taken in v2.0.1
- `--root` is now authoritative; auto-detect only when omitted. Tools fallback prefers repo `gitbook_worker/tools`, then `.github/gitbook_worker/tools`, then installed package tools.
- Converter/publisher/AI-reference steps fail fast if scripts are missing; pipeline invoked with dry-run when orchestrator is in `--dry-run`.
- Manifest preflight enforces `project.license` before any destructive step.
- Release notes updated with pip-only usage and dry-run guidance.

## Status
- Addressed in release v2.0.1 (see [docs/releases/v2.0.1.md](docs/releases/v2.0.1.md)).
- Remaining risk: Font cache-dependent pandoc tests are skipped unless LuaTeX cache is populated; see `gitbook_worker/docs/attentions/lua-font-cache.md`.
