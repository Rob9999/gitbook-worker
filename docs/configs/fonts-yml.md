---
version: 1.0.0
date: 2026-02-08
config_schema_version: "1.0.0"
history:
  - "1.0.0: 2026-02-08 — Initial documentation"
---

# fonts.yml

## Zweck

Zentrale Font-Konfiguration und **Single Source of Truth** für alle Schriftarten,
die GitBook Worker verwendet. Sicherstellung von Lizenz-Compliance, Attribution
und reproduzierbaren Builds.

## Ort

```
gitbook_worker/defaults/fonts.yml
```

## Schema-Version

Aktuell: **1.0.0** — Feld `version` (Top-Level).

## Design-Prinzipien

1. **Keine hardcodierten Fonts** — alles muss in `fonts.yml` stehen (AGENTS.md §14)
2. **Dockerfile.dynamic** liest `fonts.yml` und installiert nur konfigurierte Fonts
3. **Build schlägt fehl** statt auf System-Fonts zurückzufallen
4. **LuaTeX Cache Guard** — fehlende Fonts im Cache → Early Abort

## Schlüssel-Referenz

| Schlüssel | Typ | Pflicht | Default | Status | Beschreibung |
|-----------|-----|---------|---------|--------|--------------|
| `version` | string | ✓ | – | ✅ | SemVer-Schema-Version |
| `fonts` | object | ✓ | – | ✅ | Fonts nach Schlüssel (CJK, EMOJI, SERIF, …) |
| `fonts.<KEY>.name` | string | ✓ | – | ✅ | Font-Name für Pandoc/LuaTeX |
| `fonts.<KEY>.paths` | array | ✓* | `[]` | ✅ | Pfad-Auflösung mit Fallbacks |
| `fonts.<KEY>.license` | string | ✓ | – | ✅ | Lizenz-ID (`CC BY 4.0`, `OFL 1.1`, …) |
| `fonts.<KEY>.license_url` | string | ✓ | – | ✅ | URL zum Lizenztext |
| `fonts.<KEY>.download_url` | string | – | `null` | ✅ | Download-URL für FontStorageBootstrapper |
| `fonts.<KEY>.source_url` | string | – | `null` | ✅ | Quell-Repository (Attribution) |
| `fonts.<KEY>.version` | string | ✓ | – | ✅ | Font-Version |
| `fonts.<KEY>.fontconfig_name` | string | – | `null` | ❌ | Deklariert, nie gelesen |
| `fonts.<KEY>.copyright` | string | – | `null` | ❌ | Deklariert, nie von `font_config.py` gelesen |
| `fonts.<KEY>.usage_note` | string | – | `null` | ❌ | Deklariert, nie gelesen |

\* `paths` oder `download_url` — mindestens eines muss gesetzt sein.

## Aktuelle Fonts (v1.0.0)

| Key | Name | Version | Lizenz |
|-----|------|---------|--------|
| CJK | ERDA CC-BY CJK | 1.0.0 | CC BY 4.0 |
| INDIC | ERDA CC-BY Indic | 1.0.0 | CC BY 4.0 |
| ETHIOPIC | ERDA CC-BY Ethiopic | 1.0.0 | CC BY 4.0 |
| EMOJI | Twemoji Mozilla | 0.7.0 | CC BY 4.0 |
| MONO | DejaVu Sans Mono | 2.37 | Bitstream Vera + PD |
| SANS | DejaVu Sans | 2.37 | Bitstream Vera + PD |
| SERIF | DejaVu Serif | 2.37 | Bitstream Vera + PD |

## Offene Punkte

- **`fontconfig_name`** → Im Docker-Setup oder FontStorageBootstrapper nutzen, oder als informativ deklarieren
- **`copyright`** → Im Attribution-Generator nutzen (Detail-Sektion in ATTRIBUTION.md)
- **`usage_note`** → Im Attribution-Generator oder LICENSE-Dateien nutzen

## Versionshistorie

| Version | Datum | Änderung |
|---------|-------|----------|
| 1.0.0 | 2026-01-08 | Initiales Schema mit 7 Fonts |

## Verwandte Dokumente

- [gitbook_worker/defaults/README.md](../../gitbook_worker/defaults/README.md) — Font-System Architektur
- [gitbook_worker/docs/attentions/lua-font-cache.md](../../gitbook_worker/docs/attentions/lua-font-cache.md) — LuaTeX Cache Guard
- AGENTS.md §14–17 — Font Management Policy
