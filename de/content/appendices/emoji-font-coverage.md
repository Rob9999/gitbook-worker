---
title: Appendix – Emoji- & Schriftabdeckung
description: Nachweis geeigneter Fonts für alle Schriftzeichen und farbigen Emojis im Beispielinhalt.
date: 2024-06-05
version: 1.0
history:
  - version: 1.0
    date: 2024-06-05
    changes: Erstfassung mit Font-Matrix und Testhinweisen.
---

# Appendix – Emoji- & Schriftabdeckung

Diese Übersicht fasst die Fonts zusammen, die sämtliche Schriftsysteme der Beispieltexte sowie alle Emoji-Sets abdecken. Alle Fonts erfüllen die Lizenzanforderungen aus `AGENTS.md` und der Datei `LICENSE-FONTS`.

## Font-Matrix

| Kategorie | Font | Lizenz | Quelle | Abdeckung |
| --- | --- | --- | --- | --- |
| Serif/Sans/Mono | DejaVu Serif · DejaVu Sans · DejaVu Sans Mono (v2.37) | Bitstream Vera License + Public-Domain-Erweiterungen | `gitbook_worker/defaults/fonts.yml` · `publish/ATTRIBUTION.md` | Latein, Griechisch, Kyrillisch sowie technische Symbole für Tabellen und Code |
| CJK & weitere BMP-Glyphen | ERDA CC-BY CJK | CC BY 4.0 **oder** MIT | `.github/fonts/erda-ccby-cjk` · `LICENSE-FONTS` | Chinesisch, Japanisch, Koreanisch und zusätzliche Unicode-Blöcke aus den mehrsprachigen Vorlagen |
| Farbige Emojis | Twemoji Color Font v15.1.0 | CC BY 4.0 | https://github.com/13rac1/twemoji-color-font/releases/tag/v15.1.0 · `publish/ATTRIBUTION.md` | Alle Emoji-Kategorien einschließlich Hauttöne, ZWJ-Sequenzen und Flaggen |

## Praktische Nutzung

1. **Textabschnitte** – Die DejaVu-Familie fungiert als Standard für Fließtext (`SERIF`), UI-Elemente (`SANS`) und Code (`MONO`). Dadurch sind sämtliche europäischen Sprachen der Datei `content/templates/multilingual-neutral-text.md` abgedeckt.
2. **CJK** – Sobald Kapitel oder Beispielseiten Schriftzeichen wie 日, 学 oder 정보 verwenden, sollte das Build-System die ERDA-CC-BY-CJK-Datei aus `.github/fonts/erda-ccby-cjk/true-type/` einbetten. Das geschieht automatisch über die `CJK`-Sektion in `gitbook_worker/defaults/fonts.yml`.
3. **Emoji-Farbe** – Für die neuen Emoji-Beispielseiten wird der Twemoji-Color-Font eingebunden. Die Datei `gitbook_worker/defaults/fonts.yml` verweist auf die Download-URL, sodass CI-Builds das TTF automatisiert nachladen können.

## Testhinweise

- Führe `pytest -k emoji` aus, um sicherzustellen, dass das Font-Scanning keine unbekannten Schriften meldet.
- Prüfe PDF-Exports mit mindestens einer Seite aus jeder Emoji-Kategorie (Smileys, Natur, Aktivitäten, Objekte), um Twemoji gegen CJK-Text zu testen.
- Dokumentiere neue Fonts zusätzlich in `publish/ATTRIBUTION.md` und `LICENSE-FONTS`, falls weitere Schriftsysteme hinzukommen.
