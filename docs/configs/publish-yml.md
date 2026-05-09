---
version: 1.2.0
date: 2026-05-09
config_schema_version: "0.1.3"
history:
  - "1.2.0: 2026-05-09 — pdf_options.table_paper_strategy dokumentiert"
  - "1.1.0: 2026-05-07 — pdf_options.code_block_wrap dokumentiert"
  - "1.0.0: 2026-02-08 — Initial documentation"
---

# publish.yml

## Zweck

Steuerdatei pro Sprachbaum. Definiert Build-Profile, Projekt-Metadaten,
Publish-Entries (was → wohin), Dokumenttyp-Konfiguration, PDF-Optionen und
Assets. Der Orchestrator und der Publisher lesen diese Datei.

## Ort

```
<lang>/publish.yml       (z. B. de/publish.yml, en/publish.yml)
```

## Schema-Version

Aktuell: **0.1.3** — Feld `version` (Top-Level). Hard-Exit bei Fehler (Exit-Code 3).

## Schlüssel-Referenz

### Top-Level

| Schlüssel | Typ | Pflicht | Default | Status | Beschreibung |
|-----------|-----|---------|---------|--------|--------------|
| `version` | string | ✓ | – | ✅ | SemVer-Schema-Version |
| `profiles` | object | ✓ | – | ✅ | Benannte Build-Profile |
| `project` | object | ✓ | – | ✅ | Projekt-Metadaten |
| `publish` | array | ✓ | – | ✅ | Liste von Publish-Entries |
| `frontmatter` | object | – | `null` | ✅ | Override für `defaults/frontmatter.yml` |
| `readme` | object | – | `null` | ✅ | Override für `defaults/readme.yml` |
| `meta` | object | – | `null` | 📝 | Nur für GitHub Actions (`publish_on`, `artifacts`) |

### profiles.\<name\>

| Schlüssel | Typ | Pflicht | Default | Status | Beschreibung |
|-----------|-----|---------|---------|--------|--------------|
| `description` | string | – | `""` | ✅ | Geloggt beim Profilstart |
| `steps` | array | ✓ | – | ✅ | Pipeline-Schritte in Reihenfolge |
| `docker.use_registry` | bool | – | `false` | 📝 | Für CI-Workflows (nicht Python-seitig gelesen) |
| `docker.image` | string | – | `null` | 📝 | Für CI-Workflows |
| `docker.cache` | bool | – | `false` | 📝 | Für CI-Workflows |
| `env` | object | – | `{}` | ✅ | Umgebungsvariablen für Subprozesse |

### project.\*

| Schlüssel | Typ | Pflicht | Default | Status | Beschreibung |
|-----------|-----|---------|---------|--------|--------------|
| `name` | string | – | book.json:title | ✅ | Projektname (Titelseite) |
| `authors` | array | – | book.json:author | ✅ | Autorenliste |
| `license` | string | ✓ | – | ✅ | **Mandatory** – Pipeline bricht ab wenn fehlend |
| `date` | string | – | heute | ✅ | ISO-Datum (YYYY-MM-DD) |
| `version` | string | – | book.json:version | ✅ | Projektversion (Titelseite) |
| `attribution_policy` | string | – | `"warn"` | ✅ | `"fail"` oder `"warn"` bei fehlender Attribution |

### publish[] Entry

| Schlüssel | Typ | Pflicht | Default | Status | Beschreibung |
|-----------|-----|---------|---------|--------|--------------|
| `path` | string | ✓ | – | ✅ | Quellverzeichnis (relativ zum Sprachbaum) |
| `out_format` | string | – | `"pdf"` | ✅ | Nur `pdf` unterstützt |
| `out_dir` | string | – | `"./publish"` | ✅ | Ausgabeverzeichnis |
| `out` | string | ✓ | – | ✅ | Dateiname der Ausgabe |
| `build` | bool | – | `false` | ✅ | Gating-Flag: nur bei `true` wird gebaut |
| `source_type` | string | – | `"folder"` | ✅ | `folder` oder `file` |
| `source_format` | string | – | `"markdown"` | ✅ | Nominell, nur Markdown unterstützt |
| `use_summary` | bool | – | `true` | ✅ | SUMMARY.md für Kapitelreihenfolge nutzen |
| `use_book_json` | bool | – | `true` | ✅ | book.json für Metadaten laden |
| `keep_combined` | bool | – | `false` | ✅ | Kombiniertes .md neben .pdf speichern |
| `summary_mode` | string | – | `"gitbook"` | ✅ | Stil der SUMMARY-Generierung |
| `summary_manifest` | string | – | `null` | ✅ | Optionaler Pfad zu Ordering-Manifest |
| `summary_appendices_last` | bool | – | `false` | ✅ | Anhänge ans Ende sortieren |
| `use_document_types` | bool | – | `false` | ✅ | Doc-Type-basierte SUMMARY-Generierung |
| `document_type_config` | object | – | `{}` | ✅ | Konfiguration für Doc-Type-System |
| `reset_build_flag` | bool | – | `false` | ✅ | `build` nach erfolgreichem Lauf zurücksetzen |
| `generate_attribution` | bool | – | `false` | ✅ | Attribution-Dateien erzeugen |
| `pdf_options` | object | – | `{}` | ✅ | PDF-spezifische Optionen |
| `assets` | array | – | `[]` | ✅ | Asset-Pfade mit `path`, `type`, `copy_to_output` |

### document_type_config

| Schlüssel | Typ | Default | Status | Beschreibung |
|-----------|-----|---------|--------|--------------|
| `section_order` | array | `[]` | ✅ | Reihenfolge der Abschnitte in SUMMARY |
| `section_titles` | object | `{}` | ✅ | Überschriften pro Abschnitt |
| `section_titles_by_locale` | object | `{}` | ✅ | Locale-spezifische Überschriften |
| `title_to_doc_type` | object | `{}` | ✅ | Mapping Titel → Doc-Type |
| `title_to_doc_type_by_locale` | object | `{}` | ✅ | Locale-spezifisches Mapping |
| `show_in_summary` | object | `{}` | ✅ | Per Doc-Type: in SUMMARY anzeigen? |
| `auto_number_chapters` | bool | `false` | ✅ | „Kapitel N –" Präfix |
| `auto_number_appendices` | bool | `false` | ✅ | „Anhang A –" Präfix |
| `auto_number_parts` | bool | `false` | ✅ | „Teil N" Gruppierung |
| `chapter_appendix_indent` | bool | `false` | ✅ | Einrückung in SUMMARY |
| `chapter_appendix_prefix` | string | `""` | ✅ | Template-String `{chapter}.{id}` |
| `default_order_weight` | int | `100` | ✅ | Sortier-Fallback |

### pdf_options

| Schlüssel | Typ | Default | Status | Beschreibung |
|-----------|-----|---------|--------|--------------|
| `emoji_color` | bool | `true` | ✅ | Farb-Emojis aktivieren |
| `emoji_bxcoloremoji` | bool | `false` | ✅ | bxcoloremoji-Paket (experimentell) |
| `main_font` | string | `"DejaVu Serif"` | ✅ | → Pandoc `-V mainfont` |
| `sans_font` | string | `"DejaVu Sans"` | ✅ | → Pandoc `-V sansfont` |
| `mono_font` | string | `"DejaVu Sans Mono"` | ✅ | → Pandoc `-V monofont` |
| `mainfont_fallback` | string | `""` | ✅ | LuaTeX Fallback-Chain (`;`-getrennt) |
| `abort_if_missing_glyph` | bool | `true` | ✅ | Bei fehlenden Glyphen abbrechen |
| `code_block_wrap` | bool | `true` | ✅ | Lange Code-Fence-Zeilen im PDF umbrechen (`fvextra`) |
| `table_paper_strategy` | object | `{}` | ✅ | Redaktionelle Best-Fit-Papierwahl fuer Markdown-Pipe-Tabellen |

#### pdf_options.table_paper_strategy

| Schlüssel | Typ | Default | Status | Beschreibung |
|-----------|-----|---------|--------|--------------|
| `enabled` | bool | `true` | ✅ | Strategie aktivieren; bei `false` bleibt nur die Spaltenheuristik |
| `mode` | string | `"editorial"` | ✅ | Strategieprofil; aktuell redaktionelles Best-Fit-Modell |
| `max_cell_lines` | int | `5` | ✅ | Maximal akzeptierte geschaetzte Zeilen pro Zelle |
| `max_header_lines` | int | `3` | ✅ | Maximal akzeptierte geschaetzte Zeilen fuer Tabellenkoepfe |
| `preferred_max_avg_row_lines` | float | `2.8` | ✅ | Zielwert fuer durchschnittliche Tabellenzeilenhoehe |
| `min_readable_column_width_mm` | float | `14` | ✅ | Untergrenze fuer lesbare Spaltenbreiten |
| `unbreakable_overflow_tolerance_mm` | float | `2` | ✅ | Toleranz fuer nicht sinnvoll trennbare Token/Script-Runs |
| `oversize_policy` | string | `"preserve-column-heuristic"` | ✅ | Fallback bei Tabellen breiter als alle Kandidaten |
| `report` | string | `null` | ✅ | `jsonl` erzeugt einen maschinenlesbaren Tabellenlayout-Report |
| `report_path` | string | `null` | ✅ | Optionaler expliziter Pfad fuer JSONL-Report |
| `candidates` | array | ISO A4-A1 hoch/quer | ✅ | Standard- oder Custom-Paper-Kandidaten in Auswahlreihenfolge |

## Beispiel (Minimalversion)

```yaml
version: 0.1.3
profiles:
  local:
    description: Lokale Ausführung
    steps: [converter, publisher]
project:
  name: Mein Buch
  authors: [Max Mustermann]
  license: CC BY-SA 4.0
publish:
  - path: ./
    out: mein-buch.pdf
    build: true
```

## Versionshistorie

| Version | Datum | Änderung |
|---------|-------|----------|
| 0.1.0 | 2025-12-05 | Initiales Schema |
| 0.1.1 | 2026-01-08 | `generate_attribution`, `pdf_options.abort_if_missing_glyph`, `assets` ergänzt |
| 0.1.2 | 2026-05-07 | `pdf_options.code_block_wrap` ergänzt |
| 0.1.3 | 2026-05-09 | `pdf_options.table_paper_strategy` ergänzt |

## Verwandte Dokumente

- [docs/Configure-Doc-Types.md](../Configure-Doc-Types.md) — Doc-Type-System im Detail
- [docs/HANDBOOK.md](../HANDBOOK.md) — Gesamtreferenz
