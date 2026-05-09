---
version: 1.1.0
date: 2026-05-09
status: proposed
target_release: "v2.9.0 Qualitaetskompass"
history:
  - "1.1.0: 2026-05-09 - Anonymisiertes Kundenreview als verbindliche Abnahmeergaenzung integriert."
  - "1.0.0: 2026-05-09 - Pflichtenheft fuer redaktionelle Qualitaetsmetriken und Abnahmewerkzeuge erstellt."
---

# Pflichtenheft: Redaktionelle Qualitaetswerkzeuge

## Release-Arbeitstitel

Redaktioneller Arbeitstitel: **Qualitaetskompass**.

Der Name beschreibt den Zweck des Releases: GitBook Worker soll nicht nur PDFs
erzeugen, sondern Redaktionen eine nachvollziehbare Orientierung geben, ob ein
Dokument publikationsreif ist und welche Befunde vor einer Abnahme noch geklaert
werden muessen.

## Auftrag

Das Release stellt Werkzeuge bereit, die redaktionell wichtige Metriken aus den
Markdown-Quellen und aus den erzeugten PDFs ermitteln. Darauf aufbauend soll ein
Abnahmewerkzeug die Ergebnisse zu einem reviewbaren Entscheidungsdossier
verdichten.

Die Werkzeuge ersetzen keine menschliche Schlussredaktion. Sie schaffen eine
vollstaendige, reproduzierbare und auditierbare Grundlage fuer diese
Schlussredaktion.

## Kundenreview und Abnahmestatus

Das anonymisierte Kundenreview bewertet dieses Pflichtenheft als redaktionell
grundsaetzlich abnahmefaehig als Entwicklungsauftrag, wenn die
Kundenergaenzungen in den Lieferantenscope aufgenommen oder als verbindliche
Abnahmekriterien nachgezogen werden. Das Review ist als eigenes Evidenzdokument
abgelegt:
[editorial-quality-tools-customer-review.md](editorial-quality-tools-customer-review.md).

Die Ergaenzungen schaerfen vor allem sechs Bereiche:

- Report-Drift und Artefakt-Frische,
- wenigzeilige und leere PDF-Seiten,
- projekt- und locale-spezifische Frontmatter- und Uebersetzungsregeln,
- Aggregation der Tabellenstrategie-Reports,
- konfigurierbare Abnahmeprofile,
- manuelle Freigabe mit Restrisiko-Protokoll.

## Rollen

| Rolle | Bedarf |
|---|---|
| Redaktion | Schnell sehen, ob Struktur, Quellen, Tabellen, Bilder, Links und PDF-Satz abnahmefaehig sind. |
| Herausgeber | Einen belastbaren Abnahmenachweis mit klaren Restbefunden erhalten. |
| Technik | Metriken deterministisch in CI, Release-Runs und Kundensupport reproduzieren. |
| Kunde | Nachvollziehen, warum ein Dokument freigegeben, mit Warnung freigegeben oder zur Nacharbeit zurueckgestellt wurde. |

## Leitfragen

Die Qualitaetswerkzeuge muessen mindestens diese redaktionellen Fragen
beantworten:

- Ist der Markdown-Bestand vollstaendig, strukturell konsistent und buildbar?
- Sind Navigation, SUMMARY, Heading-Hierarchie und PDF-TOC deckungsgleich?
- Sind Quellen, Links, AI-Referenzen, Lizenzen und Attributionen pruefbar?
- Sind Tabellen, Codebloecke, lange Tokens, CJK/Hangul/Kana-Runs und Bilder im
  PDF layoutstabil?
- Sind alle benoetigten Fonts eingebettet und die relevanten Textbereiche aus
  dem PDF extrahierbar?
- Gibt es Hinweise auf leere Seiten, abgeschnittene Inhalte, fehlende Alttexte,
  nicht erklaerte TODOs oder nicht abgenommene Editor-Notizen?
- Welche Befunde blockieren die Abnahme, welche sind Warnungen, und welche sind
  rein informativ?

## Umfang

### Im Scope

- Markdown-Metriken fuer alle publizierten Inhalte und optional fuer nicht
  publizierte Inhalte.
- PDF-Metriken fuer erzeugte Artefakte.
- Abgleich zwischen Markdown-Struktur und PDF-Struktur.
- Aggregierter Abnahmereport in maschinenlesbarem JSON und menschenlesbarem
  Markdown.
- Severity-Modell fuer `info`, `warn`, `fail` und `blocked`.
- Exit-Codes fuer eindeutige Abnahmegruende.
- Integration vorhandener Qualitaetsbausteine wie Link-Audit,
  AI-Referenzcheck, Frontmatter-Checker, PDF-TOC-Extraktor,
  PDF-Validator und Tabellenlayout-Reports.

### Nicht im Scope

- Automatisches Umschreiben redaktioneller Inhalte.
- Inhaltliche Wahrheitspruefung ohne expliziten externen Provider.
- Vollautomatische Freigabe ohne menschliche Review-Entscheidung.
- Exakte TeX-Box-Messung als Ersatz fuer visuelle PDF-Abnahme.
- Netzwerkzugriffe als Standardverhalten. Externe Checks muessen explizit
  aktiviert werden.

## Funktionsanforderungen

### F1 Markdown-Metriken

Das Metriktool MUSS Markdown-Quellen und Publikationsmanifeste analysieren und
mindestens diese Metriken liefern:

| Kategorie | Metriken |
|---|---|
| Inventar | Anzahl Dateien, publishbare Dateien, nicht publishbare Dateien, verwaiste Dateien, fehlende README/SUMMARY-Signale. |
| Struktur | Heading-Tiefen, Heading-Spruenge, doppelte Titel, leere Abschnitte, zu tiefe Kapitel, Reihenfolge von Kapiteln und Anhaengen. |
| Frontmatter | Vorhandensein, SemVer, Pflichtfelder, Statuswerte, Datum, Sprach- und Lizenzsignale. |
| Text | Wort- und Zeichenzahlen, sehr lange Absaetze, sehr kurze Platzhalterabschnitte, TODO/FIXME/Review-Notizen. |
| Sprache | erkannte Sprache pro Datei, Mischsprachigkeit, Abweichung von `book.json` oder Manifest-Locale. |
| Links und Quellen | interne Links, externe Links, Anker, Zitationen, AI-Referenzen, DOI/URL-Signale, vorhandene Link-Audit-Ergebnisse. |
| Medien | Bildanzahl, fehlende Alttexte, fehlende Captions, Dateigroessen, SVG/PDF-Konvertierungsrisiko, Attribution-Signale. |
| Tabellen | Anzahl Tabellen, Zeilen/Spalten, lange Tokens, Script-Runs, Tabellenstrategie-Entscheidung, erwartete Layout-Risiken. |
| Code | Codefence-Anzahl, sehr lange Zeilen, Sprache von Codebloecken, Wrapping-Risiko. |

### F2 PDF-Metriken

Das Metriktool MUSS PDFs analysieren und mindestens diese Metriken liefern:

| Kategorie | Metriken |
|---|---|
| Dokument | Seitenzahl, Metadaten, Seitengroessen, Orientierung, wechselnde Papierformate. |
| Navigation | PDF-Outline, TOC-Eintraege, TOC-Tiefe, erwartete Beispielseiten, fehlende Bookmarks. |
| Text | extrahierbarer Text, leere oder textarme Seiten, auffaellige Ersatzglyphen, Sprachextraktionssignale. |
| Fonts | eingebettete Fonts, fehlende Fonts, bekannte Projektfonts, Emoji/CJK-Font-Signale. |
| Layout | breite Tabellen, Seiten mit Sondergeometrie, Kandidaten fuer Overflow-Sichtpruefung, Codeblock-Wrapping. |
| Bilder | Bildanzahl, Seiten mit hoher Bilddichte, sehr grosse oder sehr kleine Bilder, moegliche Aufloesungsrisiken. |
| Links | PDF-Linkannotationen, externe Ziele, interne Ziele, tote oder leere Linkziele soweit lokal pruefbar. |

### F3 Abgleich Markdown zu PDF

Das Werkzeug MUSS eine Quell-Ziel-Plausibilitaet herstellen:

- Markdown-Headings gegen PDF-TOC/Outline abgleichen.
- erwartete Titel und Schluesselseiten aus Sample Content pruefen.
- Sprach- und Versionssignale aus Manifest, Markdown und PDF vergleichen.
- Tabellenlayout-JSONL mit PDF-Seiten und Markdown-Quellen korrelieren.
- fehlende oder unerwartete PDF-Artefakte als Findings ausgeben.

### F4 Redaktionelle Abnahme

Das Abnahmewerkzeug MUSS aus Metriken eine Entscheidungsvorlage erzeugen:

- `passed`: keine blockierenden Findings.
- `passed_with_warnings`: nur Warnungen oder dokumentierte Restrisiken.
- `failed`: mindestens ein blockierender Befund.
- `blocked`: notwendige Artefakte fehlen oder konnten nicht gelesen werden.

Jedes Finding MUSS enthalten:

- stabile ID,
- Severity,
- Quelle oder PDF-Artefakt,
- betroffene Datei oder Seite,
- technische Evidenz,
- redaktionelle Bedeutung,
- vorgeschlagener Healing-Step.

### F5 Reports

Die Werkzeuge MUESSEN folgende Ausgabeformen unterstuetzen:

- JSON als primaeres Austauschformat.
- Markdown als redaktionelles Review-Dossier.
- kompakte Konsolenzusammenfassung fuer lokale Runs.
- optional CSV fuer tabellarische Metriken.

JSON-Reports MUESSEN versioniert sein und duerfen keine absoluten Pfade
erzwingen, wenn ein relativer Workspace-Pfad genuegt.

### F6 CLI und Workflow

Vorgeschlagene Einstiegspunkte:

```text
python -m gitbook_worker.tools.quality.editorial_metrics
python -m gitbook_worker.tools.quality.editorial_acceptance
```

`editorial_metrics` sammelt Fakten. `editorial_acceptance` bewertet Fakten
gegen ein Profil und erzeugt die Abnahmeentscheidung.

Beide CLIs MUESSEN `--help-exit-codes` oder eine gleichwertige Ausgabe
bereitstellen, sobald neue Exit-Codes entstehen.

### F7 Datenschutz und Reproduzierbarkeit

- Standardmaessig keine Netzwerkaufrufe.
- Keine Uebertragung von Kundentexten an externe Dienste ohne explizite Option.
- Reports duerfen sensible Inhalte nur als kurze Evidenzauszuege aufnehmen.
- Jeder Befund muss lokal reproduzierbar sein.

### F8 Report-Drift und Artefakt-Frische

Das Abnahmewerkzeug MUSS erkennen, ob Release-Dokumentation, Metrikreports und
Artefakte zueinander passen. Es muss Worker-Versionen, PDF-Frische,
Report-Frische, Seitenzahlen und bekannte Layoutbefunde im Dossier ausweisen.
Wenn Release-Dokumentation alte Worker-Versionen, alte Seitenzahlen oder alte
Layoutbefunde nennt, entsteht mindestens `warn`; im finalen Releaseprofil muss
dies als `fail` konfigurierbar sein.

### F9 Wenigzeiler- und Leerseiten-Metrik

Das PDF-Metriktool MUSS textarme Seiten strukturiert ausweisen. Mindestmetriken
sind `pages_total`, `low_text_pages_le_15`, `very_low_text_pages_le_5`,
`empty_text_pages` und `low_text_reason_hint`. Die Schwellen muessen
profilbezogen konfigurierbar sein.

### F10 Generische Frontmatter- und Uebersetzungsregeln

Das Frontmatter-Modul MUSS projektspezifische Pflichtfelder, verbotene Felder
und Uebersetzungsbeziehungen abbilden koennen, ohne an bestimmte Sprachen
gebunden zu sein. Ein Projekt kann z. B. `ja` als Source-Locale und `pl`, `hr`
oder `no` als Target-Locales definieren. Regeln werden nach Sprachrolle
(`source`, `target`) und konkreter Locale konfiguriert, nicht nach hart
verdrahteten Paaren wie Deutsch/Englisch. Typische Regeln sind: gemeinsame
`content_id`, ein konfigurierbares Locale-Feld wie `content_lang`, ein
repo-relativer Quellverweis fuer Target-Dateien, Statuswerte fuer
Uebersetzungsfreigabe und verbotene Keys wie `lang`, `language` oder
`lang-version`, wenn sie Pandoc/Babel- oder Fontfallback-Verhalten stoeren.

### F11 Scope-Klarheit und Publikationsprofil

Das Werkzeug MUSS zwischen publizierten, nicht publizierten und verwaisten
Dateien unterscheiden. `use_summary: true`, GitBook-SUMMARY-Reihenfolge,
`summary_appendices_last` und projektbezogene Ausschlussordner wie `desktop/`,
`tmp/`, `logs/`, `release-docs/` und `publish/` muessen profilierbar sein.

### F12 Tabellenstrategie als Befundblock

Tabellenlayout-JSONL-Reports duerfen nicht nur Artefakte bleiben. Das Dossier
MUSS Tabellen gesamt, Papierentscheidungen, Methoden, Fallbacks, Overrides,
nicht akzeptierte Kandidaten und Quellbezug aggregieren. Der Report soll auch
Trade-offs sichtbar machen, etwa wenn breitere Landscape-Seiten zwar
horizontal helfen, aber vertikal weniger Inhalt tragen.

### F13 PDF-Layout, Fonts und Textextraktion

PDF-Layout-Befunde MUESSEN quantifiziert und redaktionell einsortiert werden:
Seite, Art, Ueberstand in Punkten und Millimetern, gekuerzter Textauszug,
vermutete Ursache und Healing-Step. Font- und Textextraktions-Gates MUESSEN
Projektfonts, Emoji/CJK-Fontsignale, Ersatzglyphen und extrahierbare
CJK/Hangul/Kana-Stichproben pruefen.

### F14 Manuelle Freigabe, Restrisiko und Baselines

Das Dossier MUSS eine Vorlage fuer menschliche Freigabe enthalten, darf diese
aber nicht automatisch setzen. Findings brauchen stabile IDs und sollen in
einem Baseline-Vergleich als `new`, `existing`, `resolved` oder `changed`
klassifiziert werden koennen. Bewusst akzeptierte Befunde muessen mit Grund,
Rolle und optionalem Ablaufdatum dokumentierbar sein.

## Nichtfunktionale Anforderungen

- Deterministische Ergebnisse bei gleichem Input.
- Laufzeit auf Sample-Projekten unter CI-tauglichen Grenzen.
- Klare `info`/`warn`/`error`-Logs.
- Tests fuer Parser, Aggregation, Severity-Regeln und CLI-Exit-Codes.
- Pfadverarbeitung mit `pathlib.Path`.
- Keine harten Fontannahmen ausserhalb von `fonts.yml`.
- Neue Konfigurationsschluessel nur mit Konfigurationsreferenz, Status und
  Tests.

## Mindestabnahme fuer das Release

Das Release gilt redaktionell als abnahmefaehig, wenn:

- ein Sample-Projekt einen Markdown-Metrikreport erzeugt,
- ein Sample-PDF einen PDF-Metrikreport erzeugt,
- beide Reports in ein Markdown-Abnahmedossier aggregiert werden,
- mindestens ein absichtlich fehlerhafter Sample-Fall zu einem `failed`-Status
  fuehrt,
- mindestens ein Warnungsfall als `passed_with_warnings` erklaert wird,
- die vorhandenen PDF-Font-, TOC-, Link- und Tabellenlayoutsignale integriert
  sind,
- die Reports in Tests gegen stabile Snapshots oder strukturierte Assertions
  geprueft werden.

Zusaetzlich muessen die Szenarien aus dem anonymisierten Kundenreview abgedeckt
sein:

- sauberes Sample mit `passed`,
- Warnungs-Sample mit `passed_with_warnings`,
- Fehler-Sample mit `failed`,
- Blocked-Sample bei fehlenden Pflichtartefakten,
- Drift-Sample fuer alte Worker-Versionen oder Seitenzahlen,
- Translation-Sample fuer fehlenden Target-`source`/`status`, falsche
  `content_id` oder falsche Locale-Rolle,
- Table-Sample mit aggregiertem Tabellenstrategie-Report,
- Wenigzeiler-Sample mit reproduzierbar gezaehlten textarmen und leeren Seiten.

## Redaktionelles Zielbild

Ein Redakteur soll nach einem Build nicht mehr mehrere Einzeltools und Logs
zusammentragen muessen. Ein Befehl erzeugt ein Dossier mit Ampelstatus,
Messwerten, Befunden und Healing-Steps. Die Schlussentscheidung bleibt
menschlich, aber sie ist nicht mehr blind, verstreut oder nur in Terminalausgaben
versteckt.