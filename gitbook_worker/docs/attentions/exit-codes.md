---
version: 1.0.0
date: 2025-12-26
history:
  - 2025-12-26: initial draft with exit-code policy and publishing expectations
---

# Exit Codes & Healing

This note defines how CLI tools expose exit codes, messages, and remediation steps.

## What to provide
- A canonical table of all exit codes, human-readable messages, and required healing steps lives in this document.
- Every distinct exit reason must have its own exit code and a user-facing message that explains the failure plainly.
- The CLI must print this table via `--help exit-codes` (or equivalent) so users can fetch it without the docs site.
- Any error encountered during development/test that cannot be given a permanent fix must still receive a dedicated exit code and documented guidance here.

## Table shape
Document each code with at least the following columns:
- Code: stable integer (non-zero), unique per exit reason.
- Summary: one-line, human-readable message.
- Healing: concise steps to fix or mitigate; link to deeper docs if needed.
- Trigger: short condition description (e.g., missing dependency X, config parse error).
- Observability: where it surfaces (stdout/stderr/log file) and any log correlation IDs.

## Maintenance expectations
- Keep codes stable once released; only deprecate with a replacement noted.
- Update this file whenever a new exit reason is added or messaging changes.
- Ensure automated/help output stays in sync with this table during reviews.
