---
version: 0.1.0
date: 2025-12-05
history:
  - version: 0.1.0
    date: 2025-12-05
    changes: Initial capture of LaTeX warnings and font regressions discovered before release 2.0.0.
---

# LaTeX Metadata & Font Regressions (Dec 2025)

## Context
- Release: 2.0.0 cut on 2025-12-05.
- Environment: Windows 11 + repo-managed venv (`.venv`), orchestrator invoked via `gitbook_worker.tools.workflow_orchestrator run --root c:\gitbook-worker --content-config content.yaml --lang de --profile local` and Docker profile (`gitbook_worker.tools.docker.run_docker orchestrator --profile default --use-dynamic --rebuild --no-cache`).
- Goal: Record non-blocking warnings and pytest failures so that fixes do not jeopardize the currently successful orchestration pipeline.

## Observations
1. **LaTeX undefined references**
   - Warnings such as `Hyper reference 'md-chapters-chapter-02' undefined` appear during PDF generation.
   - Cause: Pandoc/LaTeX builds combined markdown fragments with entries declared after their first reference; no fatal impact but produces noisy logs.

2. **Missing glyph warnings**
   - Numerous `Missing character: There is no ... in font "DejaVu Serif"` entries for CJK, Indic, Ethiopic text.
   - Cause: `fonts.yml` still sets DejaVu as the fallback for general text while ERDA CC-BY CJK (and other scripts) is only referenced via manual overrides.

3. **Pytest failures (emoji + font stack)**
   - `gitbook_worker/tests/test_documents_publishing.py` and `test_pdf_integration.py` fail because `latex-emoji.lua` aborts on `header-includes` metadata.
   - `test_publisher.py::test_prepare_publishing_uses_manifest_fonts` exits with code 43 due to Twemoji download URL (0.7.0) returning HTTP 404.
   - `test_emoji_color_regression.py` still expects Twitter Color Emoji whereas runtime uses Twemoji Mozilla.
   - `test_emoji_color_regression.py::test_emoji_color_produces_harfbuzz_in_combined_markdown` fails to locate the `*-combined.md` artifact.
   - Secondary/environmental failures: `test_csv_converter.py::test_convert_assets` (missing Tcl/Tk on Windows CI), Docker integration test (Docker daemon unavailable).

## Impact Assessment
- Current orchestrator builds (local + Docker) succeed despite warnings, so release 2.0.0 is not blocked.
- Publishing-related pytest suites cannot be trusted until the Lua filter + font sync regressions are resolved; this blocks CI confidence for future changes.
- Font download issue prevents air-gapped or offline environments from syncing Twemoji automatically.

## Proposed Remediation
1. **LaTeX undefined references**
   - Investigate whether the combined markdown should append `header-includes` blocks after the main sections or force Pandoc to perform an extra cross-reference pass (`--lua-filter` hook or `--metadata link-citations=true`).
   - Add regression test that runs `publisher.build_pdf` on the German manifest with `--keep-combined` and asserts that `md-*` anchors resolve.

2. **Missing glyphs / font fallback**
   - Promote ERDA CC-BY CJK (and other script fonts) into the default serif/sans fallback chain via `fonts.yml`.
   - Update `gitbook_worker/tools/publishing/publisher.py` to include the new fallback when constructing metadata, ensuring glyph coverage without manual overrides.

3. **Lua filter metadata handling**
   - Update `latex-emoji.lua` to gracefully skip non-string metavariables (e.g., `header-includes` arrays) when injecting emoji metadata.
   - Add a unit test reproducing the failing fixture from `test_documents_publishing.py` to prevent regressions.

4. **Font sync / Twemoji URL**
   - Bundle Twemoji Mozilla 0.7.0 (or the approved 15.1.0) inside `fonts-storage/` and point `fonts.yml` to a repo-relative path, or refresh the download URL to a working release asset.
   - Extend `smart_font_stack` to fall back on cached assets before attempting remote download.

5. **Emoji regression tests**
   - Align expectations with Twemoji (update assertions, ensure Harfbuzz metadata still validated).
   - Ensure `keep_combined=True` path writes the `*-combined.md` file when `publish_dir` differs from `path.parent`.

6. **Environment-specific tests**
   - Document the requirement for `tk` and Docker daemon; consider adding `pytest.skip` guards when dependencies are missing.

## Next Actions
- Triage items 3 and 4 first (they unblock the majority of failing tests).
- After Lua filter and font sync fixes are merged, re-run full pytest suite and orchestrator pipelines to ensure no regression.
- Track progress in this document (increment `history`) until all sections are resolved.
