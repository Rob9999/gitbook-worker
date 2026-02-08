---
version: 2.0.0
date: 2026-02-08
status: in-progress
priority: high
target_release: "v2.2.0 „Lückenlos""
history:
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

---

## 2. Audit-Ergebnis: book.json

| Schlüssel | Status | Anmerkung |
|-----------|--------|-----------|
| `title` | ✅ | Fallback für project.name |
| `author` | ✅ | Fallback für project.authors |
| `date` | ✅ | Fallback für project.date |
| `version` | ✅ | Fallback für project.version |
| `language` | ❌ **Unused** | Deklariert, nie vom Publisher gelesen |
| `description` | ❌ **Unused** | Deklariert, nie vom Publisher gelesen |
| `root` | ❌ **Unused** | Deklariert, nie vom Publisher gelesen |
| `structure.readme` | ❌ **Unused** | Deklariert, nie vom Publisher gelesen |
| `structure.summary` | ❌ **Unused** | Deklariert, nie vom Publisher gelesen |

**Action Items:**
- [ ] `language`: Evaluieren ob der Publisher die Sprache aus book.json für Pandoc `lang` nutzen sollte.
- [ ] `root`: Evaluieren ob der Publisher `root` für die Content-Pfadauflösung nutzen sollte.
- [ ] `structure.*`: Evaluieren ob Summary/Readme-Pfade aus book.json gelesen werden sollten statt hardcoded.
- [ ] Alle genutzten Keys dokumentieren; ungenutzte entweder implementieren oder als „legacy GitBook metadata" kennzeichnen.

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
| `fonts.<KEY>.fontconfig_name` | ❌ **Unused** | Nur im EMOJI-Eintrag, nie gelesen |
| `fonts.<KEY>.copyright` | ❌ **Unused** | Deklariert, nie von font_config.py gelesen |
| `fonts.<KEY>.usage_note` | ❌ **Unused** | Deklariert, nie von font_config.py gelesen |

**Action Items:**
- [ ] `fontconfig_name`: In FontStorageBootstrapper oder Docker-Setup nutzen, oder als rein informativ dokumentieren.
- [ ] `copyright`: Im Attribution-Generator nutzen (z.B. für ATTRIBUTION.md Detail-Sektion).
- [ ] `usage_note`: Im Attribution-Generator oder als Kommentar in LICENSE-Dateien nutzen.

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
- [ ] Verifizieren, welche `docker_names` Kontexte von `run_docker.py` tatsächlich gelesen werden.
- [ ] Ungenutzte Kontexte als „deklarativ" kennzeichnen oder implementieren.

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

### Priorität 2: Unused Keys aufräumen

- [ ] `book.json`: `language`, `description`, `root`, `structure.*` evaluieren
- [ ] `fonts.yml`: `fontconfig_name`, `copyright`, `usage_note` in Attribution einbauen oder als informativ deklarieren
- [ ] `publish.yml` → `meta`: Als „deklarativ für CI" explizit dokumentieren

### Priorität 3: Testabdeckung

- [ ] Bestehenden Backlog-Eintrag `publish-yml-comprehensive-testing.md` aktualisieren
- [ ] Für jeden `pdf_options`-Schalter mindestens einen Unit-Test
- [ ] Für jeden `document_type_config`-Schalter mindestens einen Unit-Test
- [ ] Integration-Test: book.json Fallbacks für project.*

### Priorität 4: Fehlende Implementierung

- [ ] `book.json:language` → Pandoc `lang` Variable setzen
- [ ] `book.json:root` → Content-Pfadauflösung
- [ ] `docker_config.yml` Kontexte vollständig in run_docker.py einbinden
- [ ] `fonts.yml:copyright` → ATTRIBUTION.md erweitern

### Priorität 5: Konfigurationsdatei-Versionierung

- [ ] `docker_config.yml`: `version`-Feld ergänzen (aktuell fehlt es komplett)
- [ ] `book.json`: `schema_version`-Feld einführen (das bestehende `version` bezieht sich auf die Projektversion)
- [ ] Per-Config-Datei Versionshistorie in `docs/configs/*.md` bei jeder Schema-Änderung pflegen
- [ ] Versionsprüfung im Code: Alle Defaults-Dateien validieren `version` beim Laden (wie bei publish.yml)
- [ ] `docs/configs/README.md` Index-Tabelle bei Schema-Versionsänderungen aktualisieren

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

- [ ] Fehlende Edge-Case-Samples ergänzen:
  - [ ] Dokument ohne YAML-Frontmatter (testet `frontmatter.yml` Injection)
  - [ ] Dokument mit vollständigem Frontmatter (testet „kein Überschreiben")
  - [ ] Verzeichnis ohne README (testet `readme.yml` Auto-Generation)
  - [ ] Markdown mit nur einer Zeile / leerem Body (Edge Case für Converter)
  - [ ] Datei mit Right-to-Left Text (RTL) (testet Font-Fallback)
  - [ ] Datei mit CJK-Zeichen (testet CJK-Font-Fallback)
  - [ ] Datei mit äthiopischen Zeichen (testet ETHIOPIC-Font-Fallback)
  - [ ] Markdown mit verschachtelten Tabellen und Code-Blöcken
  - [ ] Markdown mit Fußnoten und Querverweisen
- [ ] Feature-spezifische Sprachbäume in `content.yaml` vorsehen:
  - [ ] `de-edge-cases/` — Edge Cases (leere Dateien, Sonderzeichen, RTL)
  - [ ] `en-edge-cases/` — Englische Entsprechungen
  - [ ] Struktur: `book.json`, `publish.yml`, `content/` mit fokussierten Testdateien
  - [ ] In `content.yaml` eintragen mit `type: local`, `build: false` als Default
- [ ] Jeder ✅-Schalter in `publish.yml` hat mindestens einen Sample, der ihn aktiviert
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
| `docker_config.yml` | ✗ | – | **Muss ergänzt werden** |
| `book.json` | (ambig) | – | `version` = Projektversion, kein Schema-Feld |

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
