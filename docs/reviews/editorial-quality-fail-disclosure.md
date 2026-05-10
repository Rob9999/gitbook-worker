---
version: 1.1.0
date: 2026-05-10
status: delivery-evidence
target_release: "v2.9.0 Qualitaetskompass"
history:
   - "1.1.0: 2026-05-10 - Fachentscheidung fuer ERDA Emoji, ERDA-Sprachfonts v2.10.0 und no-Noto Fontpolitik ergaenzt."
   - "1.0.0: 2026-05-10 - Fail-Befunde des konfigurierten release-Lieferlaufs offengelegt."
---

# Editorial Quality Fail Disclosure

Diese Offenlegung schliesst Lieferpunkt 4. Sie beschreibt die harten Befunde,
die den konfigurierten `release`-Lauf bewusst auf `failed` setzen.

## Befunde

| Dossier | Finding-ID | Regel | Artefakt | Ort | Evidenz |
|---|---|---|---|---|---|
| `de-release` | `pdf.text.replacement_glyph:9aa0b115faea` | `pdf.text.replacement_glyph` | `de/publish/das-sample-buch.pdf` | text extraction | 5131 replacement glyph signal(s) |
| `en-release` | `pdf.text.replacement_glyph:670b506aded7` | `pdf.text.replacement_glyph` | `en/publish/the-sample-book.pdf` | text extraction | 5166 replacement glyph signal(s) |
| `project-release` | beide obigen Findings | `pdf.text.replacement_glyph` | beide PDFs | text extraction | 10297 replacement glyph signal(s) gesamt |

## Bedeutung

`pdf.text.replacement_glyph` meldet moegliche fehlende Glyphen oder
Fontfallback-Probleme im extrahierbaren PDF-Text. Das ist releasekritisch,
weil die PDF-Datei zwar gebaut ist, aber Zeichen in der Darstellung oder im
Textlayer falsch, leer oder nicht reproduzierbar sein koennen.

Der aktuelle Collector kann dieses Signal nicht automatisch auf eine einzelne
Seite begrenzen, weil der Befund aus der Text-Extraktion aggregiert wird. Diese
Grenze ist selbst Teil der Offenlegung: Vor fachlicher Freigabe braucht es eine
visuelle Gegenpruefung der betroffenen PDFs, insbesondere der mehrsprachigen
Script-Samples und Emoji-/Font-Coverage-Seiten.

## Severity-Regel

| Signal | Severity | Gate-Empfehlung |
|---|---|---|
| replacement glyph signal(s) in PDF text extraction | `fail` | Release blockierend, bis Fontkonfiguration, LaTeX-Logs und visuelle Stichprobe geklaert sind. |

## Fachentscheidung vom 2026-05-10

Die bekannten Glyphen-/Font-Fails werden nicht als stilles Restrisiko
akzeptiert. Sie werden als Font-Coverage-Healing fuer v2.10.0 geplant.

Verbindliche Leitplanken:

1. Ausser der bestehenden DejaVu-Familie werden nur CC BY 4.0 lizenzierte
   Projektfonts und Emoji-Fonts verwendet.
2. Noto-Fonts sind ausgeschlossen, auch als Zwischenloesung oder Testfixture.
3. Wenn Twemoji Mozilla benoetigte Kunden-Emojis nicht abdeckt, wird ein ERDA
   Emoji Font unter CC BY 4.0 gebaut und erst nach TTF-/PDF-Validierung in
   `gitbook_worker/defaults/fonts.yml` konfiguriert.
4. Fehlende Sprachschrift-Coverage wird in v2.10.0 mit ERDA-generierten
   Basissatz-Fonts je Sprachschrift adressiert. Ziel ist bis zu 5000 Glyphen je
   Schrift, sofern der deklarierte Unicode-/Script-Scope so gross ist; kleinere
   Bloecke gelten als vollstaendig, wenn alle zugeordneten Codepoints im Scope
   abgedeckt sind.
5. Der historisch benannte Generatorpfad `.github/fonts/erda-ccby-cjk/` soll
   in einem separaten Migrationsschnitt zu `.github/fonts/erda-ccby-fonts/`
   werden, weil die Fontfamilie nicht mehr nur CJK umfasst.

## Healing-Steps

1. LaTeX- und Build-Logs auf Missing-Glyph-, `.notdef`- oder Fontfallback-
   Hinweise pruefen.
2. `gitbook_worker/defaults/fonts.yml` gegen die tatsaechlich benoetigten
   Schriftfamilien und Lizenzangaben pruefen.
3. LuaTeX-Fontcache aktualisieren, falls konfigurierte Fonts fehlen.
4. Betroffene PDFs visuell an Script-Sample-, Emoji- und Font-Coverage-Seiten
   pruefen.
5. Erst nach technischer und visueller Klaerung als behoben oder als explizit
   akzeptiertes Restrisiko dokumentieren.

6. Fuer v2.10.0 den ERDA-Fontfamilienplan in
   [gitbook_worker/docs/backlog/erda-ccby-fonts-v2-10.md](../../gitbook_worker/docs/backlog/erda-ccby-fonts-v2-10.md)
   umsetzen und danach DE/EN/Projekt-Dossiers erneut erzeugen.

## Abnahmeaussage

Solange diese Fails bestehen, ist die technische Artefaktlieferung vollstaendig,
aber die fachliche Releasefreigabe bleibt offen. Eine Nachlieferung ist nur dann
sauber abgrenzbar, wenn Kundensamples oder Kundenumgebung neue Fontfaelle
sichtbar machen; die hier bereits bekannten Fails gehoeren vor Freigabe in die
interne Klaerung oder in ein ausdrueckliches Restrisiko-Register.
