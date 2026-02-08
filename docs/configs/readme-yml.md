---
version: 1.0.0
date: 2026-02-08
config_schema_version: "1.0.0"
history:
  - "1.0.0: 2026-02-08 — Initial documentation"
---

# readme.yml

## Zweck

Steuert die automatische Erzeugung von `README.md`-Dateien in Verzeichnissen,
die noch keine README-Variante haben (case-insensitive Check).

## Ort

```
gitbook_worker/defaults/readme.yml            (System-Default)
<lang>/publish.yml → readme: { … }            (Override pro Sprachbaum)
```

## Schema-Version

Aktuell: **1.0.0** — Feld `version`.

## Schlüssel-Referenz

| Schlüssel | Typ | Pflicht | Default | Status | Beschreibung |
|-----------|-----|---------|---------|--------|--------------|
| `version` | string | ✓ | – | ✅ | SemVer-Schema-Version |
| `enabled` | bool | – | `true` | ✅ | Global-Schalter |
| `patterns.include` | array | – | `[]` (= alle) | ✅ | Glob-Patterns für einzuschließende Verzeichnisse |
| `patterns.exclude` | array | – | (lange Liste) | ✅ | Ausschlüsse (.git, node_modules, .venv, build, …) |
| `template.use_directory_name` | bool | – | `true` | ✅ | Verzeichnisname als Header nutzen |
| `template.header_level` | int | – | `1` | ✅ | Header-Ebene (1–6) |
| `template.footer` | string | – | `""` | ✅ | Zusatzinhalt, `{{directory_name}}` als Platzhalter |
| `readme_variants` | array | – | 17 Varianten | ✅ | Dateinamen die als „README vorhanden" gelten |
| `logging.level` | string | – | `"info"` | ✅ | Log-Level |
| `logging.log_skipped` | bool | – | `false` | ✅ | Übersprungene Verzeichnisse loggen |
| `logging.log_created` | bool | – | `true` | ✅ | Erstellte READMEs loggen |

## Versionshistorie

| Version | Datum | Änderung |
|---------|-------|----------|
| 1.0.0 | 2026-01-08 | Initiales Schema |

## Verwandte Dokumente

- [publish-yml.md](publish-yml.md) — Override via `publish.yml → readme`
