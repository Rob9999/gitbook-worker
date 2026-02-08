---
version: 1.0.0
date: 2026-02-08
config_schema_version: "1.0.0"
history:
  - "1.0.0: 2026-02-08 — Initial documentation"
---

# frontmatter.yml

## Zweck

Steuert die automatische Injection von YAML-Frontmatter in Markdown-Dateien
während der Workflow-Orchestrierung. Dateien ohne Frontmatter erhalten das
konfigurierte Template; bestehende Felder bleiben unverändert.

## Ort

```
gitbook_worker/defaults/frontmatter.yml       (System-Default)
<lang>/publish.yml → frontmatter: { … }       (Override pro Sprachbaum)
```

## Schema-Version

Aktuell: **1.0.0** — Feld `version`.

## Schlüssel-Referenz

| Schlüssel | Typ | Pflicht | Default | Status | Beschreibung |
|-----------|-----|---------|---------|--------|--------------|
| `version` | string | ✓ | – | ✅ | SemVer-Schema-Version |
| `enabled` | bool | – | `false` | ✅ | Global-Schalter |
| `patterns.include` | array | – | `["content/**/*.md"]` | ✅ | Glob-Patterns für einzuschließende Dateien |
| `patterns.exclude` | array | – | `["**/readme.md", "**/README.md"]` | ✅ | Glob-Patterns für Ausschlüsse (Vorrang) |
| `template.*` | object | – | s.u. | ✅ | 17-Felder-Template für technische Dokumente |

### Template-Felder

| Feld | Typ | Default | Platzhalter |
|------|-----|---------|-------------|
| `id` | string | `""` | – |
| `title` | string | `""` | – |
| `version` | string | `"v0.0.0"` | – |
| `state` | string | `"DRAFT"` | – |
| `evolution` | string | `""` | – |
| `discipline` | string | `""` | – |
| `system` | array | `[]` | – |
| `system_id` | array | `[]` | – |
| `seq` | array | `[]` | – |
| `owner` | string | `""` | – |
| `reviewers` | array | `[]` | – |
| `source_of_truth` | bool | `false` | – |
| `supersedes` | null | `null` | – |
| `superseded_by` | null | `null` | – |
| `rfc_links` | array | `[]` | – |
| `adr_links` | array | `[]` | – |
| `cr_links` | array | `[]` | – |
| `date` | string | `"{{date}}"` | `{{date}}` → Git-Last-Commit-Datum |
| `lang` | string | `"EN"` | – |

## Versionshistorie

| Version | Datum | Änderung |
|---------|-------|----------|
| 1.0.0 | 2026-01-08 | Initiales Schema mit 17-Felder-Template |

## Verwandte Dokumente

- [publish-yml.md](publish-yml.md) — Override via `publish.yml → frontmatter`
