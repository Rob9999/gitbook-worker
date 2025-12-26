---
version: 1.0.0
date: 2025-12-26
history:
  - v1.0.0: Initial note on LuaTeX font cache guard for fallbacks.
---

# LuaTeX font cache guard

When fallback fonts are configured in `fonts.yml` but not present in the LuaTeX cache, the PDF build now aborts early with a clear error instead of emitting a broken preamble that later fails in LaTeX. This typically shows up when fonts are only stored on disk (or freshly added) but `luaotfload` has not indexed them.

## Recovery steps
- Ensure the configured fallback fonts are actually installed (per `gitbook_worker/defaults/fonts.yml`). The dynamic Docker build already installs everything listed there.
- Refresh the LuaTeX cache after adding or updating fonts:
  - `luaotfload-tool --update --force`
- Re-run the publisher once the cache is fresh. If a font is intentionally missing, drop it from `fonts.yml` instead of relying on system defaults.

## Notes
- The guard is triggered before LaTeX runs, so users get actionable feedback instead of a runaway argument in the generated `.tex` file.
- You can still disable Lua fallbacks entirely with `ERDA_ENABLE_LUA_FALLBACK=0`, but doing so removes missing-glyph detection.
