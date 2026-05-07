---
title: ERDA CC-BY CJK glyph coverage gap
version: 0.2.0
date: 2026-05-07
history:
  - version: 0.2.0
    date: 2026-05-07
    description: Attached the v2.5.0 staged fallback coverage implementation and TTF stats gate.
  - version: 0.1.0
    date: 2025-12-25
    description: Captured missing-glyph findings after LuaLaTeX fallback tests.
---

# Kontext
- LuaLaTeX (LuaHBTeX TL2025) mit `Renderer=HarfBuzz` und `luaotfload.add_fallback(erda_twemoji)` nutzt DejaVu als Primärschrift, TwemojiMozilla für Emoji und die Datei `erda-ccby-cjk-test.ttf` als CJK-Fallback.
- Trotz aktivem Fallback werden weiterhin `Missing character`-Zeilen für Chinesisch/Japanisch/Koreanisch, Arabisch, Devanagari, Äthiopisch/Inuktitut geloggt; die PDF-Ausgabe enthält entsprechend fehlende Glyphen.
- Twemoji deckt nur Emoji ab; der bereitgestellte ERDA CC-BY CJK-Build scheint nur Teilmengen oder gar keine dieser Codepoints zu enthalten.

# Beobachtungen
- Logauszug (27-seitiger Lauf): `fallback=erda_twemoji` wird registriert, Fonts geladen: `TwemojiMozilla.t t f`, `erda-ccby-cjk-test.ttf`, DejaVu Serif/Sans/Mono.
- Fehlende Glyphen betreffen u.a. U+65E5, U+5B66, U+BCF4, U+0627 … U+0651, zahlreiche CJK und RTL/Indic/Abugida-Bereiche.
- Kein Hinweis auf NOTO-Fallback (bewusst vermieden); einzig ERDA + Twemoji stehen in der Kette.

# Risiken
- Mehrsprachige Beispiele im Buch bleiben unbrauchbar (leere Kästchen), CI/PDF-Tests können verdeckte Fehler übersehen.
- Ohne vollwertige Ersatzschrift drohen Workarounds mit ungeprüften Fonts oder Rückfall auf Noto (widerspricht Vorgaben).

# Nächste Schritte
- v2.5.0 setzt gestufte Fallback-Coverage im ERDA-Generator um:
  `erda-ccby-cjk.ttf` erhaelt Release-Ziele fuer mindestens 3000 Han- und
  3000 Hangul-Glyphen sowie vollstaendige Kana-Blockabdeckung.
- `erda-ccby-indic.ttf` und `erda-ccby-ethiopic.ttf` werden nicht kuenstlich
  auf 3000 behauptete Glyphen gebracht. Stattdessen zaehlen die Release-Ziele
  alle zugeordneten Codepoints der unterstuetzten Devanagari- bzw. Ethiopic-
  Unicode-Bloecke; diese Bloecke enthalten weniger als 3000 Zeichen.
- `font_cli.py stats --fail-on-targets` prueft fertige TTFs ueber
  `fontTools.ttLib.TTFont` und trennt damit Sample-Textlaenge von echter
  Font-Coverage.
- Dokumentierte Coverage-Matrix: [../architecture/erda-font-coverage-matrix.md](../architecture/erda-font-coverage-matrix.md).

# Rest-Risiko

Die v2.5.0-Fallbackglyphen sind sichtbar, lizenziert und maschinell zaehlbar,
aber noch kein vollwertiger Satzfont. Fuer echte Schriftqualitaet bleiben
separates Glyphdesign, Metriken, Hinting, Kerning und shaping-spezifische
Regressionen erforderlich.
