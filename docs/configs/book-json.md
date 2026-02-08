---
version: 1.0.0
date: 2026-02-08
config_schema_version: "– (kein version-Feld)"
history:
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

**Kein `version`-Feld** vorhanden — `book.json` hat kein eigenes Schema-Versions-Feld.
Das Feld `version` in der Datei bezieht sich auf die **Projektversion**, nicht auf
das Datei-Schema.

> 🚧 **Backlog**: Ein `schema_version`-Feld sollte eingeführt werden, um
> zukünftige Erweiterungen sauber zu versionieren.

## Schlüssel-Referenz

| Schlüssel | Typ | Pflicht | Default | Status | Beschreibung |
|-----------|-----|---------|---------|--------|--------------|
| `title` | string | – | – | ✅ | Fallback für `project.name` in `publish.yml` |
| `author` | string | – | – | ✅ | Fallback für `project.authors` |
| `date` | string | – | – | ✅ | Fallback für `project.date` |
| `version` | string | – | – | ✅ | Fallback für `project.version` (Projektversion, nicht Schema) |
| `language` | string | – | – | ❌ | Deklariert, nie vom Publisher gelesen |
| `description` | string | – | – | ❌ | Deklariert, nie vom Publisher gelesen |
| `root` | string | – | `"content/"` | ❌ | Deklariert, nie vom Publisher gelesen |
| `structure.readme` | string | – | `"README.md"` | ❌ | Deklariert, nie vom Publisher gelesen |
| `structure.summary` | string | – | `"SUMMARY.md"` | ❌ | Deklariert, nie vom Publisher gelesen |

## Offene Punkte

- **`language`** → Könnte als Pandoc `lang`-Variable genutzt werden
- **`root`** → Könnte für Content-Pfadauflösung statt Hardcoding genutzt werden
- **`structure.*`** → Könnte README/SUMMARY-Pfade dynamisch auflösen statt Annahme von Defaults

## Beispiel

```json
{
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
| – | 2025-12-05 | Übernahme des GitBook-Formats |

## Verwandte Dokumente

- [publish-yml.md](publish-yml.md) — publish.yml überschreibt book.json-Werte
- [docs/customer-installation.md](../customer-installation.md)
