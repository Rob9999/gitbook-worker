---
version: 1.2.0
date: 2026-05-10
config_schema_version: "1.0.0"
history:
  - "1.2.0: 2026-05-10 — CC-BY-only policy boundary, no-Noto rule and ERDA Emoji/v2.10.0 note documented"
  - "1.1.0: 2026-02-08 — copyright→ATTRIBUTION, usage_note→ATTRIBUTION implementiert, fontconfig_name als 📝"
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
5. **Lizenzgrenze** — ausser der bestehenden DejaVu-Familie werden nur CC BY 4.0 lizenzierte Projektfonts und Emoji-Fonts aufgenommen
6. **No Noto** — Noto-Fonts sind als Fallback, Fixture, Docker-Abhaengigkeit und Empfehlung ausgeschlossen
7. **Keine Phantom-Konfiguration** — ERDA Emoji wird erst in `fonts.yml` eingetragen, wenn ein echter validierter Font-Artefaktpfad existiert

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
| `fonts.<KEY>.fontconfig_name` | string | – | `null` | 📝 | Informativ (fontconfig-Alias, nicht programmatisch genutzt) |
| `fonts.<KEY>.copyright` | string | – | `null` | ✅ | Copyright-Hinweis, wird in ATTRIBUTION.md gerendert |
| `fonts.<KEY>.usage_note` | string | – | `null` | ✅ | Nutzungshinweis, wird in ATTRIBUTION.md gerendert |

\* `paths` oder `download_url` — mindestens eines muss gesetzt sein.

## Aktuelle Fonts (fonts.yml v1.0.0)

| Key | Name | Version | Lizenz |
|-----|------|---------|--------|
| CJK | ERDA CC-BY CJK | 1.4.1 | CC BY 4.0 |
| INDIC | ERDA CC-BY Indic | 1.4.1 | CC BY 4.0 |
| ETHIOPIC | ERDA CC-BY Ethiopic | 1.4.1 | CC BY 4.0 |
| EMOJI | Twemoji Mozilla | 0.7.0 | CC BY 4.0 |
| MONO | DejaVu Sans Mono | 2.37 | Bitstream Vera + PD |
| SANS | DejaVu Sans | 2.37 | Bitstream Vera + PD |
| SERIF | DejaVu Serif | 2.37 | Bitstream Vera + PD |

## v2.10.0 Font-Familienentscheidung

Der historische Generatorpfad `.github/fonts/erda-ccby-cjk/` beschreibt die
aktuelle Fontfamilie nicht mehr praezise. Fuer v2.10.0 ist geplant, die Familie
unter `.github/fonts/erda-ccby-fonts/` zu fuehren und dort CJK, Indic,
Ethiopic, ERDA Emoji und weitere Sprachschrift-Basisssaetze zu buendeln.

Die Umbenennung ist eine Pfad- und Dokumentationsmigration. Sie darf nicht mit
versteckten Fontwechseln vermischt werden. `fonts.yml` wird erst angepasst,
wenn die neuen Pfade existieren und die TTFs validiert wurden.

ERDA Emoji wird als CC BY 4.0 lizenzierter Projektfont gebaut, wenn Twemoji
Mozilla die benoetigten Kunden-Emojis nicht abdeckt. Noto-Fonts bleiben fuer
diese Luecke ausgeschlossen.

## Implementierte Änderungen (v2.2.0)

- ✅ **`copyright`** → Wird vom Attribution-Generator gelesen und als eigene Spalte in ATTRIBUTION.md gerendert
- ✅ **`usage_note`** → Wird vom Attribution-Generator gelesen und in ATTRIBUTION.md Notes-Spalte gerendert
- 📝 **`fontconfig_name`** → Als informatives Metadatum deklariert (beschreibt den fontconfig-Alias)

## Versionshistorie

| Version | Datum | Änderung |
|---------|-------|----------|
| 1.2.0 | 2026-05-10 | CC-BY-only/no-Noto Fontpolitik und v2.10.0 ERDA-Fontfamilienentscheidung dokumentiert |
| 1.0.0 | 2026-01-08 | Initiales Schema mit 7 Fonts |
| 1.0.0 | 2026-02-08 | copyright/usage_note von Attribution-Generator gelesen (kein Schemaänderung) |

## Verwandte Dokumente

- [gitbook_worker/defaults/README.md](../../gitbook_worker/defaults/README.md) — Font-System Architektur
- [gitbook_worker/docs/attentions/lua-font-cache.md](../../gitbook_worker/docs/attentions/lua-font-cache.md) — LuaTeX Cache Guard
- AGENTS.md §14–17 — Font Management Policy
