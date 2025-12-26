---
title: ERDA CC-BY CJK Dokumentation & Coverage-Backlog
version: 0.1.0
date: 2025-12-25
history:
  - version: 0.1.0
    date: 2025-12-25
    description: Erstfassung der Doku-Lücken zu ERDA CC-BY CJK und Fallbacknutzung.
---

# Ziel
Die Dokumentation der ERDA CC-BY CJK-Schrift so erweitern, dass Lizenz, Beschaffungsweg, Unicode-Abdeckung und Einsatz in HarfBuzz/LuaLaTeX klar und reproduzierbar sind.

# Offene Punkte
- **Coverage-Matrix**: Welche Unicode-Blöcke deckt der bereitgestellte `erda-ccby-cjk-test.ttf` tatsächlich ab (CJK, Hangul, Arabisch, Devanagari, Ethiopic, Canadian Aboriginal Syllabics)? Fehlt vieles → neue Version beschaffen oder Alternativ-Fallback definieren.
- **Lizenznachweis**: Lizenztext/URL und Herkunft der Binärdatei in `fonts.yml`/Dokumentation explizit benennen; Attribution in `publish/ATTRIBUTION.md` automatisieren.
- **Build-Integration**: Beschreiben, wie `fonts.yml`-Einträge von `Dockerfile.dynamic` gezogen und von LuaLaTeX/HarfBuzz genutzt werden (OSFONTDIR, FONTCONFIG_FILE, luaotfload cache).
- **Test-Snippets**: Kurze PDF-Snippets für jede betroffene Schriftgruppe hinterlegen, um fehlende Glyphen schneller zu erkennen.
- **Known-Limitations Abschnitt**: Klar festhalten, welche Skripte aktuell nicht unterstützt sind, bis ein vollständiger Font vorliegt.

# Maßnahmenvorschläge
- Coverage-Scan mit `luaotfload-tool --inspect` oder `pyftsubset`/`ttx` fahren und Ergebnis tabellarisch dokumentieren.
- Falls Coverage unvollständig: neues, lizenziertes Font-File beschaffen (kein Noto), Prüfsumme/Version in docs festhalten und `fonts-storage` aktualisieren.
- README/Howto für ERDA-Fonts ergänzen (Downloadpfad, Konfiguration, Testaufruf `lualatex -halt-on-error the-erda-book-nohyper-nolua.tex`).
- Regressionstest (Smoke) in CI (PyTest oder minimaler LaTeX-Lauf) ergänzen, der auf fehlende Glyphen prüft und den richtigen Fallback meldet.
