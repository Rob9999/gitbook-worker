---
version: 1.1.0
date: 2026-05-09
history:
  - "1.1.0: 2026-05-09 — Publish-Scope, PDF-Zielkorridore und Drift-Regeln als implementierte v2.9.0-Signale dokumentiert."
  - "1.0.0: 2026-05-09 — Editorial quality profile for v2.9.0 Qualitaetskompass documented."
---

# editorial quality profile

Optionale YAML-Konfiguration fuer die CLIs
`gitbook_worker.tools.quality.editorial_metrics` und
`gitbook_worker.tools.quality.editorial_acceptance`.

Die Datei wird per `--profile-config <path>` uebergeben und enthaelt ein
`profiles`-Mapping. Ohne Datei nutzt das Tool eingebaute Profile wie
`local-preview`, `release-candidate`, `publish-final`, `docs-only` und
`multilingual-release-candidate`.

## Schema-Version

Empfohlen: `version: 1.1.0`. Die Version ist aktuell dokumentiert, aber noch
nicht hart validiert.

## Beispiel

```yaml
version: 1.1.0
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
      required_fonts:
        - DejaVuSerif
        - DejaVuSans
        - DejaVuSansMono
        - TwemojiMozilla
        - ProjectCJK-Regular
    documentation:
      fail_on_stale_worker_version: true
      fail_on_stale_page_count: true
```

## Status

✅ Implementiert:

- Profil-Laden ueber `profiles.<name>`.
- generische Source-/Target-Locale-Regeln.
- Pflichtfelder je Rolle.
- verbotene Frontmatter-Keys.
- Target-Statuswerte.
- lange Markdown-Tokens.
- PDF-Wenigzeiler- und Leerseiten-Metriken.
- PDF-TOC/Outline-Metriken.
- PDF-Seitenzahl-Zielkorridore ueber `pdf_targets`.
- erwartete eingebettete PDF-Fontnamen.
- `documentation.fail_on_stale_worker_version`.
- `documentation.fail_on_stale_page_count`.
- Publish-Scope-Signale aus `content.yaml` und `publish.yml`.

🚧 WIP:

- Baseline-Vergleich und akzeptierte Restrisiken mit Ablaufdatum.
- Tiefe BBox-/Overflow-Auswertung fuer konkrete PDF-Layoutbefunde.