---
version: 1.0.0
date: 2026-02-08
config_schema_version: "1.0.0"
history:
  - "1.0.0: 2026-02-08 — Initial documentation"
---

# smart.yml

## Zweck

Konfiguriert die automatische Manifest-Auflösung: Welche Dateinamen als
Manifest-Kandidaten gelten und in welcher Reihenfolge nach einem Manifest
gesucht wird, wenn kein expliziter `--manifest`-Pfad übergeben wird.

## Ort

```
gitbook_worker/defaults/smart.yml
```

## Schema-Version

Aktuell: **1.0.0** — Feld `version`.

## Schlüssel-Referenz

| Schlüssel | Typ | Pflicht | Default | Status | Beschreibung |
|-----------|-----|---------|---------|--------|--------------|
| `version` | string | ✓ | – | ✅ | SemVer-Schema-Version |
| `filenames` | array | ✓ | `["publish.yml", "publish.yaml"]` | ✅ | Manifest-Kandidaten |
| `search` | array | ✓ | (siehe unten) | ✅ | Priorisierte Suchstrategie |
| `search[].type` | string | ✓ | – | ✅ | `cli`, `cwd` oder `repo_root` |

### Suchstrategie (Default)

1. **`cli`** — Expliziter CLI-Pfad (höchste Priorität)
2. **`cwd`** — Aktuelles Arbeitsverzeichnis
3. **`repo_root`** — Erkanntes Repository-Root

## Beispiel

```yaml
version: 1.0.0
filenames:
  - publish.yml
  - publish.yaml
search:
  - type: cli
  - type: cwd
  - type: repo_root
```

## Versionshistorie

| Version | Datum | Änderung |
|---------|-------|----------|
| 1.0.0 | 2026-01-08 | Initiales Schema |
