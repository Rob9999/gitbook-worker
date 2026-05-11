---
version: 1.12.0
date: 2026-05-11
history:
  - "1.12.0: 2026-05-11 — v2.9.1 fokussiert Long-Token-, Review-Marker- und Duplicate-Heading-Signale."
  - "1.11.0: 2026-05-10 — DejaVu Sans in mainfont_fallback fuer Checkbox-/Textsymbole dokumentiert"
  - "1.10.0: 2026-05-10 — Orchestrator --quality-scope fuer Sprach- und Gesamtprojekt-Dossiers dokumentiert"
  - "1.9.0: 2026-05-10 — editorial quality HTML-/Trend-/Snapshot-/SARIF-Ausgaben dokumentiert"
  - "1.8.0: 2026-05-09 — Pflicht-/Soll-Schnitt fuer editorial quality profile, CSV/Console und Orchestrator-Gate dokumentiert"
  - "1.7.0: 2026-05-09 — editorial accepted findings register fuer Restrisiken dokumentiert"
  - "1.6.0: 2026-05-09 — pdf_targets und Drift-Schalter fuer editorial quality profile als implementierte Signale markiert"
  - "1.5.0: 2026-05-09 — editorial quality acceptance profiles als v2.9.0-WIP ergaenzt"
  - "1.4.0: 2026-05-09 — pdf_options.table_paper_strategy fuer Tabellenprofi ergaenzt"
  - "1.3.3: 2026-05-08 — Release reference fuer v2.7.0 Wide-Table-Paper-Selection aktualisiert"
  - "1.3.2: 2026-05-08 — Release reference fuer v2.6.1 URL-Code-Fence-Hotfix aktualisiert"
  - "1.3.1: 2026-05-07 — Release reference fuer v2.6.0 Code-Fence-Wrapping aktualisiert"
  - "1.3.0: 2026-05-07 — pdf_options.code_block_wrap fuer PDF-Code-Fence-Wrapping ergaenzt"
  - "1.2.2: 2026-05-07 — Release reference refreshed for v2.4.3; no configuration schema changes"
  - "1.2.1: 2026-05-06 — Release reference refreshed for v2.4.2; no configuration schema changes"
  - "1.2.0: 2026-02-08 — pdf_options passthrough, author singular alias, format alias"
  - "1.1.0: 2026-02-08 — Added per-file docs references and config versioning table"
  - "1.0.0: 2026-02-08 — Initial configuration reference from code audit"
---

# Configuration Reference

Vollständige Referenz aller Konfigurationsschlüssel, die GitBook Worker kennt.
Jeder Eintrag trägt einen Implementierungsstatus gemäß der
Config-Completeness-Policy (AGENTS.md §25–30).

Hinweis fuer v2.8.0: Breite Markdown-Pipe-Tabellen nutzen standardmaessig die
redaktionelle `pdf_options.table_paper_strategy`. Sie bewertet Kandidaten nach
erwarteten Zellumbruechen, Kopfzeilen, Spaltentypen, CJK-/Script-Runs,
Token-Risiken und nutzbarer Textbreite. Ohne Konfiguration bleibt die Strategie
aktiv; `publish.yml` kann Kandidaten, Schwellen und Reports steuern.

Hinweis fuer v2.6.1: PDF-Code-Fence-Wrapping ist als `pdf_options.code_block_wrap`
konfigurierbar und standardmaessig aktiv. Die Option nutzt `fvextra`, wenn das
LaTeX-Paket in der Umgebung vorhanden ist, und bricht auch URL-artige Pandoc-
Token in Code-Fences innerhalb des Satzspiegels um.

Hinweis fuer Checkbox-/Textsymbole: Wenn `mainfont_fallback` projektseitig
ueberschrieben wird, muss `DejaVu Sans:mode=harf` in der Kette bleiben. Der
Publisher routet `☐`, `☑`, `☒`, `✓` und `✔` als Textsymbole ueber den Sans-Font;
ohne Sans-Fallback koennen PDF-Viewer fehlende Rechteckglyphen zeigen.

> **Ausführliche Per-File-Dokumentation** mit Versionshistorie:
> [docs/configs/](configs/README.md)

**Legende:**
✅ Implementiert · 🔨 Teilweise · 📝 Deklarativ (extern/CI) · 🚧 WIP · ❌ Unused

---

## 1. content.yaml (Repo-Root)

Zentrale Sprach- und Quellenkonfiguration. Wird vom Orchestrator gelesen.

| Schlüssel | Typ | Default | Status | Beschreibung |
|-----------|-----|---------|--------|--------------|
| `version` | string | – | ✅ | SemVer-Schema-Version |
| `default` | string | – | ✅ | Standard-Sprache wenn `--lang` fehlt |
| `contents[].id` | string | – | ✅ | Kurzname der Sprache (`de`, `en`, `ua`) |
| `contents[].type` | string | – | ✅ | `local` oder `git` |
| `contents[].uri` | string | – | ✅ | Pfad (lokal) oder Git-URL (remote) |
| `contents[].description` | string | `""` | ✅ | Beschreibung für CLI-Ausgabe |
| `contents[].credentialRef` | string | `null` | ✅ | Env-Variable mit SSH-Key (für `type: git`) |
| `contents[].branch` | string | `null` | ✅ | Git-Branch (für `type: git`) |

---

## 2. publish.yml (pro Sprachbaum)

Steuert Profile, Projekt-Metadaten, Publish-Entries und PDF-Optionen.

### 2.1 Top-Level

| Schlüssel | Typ | Default | Status | Beschreibung |
|-----------|-----|---------|--------|--------------|
| `version` | string | – | ✅ | SemVer – Hard-Exit bei Fehler (Exit-Code 3) |
| `profiles` | object | – | ✅ | Benannte Build-Profile |
| `project` | object | – | ✅ | Projekt-Metadaten |
| `publish` | array | – | ✅ | Liste von Publish-Entries |
| `frontmatter` | object | `null` | ✅ | Override für `defaults/frontmatter.yml` |
| `readme` | object | `null` | ✅ | Override für `defaults/readme.yml` |
| `meta` | object | `null` | 📝 | Nur für GitHub Actions (`publish_on`, `artifacts`) |

### 2.2 profiles.\<name\>

| Schlüssel | Typ | Default | Status | Beschreibung |
|-----------|-----|---------|--------|--------------|
| `description` | string | `""` | ✅ | Geloggt beim Profilstart |
| `steps` | array | – | ✅ | Orchestrator-Schritte in Reihenfolge |
| `docker.use_registry` | bool | `false` | 📝 | Für CI-Workflows, nicht von Python gelesen |
| `docker.image` | string | `null` | 📝 | Für CI-Workflows |
| `docker.cache` | bool | `false` | 📝 | Für CI-Workflows |
| `env` | object | `{}` | ✅ | Umgebungsvariablen, in Subprozesse injiziert |

### 2.3 project.\*

| Schlüssel | Typ | Default | Status | Beschreibung |
|-----------|-----|---------|--------|--------------|
| `name` | string | book.json:title | ✅ | Projektname (Titelseite) |
| `authors` | array | book.json:author | ✅ | Autorenliste |
| `author` | string | – | ✅ | Alias für `authors` (Singular → Array) |
| `license` | string | – | ✅ | **Mandatory** – Pipeline bricht ab wenn fehlend |
| `date` | string | heute | ✅ | ISO-Datum (YYYY-MM-DD) |
| `version` | string | book.json:version | ✅ | Projektversion (Titelseite) |
| `attribution_policy` | string | `"warn"` | ✅ | `"fail"` oder `"warn"` bei fehlender Attribution |

### 2.4 publish[] Entry

| Schlüssel | Typ | Default | Status | Beschreibung |
|-----------|-----|---------|--------|--------------|
| `path` | string | – | ✅ | Quellverzeichnis (relativ zum Sprachbaum) |
| `out_format` | string | `"pdf"` | ✅ | Nur `pdf` unterstützt; andere werden übersprungen |
| `format` | string | – | ✅ | Alias für `out_format` |
| `target_format` | string | – | ✅ | Alias für `out_format` |
| `target_style` | string | – | 📝 | Deklarativ (wird nicht gelesen) |
| `out_dir` | string | `"./publish"` | ✅ | Ausgabeverzeichnis |
| `out` | string | – | ✅ | Dateiname der Ausgabe |
| `build` | bool | `false` | ✅ | Gating-Flag: nur bei `true` wird gebaut |
| `source_type` | string | `"folder"` | ✅ | `folder` oder `file` |
| `source_format` | string | `"markdown"` | ✅ | Nominell, nur Markdown unterstützt |
| `use_summary` | bool | `true` | ✅ | SUMMARY.md für Kapitelreihenfolge nutzen |
| `use_book_json` | bool | `true` | ✅ | book.json für Metadaten laden |
| `keep_combined` | bool | `false` | ✅ | Kombiniertes .md neben .pdf speichern |
| `summary_mode` | string | `"gitbook"` | ✅ | Stil der SUMMARY-Generierung |
| `summary_manifest` | string | `null` | ✅ | Optionaler Pfad zu Ordering-Manifest |
| `summary_appendices_last` | bool | `false` | ✅ | Anhänge ans Ende sortieren |
| `use_document_types` | bool | `false` | ✅ | Doc-Type-basierte SUMMARY-Generierung |
| `document_type_config` | object | `{}` | ✅ | Konfiguration für Doc-Type-System (§2.5) |
| `reset_build_flag` | bool | `false` | ✅ | `build` nach erfolgreichem Lauf zurücksetzen |
| `generate_attribution` | bool | `false` | ✅ | Attribution-Dateien erzeugen |
| `pdf_options` | object | `{}` | ✅ | PDF-spezifische Optionen (§2.6) |
| `assets` | array | `[]` | ✅ | Asset-Pfade mit `path`, `type`, `copy_to_output` |

### 2.5 document_type_config

| Schlüssel | Typ | Default | Status | Beschreibung |
|-----------|-----|---------|--------|--------------|
| `section_order` | array | `[]` | ✅ | Reihenfolge der Abschnitte in SUMMARY |
| `section_titles` | object | `{}` | ✅ | Überschriften pro Abschnitt |
| `section_titles_by_locale` | object | `{}` | ✅ | Locale-spezifische Überschriften |
| `title_to_doc_type` | object | `{}` | ✅ | Mapping Titel → Doc-Type (Inference) |
| `title_to_doc_type_by_locale` | object | `{}` | ✅ | Locale-spezifisches Mapping |
| `show_in_summary` | object | `{}` | ✅ | Per Doc-Type: in SUMMARY anzeigen? |
| `auto_number_chapters` | bool | `false` | ✅ | „Kapitel N –" Präfix |
| `auto_number_appendices` | bool | `false` | ✅ | „Anhang A –" Präfix |
| `auto_number_parts` | bool | `false` | ✅ | „Teil N" Gruppierung |
| `chapter_appendix_indent` | bool | `false` | ✅ | Einrückung in SUMMARY |
| `chapter_appendix_prefix` | string | `""` | ✅ | Template-String `{chapter}.{id}` |
| `default_order_weight` | int | `100` | ✅ | Sortier-Fallback |

### 2.6 pdf_options

| Schlüssel | Typ | Default | Status | Beschreibung |
|-----------|-----|---------|--------|--------------|
| `emoji_color` | bool | `true` | ✅ | Farb-Emojis aktivieren |
| `emoji_bxcoloremoji` | bool | `false` | ✅ | bxcoloremoji-Paket nutzen (experimentell) |
| `main_font` | string | `"DejaVu Serif"` | ✅ | → Pandoc `-V mainfont` (Legacy-Key) |
| `sans_font` | string | `"DejaVu Sans"` | ✅ | → Pandoc `-V sansfont` (Legacy-Key) |
| `mono_font` | string | `"DejaVu Sans Mono"` | ✅ | → Pandoc `-V monofont` (Legacy-Key) |
| `mainfont` | string | – | ✅ | → Pandoc `-V mainfont` (bevorzugter Key) |
| `sansfont` | string | – | ✅ | → Pandoc `-V sansfont` (bevorzugter Key) |
| `monofont` | string | – | ✅ | → Pandoc `-V monofont` (bevorzugter Key) |
| `mainfont_fallback` | string | `""` | ✅ | LuaTeX Fallback-Chain (`;`-getrennt); bei Overrides `DejaVu Sans:mode=harf` fuer Checkbox-/Textsymbole beibehalten |
| `abort_if_missing_glyph` | bool | `true` | ✅ | Bei fehlenden Glyphen abbrechen |
| `code_block_wrap` | bool | `true` | ✅ | Lange Zeilen in Code-Fences im PDF umbrechen (`fvextra`) |
| `table_paper_strategy` | object | `{}` | ✅ | Redaktionelle Best-Fit-Papierwahl fuer Markdown-Pipe-Tabellen (§2.6.1) |
| `documentclass` | string | `"article"` | ✅ | LaTeX-Dokumentklasse (`report`, `book`, …) |
| `fontsize` | string | `"10pt"` | ✅ | LaTeX-Schriftgröße |
| `geometry` | string | `"margin=1in"` | ✅ | LaTeX-Geometry-Parameter |
| `toc` | bool | folder=`true` | ✅ | Inhaltsverzeichnis |
| `toc-depth` | int | `3` | ✅ | TOC-Tiefe |
| `numbersections` | bool | `false` | ✅ | Abschnitte nummerieren |
| `colorlinks` | bool | `false` | ✅ | Farbige Hyperlinks |
| `linkcolor` | string | – | ✅ | Farbe interner Links |
| `urlcolor` | string | – | ✅ | Farbe externer URLs |
| `citecolor` | string | – | ✅ | Farbe von Zitationslinks |
| `toccolor` | string | – | ✅ | Farbe von TOC-Links |
| `lang` | string | book.json | ✅ | Pandoc `lang` (Silbentrennung/Babel) |
| `header-includes` | string | – | ✅ | Raw-LaTeX für Dokumentpräambel |
| `classoption` | string | – | ✅ | Zusätzliche LaTeX-Klassenoptionen |
| `papersize` | string | – | ✅ | Papiergröße (`a4`, `letter`, …) |
| `linestretch` | string | – | ✅ | Zeilenabstandsfaktor |

### 2.6.1 pdf_options.table_paper_strategy

| Schlüssel | Typ | Default | Status | Beschreibung |
|-----------|-----|---------|--------|--------------|
| `enabled` | bool | `true` | ✅ | Aktiviert das redaktionelle Score-Modell; `false` nutzt nur die Spaltenheuristik |
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

---

## 3. book.json (pro Sprachbaum)

GitBook-kompatible Metadaten. Dient als Fallback für `publish.yml:project`.

| Schlüssel | Typ | Default | Status | Beschreibung |
|-----------|-----|---------|--------|--------------|
| `schema_version` | string | – | ✅ | SemVer-Schema-Version der Datei |
| `title` | string | – | ✅ | Fallback für `project.name` |
| `author` | string | – | ✅ | Fallback für `project.authors` |
| `date` | string | – | ✅ | Fallback für `project.date` |
| `version` | string | – | ✅ | Fallback für `project.version` |
| `language` | string | – | ✅ | Pandoc `lang`-Metadatum für Silbentrennung |
| `description` | string | – | 📝 | Legacy GitBook Metadatum (informativ) |
| `root` | string | `"content/"` | 📝 | Legacy GitBook Metadatum (informativ) |
| `structure.readme` | string | `"README.md"` | 📝 | Legacy GitBook Metadatum (informativ) |
| `structure.summary` | string | `"SUMMARY.md"` | 📝 | Legacy GitBook Metadatum (informativ) |

> `language` wird seit v2.2.0 als Pandoc `lang`-Metadatum genutzt.
> `description`, `root` und `structure.*` sind informative Legacy-Felder.

---

## 4. fonts.yml (gitbook_worker/defaults/)

Zentrale Font-Konfiguration. Single Source of Truth für alle Schriftarten.

| Schlüssel | Typ | Default | Status | Beschreibung |
|-----------|-----|---------|--------|--------------|
| `version` | string | – | ✅ | SemVer |
| `fonts.<KEY>.name` | string | – | ✅ | Font-Name für Pandoc/LuaTeX |
| `fonts.<KEY>.paths` | array | `[]` | ✅ | Pfad-Auflösung mit Fallbacks |
| `fonts.<KEY>.license` | string | – | ✅ | Lizenz-ID (für Attribution) |
| `fonts.<KEY>.license_url` | string | – | ✅ | URL zum Lizenztext |
| `fonts.<KEY>.download_url` | string | `null` | ✅ | Download-URL für FontStorageBootstrapper |
| `fonts.<KEY>.source_url` | string | `null` | ✅ | Quell-Repository (Attribution) |
| `fonts.<KEY>.version` | string | – | ✅ | Font-Version |
| `fonts.<KEY>.fontconfig_name` | string | `null` | 📝 | Informativ (fontconfig-Alias) |
| `fonts.<KEY>.copyright` | string | `null` | ✅ | Copyright-Hinweis → ATTRIBUTION.md |
| `fonts.<KEY>.usage_note` | string | `null` | ✅ | Nutzungshinweis → ATTRIBUTION.md |

---

## 5. Weitere Defaults (gitbook_worker/defaults/)

### frontmatter.yml

Vollständig implementiert. Steuert automatische Frontmatter-Injection.
Siehe Dateikommentare für Details.

| Schlüssel | Status |
|-----------|--------|
| `version`, `enabled`, `patterns.*`, `template.*` | ✅ |

### readme.yml

Vollständig implementiert. Steuert automatische README-Generierung.

| Schlüssel | Status |
|-----------|--------|
| `version`, `enabled`, `patterns.*`, `template.*`, `readme_variants` | ✅ |

### smart.yml

Vollständig implementiert. Manifest-Auflösungsstrategie.

| Schlüssel | Status |
|-----------|--------|
| `version`, `filenames`, `search` | ✅ |

### docker_config.yml

Template-basierte Docker-Namensvergabe.

| Schlüssel | Status | Anmerkung |
|-----------|--------|-----------|
| `docker_names.default.*` | 🔨 | Nutzung in run_docker.py zu verifizieren |
| `docker_names.github-action.*` | 📝 | Für CI-Workflows |
| `docker_names.prod.*` | 📝 | Für Produktion |
| `docker_names.test.*` | 🔨 | Für pytest |
| `docker_names.docker-test.*` | 🔨 | Für Integrationstests |

---

## 6. editorial quality profile (CLI-Option `--profile-config`)

Status: 🔨 Teilweise implementiert fuer `v2.9.1 Abnahmefix`. Die Profile
werden von `gitbook_worker.tools.quality.editorial_metrics` und
`gitbook_worker.tools.quality.editorial_acceptance` gelesen. Die Datei ist
optional; ohne Datei stehen Built-in-Profile zur Verfuegung.

| Schlüssel | Typ | Default | Status | Beschreibung |
|-----------|-----|---------|--------|--------------|
| `version` | string | – | 📝 | Empfohlene SemVer der Profil-Datei; aktuell dokumentiert, noch nicht hart validiert |
| `profiles` | object | – | ✅ | Mapping von Profilnamen auf Regeln |
| `profiles.<name>.network` | bool | `false` | ✅ | Sichtbarer Netzwerkmodus im Report; Netzwerkchecks laufen nur ueber bestehende Tools |
| `profiles.<name>.fail_on_warnings` | bool | `false` | ✅ | Warnungen koennen die Abnahme blockieren |
| `profiles.<name>.markdown.locale_field` | string | `content_lang` | ✅ | Frontmatter-Feld fuer Locale-Erkennung |
| `profiles.<name>.markdown.identity_key` | string | `content_id` | ✅ | Identitaetsfeld fuer Source/Target-Abgleich |
| `profiles.<name>.markdown.source_link_field` | string | `source` | ✅ | Repo-relativer Source-Verweis in Target-Dateien |
| `profiles.<name>.markdown.source_locale` | string | `null` | ✅ | Source-Locale, z. B. `ja` |
| `profiles.<name>.markdown.target_locales` | array | `[]` | ✅ | Target-Locales, z. B. `pl`, `hr`, `no` |
| `profiles.<name>.markdown.forbidden_frontmatter_keys` | array | `lang`, `language`, `lang-version` | ✅ | Verbotene Keys als Findings |
| `profiles.<name>.markdown.required_frontmatter_by_role` | object | source/target defaults | ✅ | Pflichtfelder je Rolle `source`/`target` |
| `profiles.<name>.markdown.allowed_translation_status` | array | `draft`, `in-review`, `approved` | ✅ | Erlaubte Target-Statuswerte |
| `profiles.<name>.markdown.exclude_dirs` | array | Tool-Default | ✅ | Ausgeschlossene Ordner fuer Markdown-Discovery |
| `profiles.<name>.markdown.skip_filenames` | array | `SUMMARY.md` | ✅ | Dateien ohne Pflicht-Frontmatter-Pruefung |
| `profiles.<name>.markdown.long_token_warn_chars` | int | `80` | ✅ | Schwelle fuer echte lange Layout-Tokens; Frontmatter und URL-/Markdown-Link-Tokens werden nicht als Rauschen gemeldet |
| `profiles.<name>.markdown.duplicate_heading_near_window` | int | `3` | ✅ | Kontextfenster fuer nahe doppelte Titel im selben Dokument |
| `profiles.<name>.pdf.low_text_page_threshold` | int | `15` | ✅ | Wenigzeiler-Schwelle pro PDF-Seite |
| `profiles.<name>.pdf.very_low_text_page_threshold` | int | `5` | ✅ | Sehr-wenig-Text-Schwelle pro PDF-Seite |
| `profiles.<name>.pdf.required_fonts` | array | `[]` | ✅ | Erwartete eingebettete PDF-Fontnamen |
| `profiles.<name>.pdf.pdf_targets` | object | `{}` | ✅ | Seitenzahl-Zielkorridore je PDF; `target_pages_min`, `target_pages_max`, `warn_pages_max` werden als Findings ausgewertet |
| `profiles.<name>.pdf.expected_pages` | object | `{}` | ✅ | Erwartete Sample-Seiten je PDF; `page`, `label`, `min_text_lines`, `must_contain` werden geprueft |
| `profiles.<name>.pdf.overflow_warn_pt` | float | `0.1` | ✅ | Warnschwelle fuer modellierte Text-/URL-/DOI-Ueberstaende in Punkten |
| `profiles.<name>.pdf.overflow_fail_pt` | float | `12.0` | ✅ | Fehlerschwelle fuer modellierte Text-/URL-/DOI-Ueberstaende in Punkten |
| `profiles.<name>.pdf.overflow_token_warn_chars` | int | `96` | ✅ | Tokenlaenge ab der ein PDF-Overflow-Signal modelliert wird |
| `profiles.<name>.documentation.fail_on_stale_worker_version` | bool | `false` | ✅ | Worker-Version-Drift im Acceptance-Dossier als harte Findings behandeln |
| `profiles.<name>.documentation.fail_on_stale_page_count` | bool | `false` | ✅ | Reports blockieren, wenn PDF-Artefakte nach dem Reportzeitpunkt veraendert wurden |
| `profiles.<name>.documentation.scan_release_docs` | bool | `true` | ✅ | Release-Dokumente auf alte Worker-Versionen und Seitenzahlen scannen |
| `profiles.<name>.documentation.release_doc_dirs` | array | `docs/releases`, `gitbook_worker/docs/releases` | ✅ | Release-Dokumentationsordner fuer Drift-Scan |

CLI-Ausgaben fuer `editorial_metrics`:

| Option | Typ | Default | Status | Beschreibung |
|--------|-----|---------|--------|--------------|
| `--csv-output` | path | `null` | ✅ | Optionale CSV-Ausgabe fuer Findings |
| `--sarif-output` | path | `null` | ✅ | Optionale SARIF-2.1.0-Ausgabe fuer Findings |
| `--console-summary` | bool | `false` | ✅ | Eine kurze scanbare Statuszeile fuer lokale Runs und CI-Logs |

CLI-Ausgaben fuer `editorial_acceptance`:

| Option | Typ | Default | Status | Beschreibung |
|--------|-----|---------|--------|--------------|
| `--json-output` | path | `null` | ✅ | Strukturierte Acceptance-Summary als JSON |
| `--html-output` | path | `null` | ✅ | Statischer, selbstenthaltener HTML-Report ohne gehostetes Dashboard |
| `--trend-output` | path | `null` | ✅ | JSONL-Trenddatei; haengt pro Lauf einen kompakten Datensatz an |
| `--snapshot-dir` | path | `null` | ✅ | High-Risk-PDF-Seitenindex und optionale PNG-Snapshots |
| `--snapshot-root` | path | `null` | ✅ | Root zur Aufloesung relativer PDF-Pfade fuer Snapshot-Rendering |
| `--snapshot-renderer` | enum | `auto` | ✅ | `auto` nutzt `pdftoppm` falls vorhanden; `none` schreibt nur den Index |
| `--snapshot-max-pages` | int | `20` | ✅ | Maximale High-Risk-Seiten pro PDF fuer Snapshot-Rendering |

Orchestrator-Integration:

| Option/Step | Typ | Default | Status | Beschreibung |
|-------------|-----|---------|--------|--------------|
| `--step editorial-quality` | step | – | ✅ | Fuehrt nach einem Build Metrics + Acceptance aus |
| `--quality-profile` | string | `release` | ✅ | Profil fuer Metrics und Acceptance |
| `--quality-baseline` | path | `null` | ✅ | Baseline-Report fuer Acceptance-Vergleich |
| `--quality-accepted-findings` | path | `null` | ✅ | Restrisiko-Register fuer Acceptance |
| `--quality-gate` | bool | `false` | ✅ | Nicht-null Acceptance-Status als CI-Gate verwenden |
| `--quality-scope` | enum | `current` | ✅ | `current` erzeugt Artefakte fuer `--lang`; `configured` erzeugt je buildbarer lokaler `content.yaml`-Version plus `project-<profile>`-Gesamtdossier |

Der Schritt erzeugt neben JSON/CSV/Markdown auch SARIF,
`*-editorial-report.html`, `editorial-trends.jsonl` und
`snapshots/<lang-profile>/index.html`.
Mit `--quality-scope configured` entstehen zusaetzlich
`project-<profile>-editorial-*`-Artefakte als Gesamtprojekt-Sicht. Remote-
Eintraege und `build: false`-Content werden fuer diesen Lieferumfang bewusst
uebersprungen.

---

## 7. editorial accepted findings (CLI-Option `--accepted-findings`)

Status: ✅ Implementiert fuer `v2.9.1 Abnahmefix`. Die Datei dokumentiert
bewusst akzeptierte Restrisiken fuer `editorial_acceptance`. Akzeptierte Befunde
werden nicht versteckt; sie erscheinen im Dossier. Abgelaufene Akzeptanzen
erzeugen ein hartes Finding.

| Schlüssel | Typ | Default | Status | Beschreibung |
|-----------|-----|---------|--------|--------------|
| `version` | string | – | ✅ | SemVer der Restrisiko-Datei |
| `accepted_findings` | array | `[]` | ✅ | Liste akzeptierter Finding-IDs |
| `accepted_findings[].finding_id` | string | – | ✅ | Exakte stabile Finding-ID aus dem Metrikreport |
| `accepted_findings[].reason` | string | – | ✅ | Redaktionelle Begruendung der Akzeptanz |
| `accepted_findings[].role` | string | – | ✅ | Rolle der akzeptierenden Person, z. B. `editor` |
| `accepted_findings[].date` | string | – | ✅ | Datum der Entscheidung (`YYYY-MM-DD`) |
| `accepted_findings[].expires` | string | `null` | ✅ | Ablaufdatum; abgelaufene Akzeptanzen werden harte Findings |
| `accepted_findings[].release` | string | `null` | ✅ | Optionaler Releasebezug, z. B. `v2.9.1` |

---

## Konfigurationsdatei-Versionen

| Datei | Schema-Version | `version`-Feld | Per-File-Dok |
|-------|---------------|----------------|-------------|
| `content.yaml` | 1.0.0 | ✓ | [content-yaml.md](configs/content-yaml.md) |
| `publish.yml` | 0.1.2 | ✓ | [publish-yml.md](configs/publish-yml.md) |
| `book.json` | 1.0.0 | ✓ | [book-json.md](configs/book-json.md) |
| `fonts.yml` | 1.0.0 | ✓ | [fonts-yml.md](configs/fonts-yml.md) |
| `frontmatter.yml` | 1.0.0 | ✓ | [frontmatter-yml.md](configs/frontmatter-yml.md) |
| `readme.yml` | 1.0.0 | ✓ | [readme-yml.md](configs/readme-yml.md) |
| `smart.yml` | 1.0.0 | ✓ | [smart-yml.md](configs/smart-yml.md) |
| `docker_config.yml` | 1.0.0 | ✓ | [docker-config-yml.md](configs/docker-config-yml.md) |
| editorial quality profile | 1.3.0 | optional | [editorial-quality-profile.md](configs/editorial-quality-profile.md) |
| editorial accepted findings | 1.0.0 | optional | [editorial-accepted-findings.md](configs/editorial-accepted-findings.md) |

---

## Verwandte Dokumente

- [docs/configs/](configs/README.md) — Per-File-Dokumentation mit Versionshistorie
- [AGENTS.md](../AGENTS.md) — Regeln 25–30 (Config-Completeness-Policy)
- [gitbook_worker/docs/backlog/config-completeness-and-documentation.md](../gitbook_worker/docs/backlog/config-completeness-and-documentation.md) — Backlog mit Action Items
- [docs/Configure-Doc-Types.md](Configure-Doc-Types.md) — Doc-Type-System im Detail
- [gitbook_worker/defaults/README.md](../gitbook_worker/defaults/README.md) — Font-System Architektur
