---
version: 0.1.0
date: 2025-12-26
history:
  - v0.1.0 Initial blocker list (user + AI)
---

# Release blockers for v2.0.0

## Open items

1) CJK glyphs missing in PDFs. Expected coverage from ERDA-CC-BY-CJK fonts, but CJK codepoints render blank. Next steps: confirm fonts installed (fonts.yml, fonts-storage), inspect luaotfload fallback stack in generated TeX, and render a minimal doc with known CJK codepoints to locate where the fallback fails.

2) Package not pip-installable from external projects. Next steps: `python -m build`, install wheel in a clean venv, verify console entry points/resources, and fix packaging metadata or data inclusion as needed.

3) Missing-glyph detector instability. The Lua detector previously triggered a hyperref runaway; it is now opt-in via ERDA_ENABLE_MISSING_GLYPH_DETECTOR and deferred to AtBeginDocument. Next steps: validate a build with the detector enabled to ensure stability, or keep it off by default for the release.
