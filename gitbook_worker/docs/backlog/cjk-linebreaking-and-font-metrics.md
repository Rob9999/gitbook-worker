---
title: CJK linebreaking and ERDA font metrics
version: 0.1.0
date: 2026-05-06
history:
  - version: 0.2.0
    date: 2026-05-06
    description: Switched implemented mitigation from LuaTeX-ja JFont setup to LaTeX-only CJK breakpoints via Pandoc Lua filter.
  - version: 0.1.0
    date: 2026-05-06
    description: Captured customer finding for Traditional Chinese PDF overflow and first LuaTeX-ja mitigation slice.
---

# Kontext

Ein Kunden-PDF zeigt in einem Traditional-Chinese-Beispielabschnitt einen
ueberbreiten Lauf nach einer lateinischen Insel wie `AI`. Der Markdown-Quelltext
ist korrekt; das Problem liegt im PDF-Satz: westliche Token wie `AI` und
`CC BY-SA 4.0` haben normale Breakpoints, der anschliessende chinesische
Textlauf jedoch nicht ausreichend. Der Originaltext wird hier bewusst nicht
abgelegt; der folgende anonymisierte Repro-Text bildet nur die typografische
Struktur nach.

Anonymisierter Repro-Text:

```text
繁體中文（排版測試）
這是一段匿名化的排版測試文字，用來模擬連續中文、標點符號與拉丁字串 AI 之間的換行行為。測試段落包含較長的中文片語、全形括號（示例說明）、頓號、逗號與句號，以觀察 PDF 是否在適當位置換行。後續文字再次加入 CC BY-SA 4.0 作為拉丁字串示例，並延續一段中文內容以檢查行尾、字距與邊界。
```

# Befund

- LuaLaTeX nutzt aktuell `luaotfload`-Fallbacks, damit fehlende Glyphen aus
  konfigurierten Fonts nachgeladen werden.
- Das allein macht den Absatz aber noch nicht CJK-satzfaehig. Ohne CJK-aware
  Linebreaking kann TeX lange Han-Zeichenlaeufe als zu breite HBox setzen.
- Der ERDA-CJK-Font ist zusaetzlich ein minimalistischer Fallback mit begrenzter
  typografischer Metrikqualitaet. Das erklaert Pixeligkeit oder ungewohnte
  Glyphenform, selbst wenn keine Glyphen fehlen.

# Umgesetzter P0-Slice

- `cjk-linebreak.lua` fuegt fuer LaTeX-Ausgabe Breakpoints nach CJK-Zeichen ein.
- Die Fontbehandlung bleibt bei den vorhandenen, konfigurierten
  `luaotfload`-Fallbacks aus `fonts.yml`. Es wird kein unkonfigurierter
  Systemfont und kein instabiler `\setmainjfont`-Pfad verwendet.
- `Dockerfile.dynamic` braucht dadurch kein zusaetzliches LuaTeX-ja-Paket fuer
  diesen P0-Slice.
- Regressionstests pruefen Default-Filter, Header-Erzeugung ohne LuaTeX-ja-JFont
  und Dockerfile-Abhaengigkeit.

# Offene Punkte

- Visueller Kunden-PDF-Abgleich mit echten Taiwan-/CJK-Lizenzabschnitten.
- Vollwertige ERDA-CJK-Fontmetriken bzw. ein rechtssicherer, vollstaendiger
  CJK-Satzfont bleiben ein separates Font-Backlog-Thema.
- Pruefen, ob ERDA-Fonts als gestufte Coverage-Fonts gepflegt werden sollen:
  z. B. 500, 1.000, 3.000 oder 5.000 haeufige Glyphen pro Schriftfamilie plus
  projektspezifische Pflichtzeichen. Das ist fuer Sample-/Fallback-Fonts
  machbar und ueblich, ersetzt aber fuer Chinesisch/Japanisch/Koreanisch keinen
  vollwertigen Satzfont mit sauberem Kerning, Metriken, Hinting und
  Linebreaking-Testabdeckung.
- Overfull-HBox-Loggate fuer CJK-Abschnitte pruefen, sobald eine stabile
  Baseline existiert.
