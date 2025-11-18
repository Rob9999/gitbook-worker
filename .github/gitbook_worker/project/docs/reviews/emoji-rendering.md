<!-- License: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) -->
# Emoji-Rendering ohne System-Fallbacks

Dieses Dokument erläutert den neuen Workflow zur Inline-Darstellung von Emojis im ERDA-Buch. Ziel ist eine reproduzierbare, farbige Ausgabe ohne externe System-Fonts.

## Überblick

1. **Inventur** – `python -m tools.emoji.scan_emojis` liest sämtliche Markdown-Dateien (`content/**`, `docs/**`) ein und erzeugt `build/emoji-report.json`. Neben dem Unicode-String werden Codepoints, CLDR-Namen und Häufigkeiten ermittelt. Parallel protokolliert `python -m tools.emoji.scan_fonts` alle deklarierten Schriften in `build/font-report.json`.
2. **Harness** – `harness/emoji-harness.md` fungiert als Vorlage. Das Shell-Skript `.github/gitbook_worker/tools/run-emoji-harness.sh` füllt die Platzhalter mit den aktuellen Daten, generiert HTML (`pandoc`) und versieht es anschließend mit Inline-Emojis.
3. **Inlining** – `python -m tools.emoji.inline_emojis` ersetzt jedes Emoji durch ein `<span class="emoji">…</span>` mit eingebettetem SVG/PNG. Primärquelle ist [Twemoji (CC BY 4.0)](https://twemoji.twitter.com/). Für Lücken dient [OpenMoji Black (CC BY-SA 4.0)](https://openmoji.org/), wodurch das Rendering mindestens monochrom bleibt.
4. **PDF-Erzeugung** – `.github/gitbook_worker/tools/html_to_pdf.js` ruft Playwright/Chromium auf und schreibt PDFs mit `printBackground: true`. Der Harness sowie das komplette Buch werden auf diese Weise transformiert.
5. **Gates & Coverage** – Die Inlining-Quote landet in `build/emoji-inline-coverage.json` und muss ≥ 0,90 sein. Unit-Tests (`pytest --cov`) überwachen den Python-Anteil. `run-emoji-harness.sh` prüft außerdem: keine zusätzlichen System-Emoji-Fonts im Repo/Container, nur CC BY-/CC BY-SA-lizenzierte Assets, konsistente Tests.

## Share-Alike-Hinweise

Twemoji-Inhalte stehen unter **CC BY 4.0** – Attribution genügt (siehe `ATTRIBUTION.md`). OpenMoji Black benötigt **CC BY-SA 4.0** für abgeleitete Asset-Sammlungen. Da wir lediglich fallbackweise einzelne SVGs einbetten, bleibt die Share-Alike-Pflicht auf diese Snippets beschränkt.

## Feature-Flag

Das Environment-Flag `EMOJI_INLINING=off` deaktiviert sämtliche Ersetzungen. Dadurch lässt sich im Fehlerfall rasch zum monochromen Standard zurückkehren.

Weitere Details zu Dateipfaden und Ausführung liefert das Shell-Skript `.github/gitbook_worker/tools/run-emoji-harness.sh`.
