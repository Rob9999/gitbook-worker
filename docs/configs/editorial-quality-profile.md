---
version: 1.5.0
date: 2026-05-11
history:
  - "1.5.0: 2026-05-11 — Long-Token-, Review-Marker- und Duplicate-Heading-Signale redaktionell fokussiert."
  - "1.4.0: 2026-05-11 — Textlayer-Replacement-Signale als Warnung statt Font-Fail dokumentiert."
  - "1.3.0: 2026-05-09 — Pflicht-/Soll-Schnitt: erwartete PDF-Seiten, Overflow-Schwellen, Release-Doku-Scan und Built-in-Profile local/release/customer-handover dokumentiert."
  - "1.2.0: 2026-05-09 — Baseline und Restrisiken in eigene Acceptance-Eingaben ausgelagert."
  - "1.1.0: 2026-05-09 — Publish-Scope, PDF-Zielkorridore und Drift-Regeln als implementierte v2.9.0-Signale dokumentiert."
  - "1.0.0: 2026-05-09 — Editorial quality profile for v2.9.0 Qualitaetskompass documented."
---

# editorial quality profile

Optionale YAML-Konfiguration fuer die CLIs
`gitbook_worker.tools.quality.editorial_metrics` und
`gitbook_worker.tools.quality.editorial_acceptance`.

Die Datei wird per `--profile-config <path>` uebergeben und enthaelt ein
`profiles`-Mapping. Ohne Datei nutzt das Tool eingebaute Profile wie
`local`, `release`, `customer-handover`, `local-preview`,
`release-candidate`, `publish-final`, `docs-only` und
`multilingual-release-candidate`.

## Schema-Version

Empfohlen: `version: 1.3.0`. Die Version ist aktuell dokumentiert, aber noch
nicht hart validiert.

## Beispiel

```yaml
version: 1.3.0
profiles:
  multilingual-release-candidate:
    network: false
    markdown:
      locale_field: content_lang
      identity_key: content_id
      source_link_field: source
      source_locale: ja
      target_locales:
        - pl
        - hr
        - no
      forbidden_frontmatter_keys:
        - lang
        - language
        - lang-version
      required_frontmatter_by_role:
        source:
          - content_id
          - content_lang
        target:
          - content_id
          - content_lang
          - source
          - status
      allowed_translation_status:
        - draft
        - in-review
        - approved
    pdf:
      low_text_page_threshold: 15
      very_low_text_page_threshold: 5
      pdf_targets:
        publish/sample.pdf:
          target_pages_min: 120
          target_pages_max: 140
          warn_pages_max: 150
      expected_pages:
        publish/sample.pdf:
          - page: 1
            label: cover sample
            min_text_lines: 3
            must_contain: Sample
      overflow_warn_pt: 0.1
      overflow_fail_pt: 12.0
      overflow_token_warn_chars: 96
      required_fonts:
        - DejaVuSerif
        - DejaVuSans
        - DejaVuSansMono
        - TwemojiMozilla
        - ProjectCJK-Regular
    documentation:
      fail_on_stale_worker_version: true
      fail_on_stale_page_count: true
      scan_release_docs: true
      release_doc_dirs:
        - docs/releases
        - gitbook_worker/docs/releases
```

## Status

✅ Implementiert:

- Profil-Laden ueber `profiles.<name>`.
- generische Source-/Target-Locale-Regeln.
- Pflichtfelder je Rolle.
- verbotene Frontmatter-Keys.
- Target-Statuswerte.
- lange Markdown-Tokens ohne Frontmatter- und URL-/Markdown-Link-Rauschen.
- doppelte Markdown-Titel als nahe Wiederholungen im selben Dokument (`duplicate_heading_near_window`).
- explizite Review-Marker wie `TODO`, `FIXME`, `XXX`, `REVIEW:`, `[REVIEW]` oder `<!-- REVIEW`; normale Fachbegriffe wie "peer review" sind kein Marker.
- AI-Referenzkandidaten aus `ai_references` als sichtbare Signale.
- Frontmatter-Syntaxsignale aus dem bestehenden Frontmatter-Checker.
- PDF-Wenigzeiler- und Leerseiten-Metriken.
- PDF-Textlayer-Replacement-Signale als Accessibility-/Copy-Paste-Warnung.
- PDF-TOC/Outline-Metriken.
- PDF-Seitenzahl-Zielkorridore ueber `pdf_targets`.
- erwartete PDF-Sample-Seiten ueber `expected_pages`.
- BBox-/Overflow-nahe Textsignale mit `overflow_*`-Schwellen.
- CJK/Hangul/Kana-Stichproben im extrahierten PDF-Text.
- erwartete eingebettete PDF-Fontnamen.
- `documentation.fail_on_stale_worker_version`.
- `documentation.fail_on_stale_page_count`.
- Release-Dokument-Scan ueber `documentation.scan_release_docs` und
  `documentation.release_doc_dirs`.
- Publish-Scope-Signale aus `content.yaml` und `publish.yml`.