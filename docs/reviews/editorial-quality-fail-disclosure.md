---
version: 1.0.0
date: 2026-05-10
status: delivery-evidence
target_release: "v2.9.0 Qualitaetskompass"
history:
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

## Abnahmeaussage

Solange diese Fails bestehen, ist die technische Artefaktlieferung vollstaendig,
aber die fachliche Releasefreigabe bleibt offen. Eine Nachlieferung ist nur dann
sauber abgrenzbar, wenn Kundensamples oder Kundenumgebung neue Fontfaelle
sichtbar machen; die hier bereits bekannten Fails gehoeren vor Freigabe in die
interne Klaerung oder in ein ausdrueckliches Restrisiko-Register.