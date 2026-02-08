---
version: 1.0.0
date: 2026-02-08
config_schema_version: "1.0.0"
history:
  - "1.0.0: 2026-02-08 — Initial documentation"
---

# content.yaml

## Zweck

Zentrale Sprach- und Quellenkonfiguration auf Repo-Ebene.
Der Orchestrator liest diese Datei um festzustellen, welche Sprachbäume
existieren, ob sie lokal oder remote (Git) liegen, und welche Sprache als
Standard gilt.

## Ort

```
<repo-root>/content.yaml
```

## Schema-Version

Aktuell: **1.0.0** — Feld `version` in der Datei.

## Schlüssel-Referenz

| Schlüssel | Typ | Pflicht | Default | Status | Beschreibung |
|-----------|-----|---------|---------|--------|--------------|
| `version` | string | ✓ | – | ✅ | SemVer-Schema-Version |
| `default` | string | ✓ | – | ✅ | Standard-Sprache (`de`, `en`, …) wenn `--lang` nicht übergeben |
| `contents` | array | ✓ | – | ✅ | Liste der Inhaltsquellen |
| `contents[].id` | string | ✓ | – | ✅ | Sprachkürzel, z. B. `de`, `en`, `ua` |
| `contents[].type` | string | ✓ | – | ✅ | `local` oder `git` |
| `contents[].uri` | string | ✓ | – | ✅ | Pfad (lokal) oder Git-URL (remote) |
| `contents[].description` | string | – | `""` | ✅ | Menschenlesbare Beschreibung |
| `contents[].credentialRef` | string | – | `null` | ✅ | Env-Variable mit SSH-Deploy-Key (nur `type: git`) |
| `contents[].branch` | string | – | `null` | ✅ | Git-Branch (nur `type: git`) |

## Beispiel

```yaml
version: 1.0.0
default: de
contents:
  - id: de
    type: local
    uri: de/
    description: German baseline content
  - id: en
    type: local
    uri: en/
    description: English content
  - id: ua
    type: git
    uri: github.com:rob9999@democratic-social-wins
    description: Ukrainian content (remote)
    credentialRef: GITBOOK_CONTENT_UA_DEPLOY_KEY
    branch: main
```

## Versionshistorie

| Version | Datum | Änderung |
|---------|-------|----------|
| 1.0.0 | 2025-12-05 | Initiales Schema mit `local` und `git` Typen |

## Verwandte Dokumente

- [docs/multilingual-content-guide.md](../multilingual-content-guide.md)
- [docs/contributor-new-language.md](../contributor-new-language.md)
