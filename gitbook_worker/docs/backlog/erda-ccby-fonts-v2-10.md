---
title: ERDA CC-BY fonts v2.10.0 coverage and rename plan
version: 1.1.0
date: 2026-05-10
status: planned
target_release: "v2.10.0"
history:
  - version: 1.1.0
    date: 2026-05-10
    description: Adds related-backlog audit for the v2.10.0 font release scope.
  - version: 1.0.0
    date: 2026-05-10
    description: Documents the CC-BY-only/no-Noto policy, ERDA Emoji decision, per-script baseline font plan and erda-ccby-fonts rename.
---

# ERDA CC-BY Fonts v2.10.0 Coverage And Rename Plan

## Decisions

1. Apart from the already configured DejaVu family, all project fonts and emoji
   fonts must be CC BY 4.0 licensed.
2. Noto fonts are forbidden in this repository. This includes runtime fallback,
   test fixtures, Docker images, examples and documentation recommendations.
3. If Twemoji Mozilla does not cover customer-required emojis, the remediation
   is an ERDA Emoji font under CC BY 4.0.
4. v2.10.0 extends the ERDA-generated font family with per-script baseline
   coverage up to 5000 glyphs per script where the Unicode/script scope makes
   that meaningful. Scripts with fewer assigned codepoints use complete assigned
   block coverage instead of inflated targets.
5. The historical `.github/fonts/erda-ccby-cjk/` name should be renamed to
   `.github/fonts/erda-ccby-fonts/`, because the family now covers CJK, Indic,
   Ethiopic, planned emoji and additional script fonts.

## Related Backlogs For v2.10.0

The v2.10.0 font slice should pull in adjacent backlog work where it directly
protects the new font family. It should not become a general PDF layout release.

| Backlog | Decision | v2.10.0 slice |
|---|---|---|
| [erda-ccby-cjk-glyph-coverage.md](erda-ccby-cjk-glyph-coverage.md) | Include | Supersede the historical CJK-only framing with ERDA CC-BY Fonts; carry forward the staged coverage/statistics gate. |
| [cjk-linebreaking-and-font-metrics.md](cjk-linebreaking-and-font-metrics.md) | Include | Add CJK/sample regression evidence for embedded ERDA fonts and keep the 5000-glyph ceiling policy connected to linebreaking/metrics risk. |
| [font-storage-dynamic-generation.md](font-storage-dynamic-generation.md) | Include | New ERDA Emoji and script fonts make `fonts.yml`-driven storage generation a release blocker for avoiding drift. |
| [publish-yml-comprehensive-testing.md](publish-yml-comprehensive-testing.md) | Include | Extend config-aware PDF validation for ERDA Emoji and every configured ERDA script font; no hardcoded family assumptions. |
| [editorial-quality-tools.md](editorial-quality-tools.md) | Include partial | Refine `pdf.text.replacement_glyph` diagnostics with page/context/extractor split so the release proves real improvement. |
| [config-completeness-and-documentation.md](config-completeness-and-documentation.md) | Include partial | Update `fonts.yml`, `publish.yml` samples and config docs for every new validated font key/path. |
| [customer-v2-4-2-pdf-feedback.md](customer-v2-4-2-pdf-feedback.md) | Include as evidence | Reuse CJK embedding/extractability and Windows font-stub lessons as regression acceptance criteria. |
| [windows-font-stub-hardening.md](windows-font-stub-hardening.md) | Regression only | Already implemented; keep smoke coverage so new fonts also prefer managed validated files over stale user stubs. |
| [license-policy-management.md](license-policy-management.md) | Include small slice | Add a font-license policy validator or release check for CC BY 4.0-only project fonts and explicit no-Noto enforcement. |
| [data-sovereignty-gate.md](data-sovereignty-gate.md) | Guardrail, not core | Reuse DS-004 thinking to ensure no runtime public font/CDN dependency enters the PDF pipeline. |

Explicit non-scope for v2.10.0:

- [pdf-layout-overflow-hardening.md](pdf-layout-overflow-hardening.md) remains a
  separate layout release unless new font metrics create a direct regression.
- [table-paper-selection-strategy-hardening.md](table-paper-selection-strategy-hardening.md)
  remains separate; only CJK/emoji width regression fixtures may be reused.
- [pdf-block-headings-for-h4.md](pdf-block-headings-for-h4.md) remains separate;
  it is customer-visible PDF hardening, but not part of the font-family cut.

## ERDA Emoji Scope

ERDA Emoji is the urgent customer-facing fix for missing emoji coverage that
Twemoji Mozilla 0.7.0 cannot cover reliably. It must not be configured in
`gitbook_worker/defaults/fonts.yml` until a real TTF/OTF artifact exists and has
passed local PDF embedding validation.

Minimum implementation criteria:

- CC BY 4.0 license metadata in the font name table and `fonts.yml`.
- Source artwork or generated glyph data with CC BY 4.0 provenance.
- Coverage list derived from failing customer/release emoji samples.
- LuaLaTeX/Pandoc embedding proof in DE and EN PDFs.
- Attribution output in `ATTRIBUTION.md`.
- `pdffonts` evidence that the font is embedded and subsetted.
- Editorial-quality rerun proving the emoji-related replacement-glyph cluster is
  reduced or eliminated.

## Per-Script Baseline Fonts

v2.10.0 should add ERDA-generated baseline fonts for the scripts that currently
produce the strongest replacement-glyph signals in the release PDFs. Initial
priority is based on the v2.9.0 fail disclosure and the 100-language samples:

| Priority | Script area | Reason |
|---|---|---|
| P1 | Emoji | Customer-visible missing emoji cases; high replacement-glyph density in emoji coverage pages. |
| P1 | Bengali | Bangladesh/Bengali samples show replacement-glyph signals in PDF text extraction. |
| P1 | Arabic/Persian/RTL baseline | RTL samples contribute replacement signals and need explicit ERDA fallback coverage. |
| P2 | Telugu, Kannada, Malayalam, Tamil, Sinhala | South-Asian samples are present in DE/EN language coverage and are not fully covered by current ERDA Indic. |
| P2 | Thai/Lao | Southeast-Asian samples appear in the 100-language coverage set. |

Each script font must have a named scope, a glyph target, a generated coverage
report and a font-stats gate. The phrase "up to 5000 glyphs" is a ceiling, not a
false claim: small Unicode blocks are considered complete when all assigned
codepoints in the declared scope are covered.

## Rename Plan

Recommended migration path:

1. Create `.github/fonts/erda-ccby-fonts/` as the new home for the generator,
   datasets, docs, tests and `true-type/` outputs.
2. Update `gitbook_worker/defaults/fonts.yml` paths from
   `.github/fonts/erda-ccby-cjk/true-type/...` to
   `.github/fonts/erda-ccby-fonts/true-type/...` in the same release as the
   directory move.
3. Keep a small `.github/fonts/erda-ccby-cjk/README.md` compatibility pointer
   for one minor release so older notes and local scripts fail with a clear
   message instead of disappearing silently.
4. Update release docs, architecture docs and backlog references.
5. Remove the compatibility pointer no earlier than v3.0.0.

The rename should be done as a separate, mechanical commit before the v2.10.0
font-generation changes, so reviewers can distinguish path movement from glyph
coverage behavior.

## Definition Of Done

- `fonts.yml` contains only existing, validated font artifacts.
- No Noto references are introduced except in this policy as a forbidden option.
- ERDA Emoji is embedded in DE/EN PDFs when selected.
- Every new font has CC BY 4.0 attribution and a documented source/provenance.
- `font_cli.py stats --fail-on-targets` covers every generated ERDA font.
- Editorial quality reports show either resolved replacement-glyph failures or
  page-level residual findings with explicit acceptance text.

## Review Summary

The decision is coherent with the existing license-compliance architecture:
font coverage expands through ERDA-owned CC BY 4.0 assets, not through external
system fallback fonts. The main risk is scope growth; therefore ERDA Emoji and
the directory rename should be isolated before adding multiple script families.
