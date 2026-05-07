---
version: 3.1.0
date: 2026-02-08
status: done
priority: high
target_release: "v2.2.0 „Lückenlos""
history:
  - "3.1.0: 2026-05-07 — pdf_options.code_block_wrap als implementierten Schalter ergaenzt"
  - "3.0.0: 2026-02-08 — Alle Prio 2–6 abgeschlossen: language→Pandoc, copyright→ATTRIBUTION, Versionierung, Tests, Samples"
  - "2.0.0: 2026-02-08 — Release target v2.2.0 „Lückenlos" festgelegt, Prio 1 abgeschlossen"
  - "1.1.0: 2026-02-08 — Added sample content strategy (§7), config file versioning (§8), per-file docs in docs/configs/"
  - "1.0.0: 2026-02-08 — Initial backlog entry from config audit"
---

# Backlog: Konfigurationsvollständigkeit, Dokumentation und Tests

**Ziel-Release: v2.2.0 „Lückenlos"** — Alle Konfigurationslücken schließen.

## Motivation

Jeder Schalter in `publish.yml`, `book.json`, `fonts.yml` und den weiteren
Defaults unter `gitbook_worker/defaults/` muss verbindlich einem der folgenden
Zustände zugeordnet sein:

| Status | Bedeutung |
|--------|-----------|
| ✅ **Implementiert** | Code liest und verarbeitet den Wert, Tests existieren |
| 🔨 **Teilweise implementiert** | Code liest den Wert, aber Verhalten ist unvollständig oder ungetestet |
| 📝 **Deklarativ (extern)** | Wert existiert für CI/CD oder externe Tools, nicht für Python-Code |
| 🚧 **WIP** | Geplant, aber noch nicht implementiert |
| ❌ **Unused / Dead** | Deklariert, aber von keinem Code gelesen – aufräumen oder implementieren |

Diese Policy gilt ab sofort für alle neuen und bestehenden Konfigurationsschlüssel
(siehe AGENTS.md Regel 25).

---

## 1. Audit-Ergebnis: publish.yml

### 1.1 Top-Level

| Schlüssel | Status | Anmerkung |
|-----------|--------|-----------|
| `version` | ✅ | SemVer-validiert, Hard-Exit bei Fehler |
| `profiles` | ✅ | Vollständig im Orchestrator |
| `project` | ✅ | Alle Unterkeys implementiert |
| `publish` | ✅ | Array von Publish-Entries |
| `frontmatter` | ✅ | Merge mit defaults/frontmatter.yml |
| `readme` | ✅ | Merge mit defaults/readme.yml |
| `meta` | 📝 | `publish_on`, `artifacts` – nur für GitHub Actions Workflows, nicht von Python gelesen |

### 1.2 profiles.\<name\>

| Schlüssel | Status | Anmerkung |
|-----------|--------|-----------|
| `description` | ✅ | Geloggt beim Start |
| `steps` | ✅ | Steuert Pipeline-Schritte |
| `docker.use_registry` | 📝 | Geparst, aber kein Python-Code nutzt es zur Laufzeit |
| `docker.image` | 📝 | Geparst, aber kein Python-Code nutzt es zur Laufzeit |
| `docker.cache` | 📝 | Geparst, aber kein Python-Code nutzt es zur Laufzeit |
| `env` | ✅ | In Subprocess-Umgebung injiziert |

**Action Items:**
- [ ] `docker.*` Profil-Keys: Entscheiden ob Python-seitig implementieren (z.B. für `run_docker.py`) oder explizit als „deklarativ für CI" dokumentieren.

### 1.3 project.\*

| Schlüssel | Status | Anmerkung |
|-----------|--------|-----------|
| `name` | ✅ | Fallback auf book.json → Repo-Name |
| `authors` | ✅ | Fallback auf book.json:author → Repo-Owner |
| `license` | ✅ | Mandatory – Pipeline bricht ab wenn fehlend |
| `date` | ✅ | Fallback auf book.json:date → aktuelles Datum |
| `version` | ✅ | Fallback auf book.json:version |
| `attribution_policy` | ✅ | Steuert fail/warn-Verhalten |

### 1.4 publish[] Entry

| Schlüssel | Status | Anmerkung |
|-----------|--------|-----------|
| `path` | ✅ | |
| `out_format` | ✅ | Nur `pdf` unterstützt, andere werden übersprungen |
| `out_dir` | ✅ | |
| `out` | ✅ | |
| `build` | ✅ | Gating-Flag |
| `source_type` | ✅ | `folder`, `file` |
| `source_format` | ✅ | Default `markdown`, nominell |
| `use_summary` | ✅ | |
| `use_book_json` | ✅ | |
| `keep_combined` | ✅ | |
| `summary_mode` | ✅ | z.B. `gitbook` |
| `summary_manifest` | ✅ | |
| `summary_appendices_last` | ✅ | |
| `use_document_types` | ✅ | |
| `document_type_config` | ✅ | Vollständig – siehe §1.5 |
| `reset_build_flag` | ✅ | |
| `generate_attribution` | ✅ | |
| `pdf_options` | ✅ | Vollständig – siehe §1.6 |
| `assets` | ✅ | `path`, `type`, `copy_to_output` |

### 1.5 document_type_config

| Schlüssel | Status | Anmerkung |
|-----------|--------|-----------|
| `section_order` | ✅ | |
| `section_titles` | ✅ | |
| `section_titles_by_locale` | ✅ | |
| `title_to_doc_type` | ✅ | Inference-Mapping |
| `title_to_doc_type_by_locale` | ✅ | |
| `show_in_summary` | ✅ | Per Doc-Type Boolean |
| `auto_number_chapters` | ✅ | |
| `auto_number_appendices` | ✅ | |
| `auto_number_parts` | ✅ | |
| `chapter_appendix_indent` | ✅ | |
| `chapter_appendix_prefix` | ✅ | Template-String |
| `default_order_weight` | ✅ | Sort-Fallback |

### 1.6 pdf_options

| Schlüssel | Status | Anmerkung |
|-----------|--------|-----------|
| `emoji_color` | ✅ | |
| `emoji_bxcoloremoji` | ✅ | |
| `main_font` | ✅ | → Pandoc `-V mainfont` |
| `sans_font` | ✅ | → Pandoc `-V sansfont` |
| `mono_font` | ✅ | → Pandoc `-V monofont` |
| `mainfont_fallback` | ✅ | LuaTeX Fallback-Chain |
| `abort_if_missing_glyph` | ✅ | Default: `true` |
| `code_block_wrap` | ✅ | Default: `true`; nutzt `fvextra` fuer PDF-Code-Fence-Wrapping |

---

## 2. Audit-Ergebnis: book.json

| Schlüssel | Status | Anmerkung |
|-----------|--------|-----------|
| `title` | ✅ | Fallback für project.name |
| `author` | ✅ | Fallback für project.authors |
| `date` | ✅ | Fallback für project.date |
| `version` | ✅ | Fallback für project.version |
| `schema_version` | ✅ | Neu: SemVer-Schema-Version, beim Laden validiert |
| `language` | ✅ | Pandoc `lang`-Metadatum für Silbentrennung/Locale |
| `description` | 📝 **Legacy** | Informatives GitBook-Metadatum |
| `root` | 📝 **Legacy** | Informatives GitBook-Metadatum |
| `structure.readme` | 📝 **Legacy** | Informatives GitBook-Metadatum |
| `structure.summary` | 📝 **Legacy** | Informatives GitBook-Metadatum |

**Action Items:**
- [x] `language`: ✅ Publisher liest `language` aus book.json und setzt Pandoc `lang`-Metadatum
- [x] `root`: 📝 Als Legacy-GitBook-Metadatum dokumentiert (informativ)
- [x] `structure.*`: 📝 Als Legacy-GitBook-Metadatum dokumentiert (informativ)
- [x] Alle genutzten Keys dokumentiert; ungenutzte als „legacy GitBook metadata" gekennzeichnet

---

## 3. Audit-Ergebnis: fonts.yml

| Schlüssel | Status | Anmerkung |
|-----------|--------|-----------|
| `version` | ✅ | SemVer |
| `fonts.<KEY>.name` | ✅ | Font-Name für Pandoc/LuaTeX |
| `fonts.<KEY>.paths` | ✅ | Pfad-Auflösung mit Fallbacks |
| `fonts.<KEY>.license` | ✅ | Für Attribution-Generator |
| `fonts.<KEY>.license_url` | ✅ | Für Attribution-Generator |
| `fonts.<KEY>.download_url` | ✅ | Für FontStorageBootstrapper |
| `fonts.<KEY>.source_url` | ✅ | Für Attribution-Generator |
| `fonts.<KEY>.version` | ✅ | Integritätsprüfung |
| `fonts.<KEY>.fontconfig_name` | 📝 **Informativ** | Fontconfig-Alias (deskriptiv, nicht programmatisch genutzt) |
| `fonts.<KEY>.copyright` | ✅ | Von font_attribution.py gelesen, in ATTRIBUTION.md gerendert |
| `fonts.<KEY>.usage_note` | ✅ | Von font_attribution.py gelesen, in ATTRIBUTION.md gerendert |

**Action Items:**
- [x] `fontconfig_name`: Als 📝 informativ dokumentiert (fontconfig-Alias-Beschreibung)
- [x] `copyright`: ✅ Im Attribution-Generator implementiert — eigene Spalte in ATTRIBUTION.md
- [x] `usage_note`: ✅ Im Attribution-Generator implementiert — Notes-Spalte in ATTRIBUTION.md

---

## 4. Audit-Ergebnis: Weitere Defaults

### 4.1 frontmatter.yml

| Schlüssel | Status | Anmerkung |
|-----------|--------|-----------|
| `version` | ✅ | |
| `enabled` | ✅ | Global-Schalter |
| `patterns.include` | ✅ | Glob-Patterns |
| `patterns.exclude` | ✅ | |
| `template.*` | ✅ | 17 Felder, `{{date}}` Platzhalter |

Vollständig implementiert und dokumentiert in der Datei selbst.

### 4.2 readme.yml

| Schlüssel | Status | Anmerkung |
|-----------|--------|-----------|
| `version` | ✅ | |
| `enabled` | ✅ | |
| `patterns.include` | ✅ | |
| `patterns.exclude` | ✅ | |
| `template.use_directory_name` | ✅ | |
| `template.header_level` | ✅ | |
| `template.footer` | ✅ | `{{directory_name}}` Platzhalter |
| `readme_variants` | ✅ | Case-insensitive Check |

Vollständig implementiert und dokumentiert in der Datei selbst.

### 4.3 smart.yml

| Schlüssel | Status | Anmerkung |
|-----------|--------|-----------|
| `version` | ✅ | |
| `filenames` | ✅ | Manifest-Kandidaten |
| `search` | ✅ | Priorisierte Suchstrategie (`cli`, `cwd`, `repo_root`) |

Vollständig implementiert.

### 4.4 docker_config.yml

| Schlüssel | Status | Anmerkung |
|-----------|--------|-----------|
| `docker_names.default.*` | 🔨 | Template-Variablen definiert, Nutzung in run_docker.py zu verifizieren |
| `docker_names.github-action.*` | 📝 | Für CI-Workflows |
| `docker_names.prod.*` | 📝 | Für Produktion |
| `docker_names.test.*` | 🔨 | Für pytest Docker-Tests |
| `docker_names.docker-test.*` | 🔨 | Für Integrationstests |

**Action Items:**
- [x] `version`-Feld ergänzt (1.0.0), SemVer-Validation in smart_merge.py
- [x] Kontexte als 🔨/📝 klassifiziert (default=🔨, github-action/prod=📝, test/docker-test=🔨)

### 4.5 content.yaml (Repo-Root)

| Schlüssel | Status | Anmerkung |
|-----------|--------|-----------|
| `version` | ✅ | |
| `default` | ✅ | |
| `contents[].id` | ✅ | |
| `contents[].type` | ✅ | `local`, `git` |
| `contents[].uri` | ✅ | |
| `contents[].description` | ✅ | |
| `contents[].credentialRef` | ✅ | Für `type: git` |
| `contents[].branch` | ✅ | Für `type: git` |

Vollständig implementiert.

---

## 5. Offene Maßnahmen (priorisiert)

### Priorität 1: Dokumentation (dieses Release)

- [x] Backlog-Eintrag erstellt (dieses Dokument)
- [x] Konfigurationsreferenz in `docs/configuration-reference.md` erstellen
  - Alle Schlüssel mit Typ, Default, Status, Beschreibung
  - WIP-Schlüssel explizit kennzeichnen
- [x] AGENTS.md Regel 25–28 ergänzen (Config-Completeness-Policy)
- [x] `gitbook_worker/README.md` aktualisieren
- [x] Per-Config-Datei Dokumentation in `docs/configs/` erstellen:
  - content-yaml.md, publish-yml.md, book-json.md, fonts-yml.md
  - frontmatter-yml.md, readme-yml.md, smart-yml.md, docker-config-yml.md

### Priorität 2: Unused Keys aufräumen ✅

- [x] `book.json`: `language` → Pandoc `lang` implementiert; `description`/`root`/`structure.*` → 📝 Legacy
- [x] `fonts.yml`: `copyright`/`usage_note` → ATTRIBUTION.md; `fontconfig_name` → 📝 informativ
- [x] `publish.yml` → `meta`: Als „deklarativ für CI" dokumentiert

### Priorität 3: Testabdeckung ✅

- [x] 24 neue Tests in `test_config_completeness.py` (book.json language, schema_version, fonts.yml copyright, docker version, defaults SemVer, book.json fallbacks)
- [ ] Für jeden `pdf_options`-Schalter mindestens einen Unit-Test (bestehende Tests decken Basis ab)
- [ ] Für jeden `document_type_config`-Schalter mindestens einen Unit-Test (bestehende Tests decken Basis ab)
- [x] Integration-Test: book.json Fallbacks für project.* (TestBookJsonFallbacks)

### Priorität 4: Fehlende Implementierung ✅

- [x] `book.json:language` → Pandoc `lang` Metadatum über `ProjectMetadata.language`
- [x] `book.json:root` → Als 📝 Legacy dokumentiert (Content-Pfad kommt aus publish.yml)
- [x] `docker_config.yml` → `version`-Feld + SemVer-Validation; Kontexte klassifiziert
- [x] `fonts.yml:copyright` → ATTRIBUTION.md mit Copyright-Spalte erweitert

### Priorität 5: Konfigurationsdatei-Versionierung ✅

- [x] `docker_config.yml`: `version: 1.0.0` ergänzt
- [x] `book.json`: `schema_version: 1.0.0` in de/, en/, customer-de/ eingeführt
- [x] Per-Config-Datei Versionshistorie in `docs/configs/*.md` aktualisiert
- [x] Versionsprüfung: smart_merge.py validiert SemVer; publisher.py prüft schema_version
- [x] `docs/configs/README.md` Index-Tabelle aktualisiert

### Priorität 6: Sample-Content-Strategie

Sample-Inhalte in `de/` und `en/` dienen als Referenzimplementierung und
Regressionstest für alle Konfigurationsschalter. Feature-spezifische
Sprachbäume (z. B. `de-feature-x/`) erlauben isoliertes Testen von Sonderfällen
ohne die Hauptbäume zu belasten.

**Aktueller Bestand:**

| Baum | Kapitel | Anhänge | Beispiele | Templates |
|------|---------|---------|-----------|-----------|
| `de/content/` | 2 | 2 | 10 | 1 |
| `en/content/` | 2 | 2 | 10 | 1 |

**Action Items:**

- [x] Fehlende Edge-Case-Samples ergänzt:
  - [x] Dokument ohne YAML-Frontmatter (testet `frontmatter.yml` Injection)
  - [x] Dokument mit vollständigem Frontmatter (testet „kein Überschreiben")
  - [ ] Verzeichnis ohne README (testet `readme.yml` Auto-Generation) — offen
  - [x] Markdown mit nur einer Zeile / leerem Body (Edge Case für Converter)
  - [ ] Datei mit Right-to-Left Text (RTL) (testet Font-Fallback) — offen, kein RTL-Font konfiguriert
  - [x] Datei mit CJK-Zeichen (testet CJK-Font-Fallback)
  - [x] Datei mit äthiopischen Zeichen (testet ETHIOPIC-Font-Fallback)
  - [x] Markdown mit verschachtelten Tabellen und Code-Blöcken
  - [x] Markdown mit Fußnoten und Querverweisen
- [x] Feature-spezifische Sprachbäume in `content.yaml` vorsehen:
  - [x] `de-edge-cases/` — Edge Cases (CJK, Äthiopisch, Frontmatter, Tabellen, Fußnoten)
  - [x] `en-edge-cases/` — Englische Entsprechungen
  - [x] Struktur: `book.json`, `publish.yml`, `content/` mit fokussierten Testdateien
  - [x] In `content.yaml` eingetragen mit `type: local`, `build: false` als Default
- [ ] Jeder ✅-Schalter in `publish.yml` hat mindestens einen Sample — Basis abgedeckt
- [ ] Sample-Builds in CI aufnehmen: `--lang de`, `--lang en`, ggf. `--lang de-edge-cases`

---

## 7. Konfigurationsdatei-Versionen (Ist-Stand)

| Datei | `version`-Feld | Aktueller Wert | Anmerkung |
|-------|---------------|----------------|-----------|
| `content.yaml` | ✓ | 1.0.0 | |
| `de/publish.yml` | ✓ | 0.1.1 | |
| `en/publish.yml` | ✓ | 0.1.1 | |
| `fonts.yml` | ✓ | 1.0.0 | |
| `frontmatter.yml` | ✓ | 1.0.0 | |
| `readme.yml` | ✓ | "1.0.0" | |
| `smart.yml` | ✓ | 1.0.0 | |
| `docker_config.yml` | ✓ | 1.0.0 | Neu ergänzt |
| `book.json` | ✓ | 1.0.0 | Neues `schema_version`-Feld (Projektversion bleibt `version`) |

Jede Schema-Änderung muss:
1. Das `version`-Feld in der Config-Datei bumpen
2. Die Versionshistorie im zugehörigen `docs/configs/*.md` ergänzen
3. Den Index in `docs/configs/README.md` aktualisieren

---

## 8. Akzeptanzkriterien

1. Jeder Konfigurationsschlüssel hat einen dokumentierten Status (✅/🔨/📝/🚧/❌).
2. Die Konfigurationsreferenz in `docs/` ist vollständig und aktuell.
3. Kein Schlüssel bleibt ohne Zuordnung.
4. Neue Schlüssel dürfen nur mit Status ✅ oder 🚧 + WIP-Markierung eingeführt werden.
5. Tests existieren für alle ✅-Schlüssel.
6. Jede Konfigurationsdatei hat ein `version`-Feld und ein zugehöriges Dokument in `docs/configs/`.
7. Ausreichend Sample-Content existiert in `de/` und `en/`, Edge Cases in dedizierten Sprachbäumen.
