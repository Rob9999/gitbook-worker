<!-- License: CC BY-SA 4.0 (Text); MIT (Code); CC BY 4.0/MIT (Fonts) -->
# Medien- & Lizenz-Attribution

**Lizenzmatrix (Kurz):** Texte = **CC BY-SA 4.0** · Code = **MIT** · Fonts (eigene) = **CC BY 4.0 / MIT** · Emojis = **Twemoji (CC BY 4.0)**.  
Details: siehe **Anhang J: Lizenz & Offenheit** sowie die LICENSE-Dateien.

## Überblick

| Kategorie | Asset | Urheber:in / Rechteinhaber:in | Lizenz | Quelle / Hinweis | Verwendung |
| --- | --- | --- | --- | --- | --- |
| Emoji | Twemoji Color Font v15.1.0 | Twitter, Inc. & Mitwirkende (via 13rac1/twemoji-color-font) | CC BY 4.0 | https://github.com/13rac1/twemoji-color-font/releases/tag/v15.1.0 | Farbige Emoji-Glyphen (SVG-in-OpenType) für PDF-Erzeugung und Dokumentation. |
| Font | ERDA CJK (eigene Entwicklung) | Robert Alexander Massinger / Projekt | CC BY 4.0 **oder** MIT | Quell- & TTF-Dateien im Repo (`.github/fonts/`) | CJK-Abdeckung für mehrsprachige Kapitel. |
| Font | DejaVu Serif/Sans/Mono v2.37 | © 2003 Bitstream, Inc. (Basis); DejaVu-Änderungen Public Domain | Bitstream Vera License | https://dejavu-fonts.github.io/ · Ubuntu fonts-dejavu-core | Haupttext (Serif), UI-Elemente (Sans), Code-Blöcke (Mono) im PDF. Font-Dateien dürfen nicht separat verkauft werden; Verwendung in Dokumenten unbeschränkt. |
| Logo | ERDA Buch Logo | Robert Alexander Massinger; Nutzungsrecht für ERDA Institut | CC BY 4.0 | Originaldateien im Projektarchiv | Cover, Kapitel-Header, Kommunikationsmaterialien. |

> Hinweise:
> - **Twemoji** erfordert Namensnennung; Anpassungen sind erlaubt.
> - **Eigen-Fonts** sind dual lizenziert (CC BY 4.0 / MIT). Keine OFL-/GPL-/proprietären Fonts im Repo.
> - Weitere Dritt-Assets bitte tabellarisch ergänzen (Quelle, Version, Lizenz) und Änderungen im Commit vermerken.

## Pflegehinweise

### ⚠️ Attribution-Hierarchie beachten

Diese Datei ist **Primärquelle** für alle Drittinhalte. Bei Änderungen an Fonts, Emojis oder Assets müssen **drei Ebenen** synchron gehalten werden:

1. **`ATTRIBUTION.md`** (diese Datei) — Tabelle erweitern
2. **`content/anhang-l-kolophon.md`** — Abschnitt L.2 Typografie aktualisieren
3. **`content/anhang-j-lizenz-and-offenheit.md`** — Lizenzmatrix prüfen (falls neue Lizenzkategorie)

### Checkliste bei neuen Assets

- [ ] Neue Zeile in obiger Tabelle mit allen Pflichtfeldern (Asset, Urheber, Lizenz, Quelle, Verwendung)
- [ ] Lizenz kompatibel mit `AGENTS.md` (keine OFL/GPL/UFL/proprietär)
- [ ] Version und Quelle exakt dokumentiert
- [ ] `content/anhang-l-kolophon.md` Abschnitt L.2 ergänzt
- [ ] `content/anhang-j-lizenz-and-offenheit.md` Lizenzmatrix (J.2) geprüft
- [ ] Commit mit `Signed-off-by:` (DCO)
- [ ] CI/CD-Compliance-Check erfolgreich

**Hinweis:** Lizenz- und Quellenangaben müssen mit den tatsächlichen Dateien im Repo übereinstimmen.
