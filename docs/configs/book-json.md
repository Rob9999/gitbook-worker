---
version: 1.1.0
date: 2026-02-08
config_schema_version: "1.0.0"
history:
  - "1.1.0: 2026-02-08 — language→Pandoc implementiert, schema_version eingeführt, Legacy-Keys als 📝 markiert"
  - "1.0.0: 2026-02-08 — Initial documentation"
---

# book.json

## Zweck

GitBook-kompatible Metadaten pro Sprachbaum. Dient als **Fallback** wenn
Werte in `publish.yml → project` fehlen. Der Publisher liest `title`,
`author`, `date` und `version`; die übrigen Felder sind Legacy-Deklarationen
aus dem GitBook-Ökosystem.

## Ort

```
<lang>/book.json       (z. B. de/book.json, en/book.json)
```

## Schema-Version

Aktuell: **1.0.0** — Feld `schema_version` (Top-Level).

Das Feld `version` in der Datei bezieht sich weiterhin auf die **Projektversion**;
`schema_version` ist das eigentliche Datei-Schema-Versionsfeld.

## Schlüssel-Referenz

| Schlüssel | Typ | Pflicht | Default | Status | Beschreibung |
|-----------|-----|---------|---------|--------|--------------|
| `schema_version` | string | – | – | ✅ | SemVer-Schema-Version der Datei |
| `title` | string | – | – | ✅ | Fallback für `project.name` in `publish.yml` |
| `author` | string | – | – | ✅ | Fallback für `project.authors` |
| `date` | string | – | – | ✅ | Fallback für `project.date` |
| `version` | string | – | – | ✅ | Fallback für `project.version` (Projektversion, nicht Schema) |
| `language` | string | – | – | ✅ | Pandoc `lang`-Variable für Silbentrennung/Locale |
| `description` | string | – | – | 📝 | Legacy GitBook Metadatum (informativ) |
| `root` | string | – | `"content/"` | 📝 | Legacy GitBook Metadatum (informativ) |
| `structure.readme` | string | – | `"README.md"` | 📝 | Legacy GitBook Metadatum (informativ) |
| `structure.summary` | string | – | `"SUMMARY.md"` | 📝 | Legacy GitBook Metadatum (informativ) |

## Implementierte Änderungen (v2.2.0)

- ✅ **`language`** → Wird als Pandoc `lang`-Metadatum gesetzt (Silbentrennung, Locale)
- ✅ **`schema_version`** → Neues Feld für Datei-Schema-Versionierung mit SemVer-Validation
- 📝 **`description`**, **`root`**, **`structure.*`** → Als Legacy-GitBook-Metadaten dokumentiert (informativ, kein Code liest sie)

## Beispiel

```json
{
  "schema_version": "1.0.0",
  "title": "Das SAMPLE Buch",
  "author": "SAMPLE Team",
  "date": "2026-01-08",
  "language": "de",
  "description": "Beispiel-Buch für Layout und Tests.",
  "root": "content/",
  "structure": {
    "readme": "README.md",
    "summary": "SUMMARY.md"
  }
}
```

## Versionshistorie

| Version | Datum | Änderung |
|---------|-------|----------|
| 1.0.0 | 2026-02-08 | `schema_version` eingeführt, `language` implementiert |
| – | 2025-12-05 | Übernahme des GitBook-Formats |

## Verwandte Dokumente

- [publish-yml.md](publish-yml.md) — publish.yml überschreibt book.json-Werte
- [docs/customer-installation.md](../customer-installation.md)
