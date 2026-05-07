---
version: 1.2.2
date: 2026-05-07
history:
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

Hinweis fuer v2.4.3: Der PDF-Font-Guard- und Heading-Hotfix aendert keine
Konfigurationsschluessel; die Windows-Font-Stub-Haertung, ERDA-Script-Font-Pfade
und H4/H5-Blockheadings werden intern durch den Publisher aktiviert.

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
| `mainfont_fallback` | string | `""` | ✅ | LuaTeX Fallback-Chain (`;`-getrennt) |
| `abort_if_missing_glyph` | bool | `true` | ✅ | Bei fehlenden Glyphen abbrechen |
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

## Konfigurationsdatei-Versionen

| Datei | Schema-Version | `version`-Feld | Per-File-Dok |
|-------|---------------|----------------|-------------|
| `content.yaml` | 1.0.0 | ✓ | [content-yaml.md](configs/content-yaml.md) |
| `publish.yml` | 0.1.1 | ✓ | [publish-yml.md](configs/publish-yml.md) |
| `book.json` | 1.0.0 | ✓ | [book-json.md](configs/book-json.md) |
| `fonts.yml` | 1.0.0 | ✓ | [fonts-yml.md](configs/fonts-yml.md) |
| `frontmatter.yml` | 1.0.0 | ✓ | [frontmatter-yml.md](configs/frontmatter-yml.md) |
| `readme.yml` | 1.0.0 | ✓ | [readme-yml.md](configs/readme-yml.md) |
| `smart.yml` | 1.0.0 | ✓ | [smart-yml.md](configs/smart-yml.md) |
| `docker_config.yml` | 1.0.0 | ✓ | [docker-config-yml.md](configs/docker-config-yml.md) |

---

## Verwandte Dokumente

- [docs/configs/](configs/README.md) — Per-File-Dokumentation mit Versionshistorie
- [AGENTS.md](../AGENTS.md) — Regeln 25–30 (Config-Completeness-Policy)
- [gitbook_worker/docs/backlog/config-completeness-and-documentation.md](../gitbook_worker/docs/backlog/config-completeness-and-documentation.md) — Backlog mit Action Items
- [docs/Configure-Doc-Types.md](Configure-Doc-Types.md) — Doc-Type-System im Detail
- [gitbook_worker/defaults/README.md](../gitbook_worker/defaults/README.md) — Font-System Architektur
