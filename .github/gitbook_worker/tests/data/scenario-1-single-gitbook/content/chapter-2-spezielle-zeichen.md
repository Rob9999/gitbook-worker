# Kapitel 2: Spezielle Zeichen & Tests

Dieses Kapitel testet LaTeX-Sonderzeichen und Emoji-Support.

## 2.1 LaTeX-Sonderzeichen im Titel & Text

Folgende Zeichen müssen korrekt escaped werden:
- Ampersand: A & B (sollte funktionieren)
- Prozent: 100% Erfolg  
- Dollar: \$100 (ohne Math-Mode)
- Unterstrich: test\_variable
- Hash: \#hashtag
- Geschweifte Klammern: \{test\}
- Backslash: `C:\Pfad\Test` C:\\Pfad\\Test und (in Code, da Backslash speziell)

## 2.2 Emoji-Tests

Verschiedene Emojis sollten korrekt dargestellt werden:

- 😀 Lachen
- 🎉 Party
- ✅ Erledigt
- 🇩🇪 Deutsche Flagge
- 🇪🇺 EU-Flagge

## 2.3 CJK-Zeichen

Test für CJK-Font-Fallback:

- 中文 (Chinesisch)
- 日本語 (Japanisch)
- 한국어 (Koreanisch)

## 2.4 Komplexe Kombination

Ein Satz mit allem: Die EU 🇪🇺 erreichte 2025 100% Erfolg bei A & B mit $1000 Budget! 中文支持 ✅
