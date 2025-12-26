---
title: ERDA CC-BY CJK glyph coverage gap
version: 0.1.0
date: 2025-12-25
history:
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
- Beschaffen/prüfen einer ERDA CC-BY CJK-Version mit voller CJK/RTL/Indic/Abugida-Abdeckung **oder** zugelassene Zusatz-Fallbacks (nicht Noto) definieren.
- Nach Austausch: `fonts.yml` und LaTeX-Fallbackkette auf neue Datei verweisen; kurze HarfBuzz-Regressionstests (`lualatex` smoke) ergänzen.
- Dokumentierte Coverage-Matrix (Unicode-Blöcke, Lizenz) in die Schrift-Dokumentation aufnehmen und auf diese Backlog-Notiz verlinken.
