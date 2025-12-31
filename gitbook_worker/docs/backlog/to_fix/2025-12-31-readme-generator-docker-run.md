---
version: 0.1.0
date: 2025-12-31
history:
  - version: 0.1.0
    date: 2025-12-31
    changes: Initial bug capture for README generator creating files in code area during docker-based orchestrator run.
---

# README generator creates README.md in code area (docker orchestrator)

## Summary
During a docker-based orchestrator run (profile `default`), the README generator step created a `README.md` in the code area instead of limiting itself to content roots. This pollutes the source tree and can overwrite or add unintended files outside the content folders.

## Impact
- Unwanted `README.md` files appear in the code area during CI/Orchestrator runs.
- Risk of overwriting manually maintained README files or introducing dirty git state.

## Steps to Reproduce
1. Run the orchestrator in docker mode, e.g.:
   - `python -m gitbook_worker.tools.workflow_orchestrator run --root C:/gitbook-worker --content-config content.yaml --lang de --profile default`
2. Observe that the README generator step writes `README.md` outside the intended content root (code area).

## Expected Behavior
- README generation should target only the content roots/books (e.g., `de/` or `en/` content trees) and never create or modify README files in the code area (e.g., `gitbook_worker/`, tooling directories, or repo root unless explicitly intended).

## Actual Behavior
- A `README.md` is created in the code area during the docker-based orchestrator run.

## Notes / Leads
- The `ensure_readme` step may be running with an overly broad base path when invoked in docker profile.
- Check orchestrator profile `default` and README generation logic for scoping to language/content root only.
- Add a guard to skip code/tooling directories when generating READMEs.
