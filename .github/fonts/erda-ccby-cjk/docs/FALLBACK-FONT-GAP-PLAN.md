---
version: 0.1.0
date: 2025-11-19
history:
  - 2025-11-19: Initial fallback-font gap analysis plus CC BY 4.0 remediation plan.
---

# Mainfontfallback Coverage Plan (CC BY 4.0)

## Ausgangslage
- Pandoc meldet fehlende Glyphen für **vereinfachtes Chinesisch** (z. B. 观, 团, 录, 据), **Japanisch** (観, 測, 穏, 記, 録, 週, 較), **Koreanisch** (관, 측, 팀, 정, 값, 비, 교, 월, 했), **Devanagari/Hindi** (ाः, े, ँ, औ, ु, ो, ।) und **Äthiopisch/Ge’ez** (ቡ, ድ, ኑ, በ, መ, ጣ, እ, ። usw.).
- Der aktuelle Fallback (`ERDA CC-BY CJK`) deckt Trad./JP/Hangul gut ab, lässt aber obige Codepoints und nicht-CJK-Skripte offen.
- Externe Vollabdeckungs-Fonts wie Noto/Source Han sind **SIL OFL**, nicht CC BY 4.0, daher nicht geeignet als direkte mainfontfallback-Lösung.

## Lizenzanforderungen
- mainfontfallback muss **CC BY 4.0** bleiben, damit PDF-Embedding und Redistribution der Builds lizenzrein ist.
- Emoji bleiben über `Twemoji Color Font` (CC BY 4.0) abgedeckt; der Fokus liegt auf Text-Skripten.

## Vorschlag (CC BY 4.0 Eigen-Fonts)
1. **ERDA CC-BY CJK v1.2**
   - Neue Glyphen für die vereinfachten chinesischen/japanischen Warnzeichen ergänzen (`generator/hanzi.py` + `dataset/chinese.md`, `dataset/japanese.md`).
   - Hangul-Silben werden schon algorithmisch erzeugt; prüfen, ob die betroffenen Silben als Teststrings aufgenommen werden müssen (`dataset/korean.md`).

2. **ERDA CC-BY Indic (Hindi) v1.0**
   - Separates 8×8-Monospace-Font-File mit kompletter Devanagari-Basis plus fehlende Vokalzeichen (े, ा, ँ, औ, ु, ो, ।) ergänzen; Modul analog zu `generator/devanagari.py`, Export nach `true-type/erda-ccby-indic.ttf`.
   - Dataset-Erweiterung `dataset/hindi.md` um die Warnzeichen, plus Coverage-Test via `tests/check_coverage.py`.

3. **ERDA CC-BY Ethiopic v1.0 (Mini-Fallback)**
   - Neues Glyph-Modul `generator/ethiopic.py` für die im Log genannten Zeichen (ቡ, ድ, ኑ, በ, መ, ጣ, እ, ። usw.) im selben 8×8-Stil.
   - Kleines Dataset `dataset/ethiopic.md` für Regressionstests und Sichtkontrolle.

4. **Mainfontfallback-Kette**
   - Nach Build: `mainfontfallback="ERDA CC-BY CJK:mode=harf; ERDA CC-BY Indic:mode=harf; ERDA CC-BY Ethiopic:mode=harf"` als Standard setzen (Pandoc >=3.6 verlangt HarfBuzz-Mode).
   - `gitbook_worker/defaults/fonts.yml` um die neuen Fonts ergänzen (jeweils Pfad unter `.github/fonts/erda-ccby-cjk/true-type/`).

## Umsetzungsschritte
- **Glyph-Erstellung:** Bitmap-Vorlagen in `generator/hanzi.py` (CJK), `generator/devanagari.py` (Kopie als Basis für Indic), neues `generator/ethiopic.py` erstellen.
- **Index & Build:** `generator/character_index.py` und `generator/build_ccby_cjk_font.py` um neue Module registrieren (ggf. separate Build-Skripte für Indic/Ethiopic anlegen, falls Dateiname getrennt bleiben soll).
- **Datasets/Tests:** Jeweils neue Beispieldateien in `dataset/` hinzufügen und `tests/check_coverage.py`/`tests/test-font-version.html` erweitern, damit fehlende Zeichen als Regressionstest abgedeckt werden.
- **Dokumentation:** README/Changelog im Font-Ordner um neue Varianten erweitern; Lizenzhinweise in `LICENSE-FONTS` ergänzen.
- **Distribution:** Nach Build `true-type/erda-ccby-*.ttf` in `gitbook_worker/defaults/fonts.yml` eintragen und Publish-Pipeline (`publisher.py`) validieren.

## Erwartetes Ergebnis
- Keine Pandoc-Warnungen mehr für CJK/Hindi/Ethiopic bei PDF-Builds.
- mainfontfallback bleibt vollständig **CC BY 4.0** (Eigen-Glyphen), wodurch Wiederverwendung in öffentlichen Artefakten lizenziert bleibt.
- Klare Trennung pro Skript erleichtert zukünftige Releases und optionale Deaktivierung je nach Buchsprache.
