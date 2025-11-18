# Agent Directives for GitBook Worker (v1.0.2)

1. **Package-first layout**: The Python package now lives at repository root
   (`gitbook_worker/`). Prefer imports via `gitbook_worker.*`; the `tools/`
   shim is for backwards compatibility only.
2. **Documentation location**: New development docs belong next to the package
   (e.g. `README.md`, `SPRINT_PLAN.md`). Keep the historical archive under
   `.github/gitbook_worker/docs/` intact for past references.
3. **Front matter & versioning**: Planning or engineering documents must carry
   YAML front matter with at least `version`, `date`, and a short `history` note.
4. **Testing**: Run `pytest` from repository root for new features or fixes.
5. **Logging**: Retain informative logging (info/warn/error) in new automation
   code to aid traceability.
