---
version: 1.3.0
date: 2026-05-10
status: pre-delivery-review
history:
  - "1.3.0: 2026-05-10 - Konfigurierten release-Lieferlauf und Nachweisartefakte aufgenommen."
  - "1.2.0: 2026-05-10 - Lieferumfang auf ein Dossier pro buildbarer lokaler Language-Version plus Gesamtprojekt-Dossier praezisiert."
  - "1.1.0: 2026-05-10 - Vorlieferungsfeedback aufgenommen und Abnahmeaussage an fehlende Artefaktnachweise gebunden."
  - "1.0.0: 2026-05-10 - Redakteursreport zu erfuellten Pflichtenheftpunkten und offenen redaktionellen Entscheidungen erstellt."
---

# Redakteursreport: v2.9.0 Qualitaetskompass

Dieser Report fasst fuer die Kundenredaktion zusammen, welche Punkte des
Pflichtenhefts fuer die redaktionellen Qualitaetswerkzeuge umgesetzt sind und
welche Entscheidungen noch fachlich bewertet werden muessen.

Stand: 2026-05-10  
Quelle: `gitbook_worker/docs/backlog/editorial-quality-tools.md`  
Nachweisartefakte: `logs/quality/de-release-editorial-acceptance.md`,
`logs/quality/en-release-editorial-acceptance.md`,
`logs/quality/project-release-editorial-acceptance.md`

## Kurzfazit

Aus Umsetzungssicht sind die Muss-, Soll- und Kann-Anforderungen des
Pflichtenhefts im Werkzeugdesign umgesetzt und das vollstaendige
Artefaktpaket wurde reproduzierbar erzeugt: ein Dossier pro konfigurierter
buildbarer lokaler Content-/Language-Version plus ein
`project-release`-Gesamtprojekt-Dossier.

Die technische Lieferung darf zur Pruefung angenommen werden, aber nur mit
Bedingungen. Eine fachliche Kundenfreigabe erfolgt erst nach Sichtung der realen
Artefakte, Reproduktionslauf im ERDA-Repo und redaktioneller Entscheidung ueber
Warnungs-, Gate- und Restrisiko-Policy.

Die Definition of Done ist formal vorbereitet. Der lokale EN-Nachweislauf
erzeugt ein Abnahmedossier und zeigt bewusst reale Befunde statt eines
scheinbar gruenen Ergebnisses.

Der aktuelle konfigurierte Nachweislauf endet bewusst mit Status `failed`:
`de-release` meldet `1 fail`, `195 warn`, `27 info`; `en-release` meldet
`1 fail`, `172 warn`, `18 info`; `project-release` meldet `2 fail`, `546 warn`,
`30 info`. Das ist kein Implementierungsdefekt des Qualitaetswerkzeugs,
sondern ein ehrliches Ergebnis der geprueften Inhalte. Die offenen Punkte sind
redaktionelle Bewertungsentscheidungen und Font-/Glyphen-Healing.

## Lieferreife nach Vorabfeedback

| Bereich | Bewertung | Einordnung |
|---|---|---|
| Pflichtenheft-Abdeckung nach Bericht | gruen-gelb | Die Punkte sind im Bericht adressiert, brauchen aber eine Anforderungsmatrix mit Test- und Artefaktbelegen. |
| Nachweisbarkeit vor Lieferung | gruen-gelb | Alle buildbaren lokalen Content-/Language-Versionen, Gesamtprojekt, SARIF, HTML, Trend und Snapshot-Index sind als Lieferpaket belegt. |
| Werkzeug-Design | gruen | Architektur, Profile, Formate, Baseline und Dossierlogik passen zum Zielbild. |
| Kunden-/Release-Abnahme | rot | Die Abnahme haengt an realen Artefakten, ERDA-Reproduktionslauf und redaktioneller Policy. |
| Lieferfreigabe zum Paketuebergang | ja, mit Bedingungen | Uebergabe zur technischen Pruefung ist vertretbar; fachliche Freigabe erst nach Abnahme. |

Der Report ist damit ein technischer Lieferstatus mit offenen Fails, nicht eine
finale Kundenfreigabe.

## Aktueller Lieferlauf

| Prefix | Ebene | Status | Findings |
|---|---|---|---|
| `de-release` | deutsche lokale Content-Version | `failed` | 1 fail, 195 warn, 27 info |
| `en-release` | englische lokale Content-Version | `failed` | 1 fail, 172 warn, 18 info |
| `project-release` | Gesamtprojekt `de` + `en` | `failed` | 2 fail, 546 warn, 30 info |

Die Liefernachweise liegen hier:

- [editorial-quality-delivery-evidence.md](editorial-quality-delivery-evidence.md)
- [editorial-quality-requirements-matrix.md](editorial-quality-requirements-matrix.md)
- [editorial-quality-warning-groups.md](editorial-quality-warning-groups.md)
- [editorial-quality-fail-disclosure.md](editorial-quality-fail-disclosure.md)
- [editorial-quality-exit-code-evidence.md](editorial-quality-exit-code-evidence.md)
- [editorial-quality-evidence-privacy.md](editorial-quality-evidence-privacy.md)

## Erfuellt vom Pflichtenheft

| Bereich | Status | Ergebnis |
|---|---:|---|
| Muss-Anforderungen M1 bis M3 | erfuellt | Markdown-Metriken, PDF-Metriken und Markdown-PDF-Abgleich sind umgesetzt. |
| Erweiterte Muss-Schnitte | erfuellt | Publish-Scope, Tabellenstrategie, Release-Doku-Drift, Baseline-Vergleich und Restrisiko-Register sind im Dossier abbildbar. |
| Soll-Anforderungen S1 bis S5 | erfuellt | Profile, Schwellen, JSON/Markdown/CSV/Konsole, Orchestrator-Integration, Samples und Seitenzahl-Zielkorridore sind vorhanden. |
| Kann-Anforderungen | erfuellt | Statischer HTML-Report, High-Risk-Snapshot-Index, Baseline-Vergleich, Trend-JSONL und SARIF-Ausgabe sind umgesetzt. |
| Definition of Done | erfuellt | Doku, Tests, Exit-Codes, Konfigurationsreferenz und lokaler EN-Dossier-Nachweis sind vorhanden. |

## Bereits verfuegbare Artefakte

Im aktuellen konfigurierten Nachweisstand sind pro Prefix diese Dateien
vorhanden:

- Kanonischer Metrikreport als JSON.
- Redaktionelles Abnahmedossier als Markdown.
- Strukturierte Acceptance-Zusammenfassung als JSON.
- Findings als CSV fuer Tabellenarbeit.
- Findings als SARIF 2.1.0 fuer Code-Scanning-Oberflaechen.
- Statischer HTML-Report als archivfaehige Einzeldatei ohne Hosting.
- JSONL-Trenddatei fuer Status, Findings, PDF-Anzahl und Seitenzahlen ueber
  mehrere Laeufe.
- High-Risk-Snapshot-Index; PNG-Snapshots werden optional erzeugt, wenn
  `pdftoppm` verfuegbar ist.
- Ein Dossier pro konfigurierter buildbarer lokaler Content-/Language-Version
  und ein `project-<profile>`-Gesamtprojekt-Dossier.
- Anforderungsmatrix mit M1-M3, S1-S5, Kann-Punkten und ERDA-Ergaenzungen E1-E14.
- Gruppierte Warnungsuebersicht nach Kategorien.
- Offenlegung der konkreten `fail`-Befunde inklusive Severity-Regel und
  Healing-Step; falls keine genaue Seite automatisch ermittelt werden kann,
  muss diese Limitierung dokumentiert und visuell gegengeprueft werden.

## Offene redaktionelle Entscheidungen

### 1. Umgang mit `passed_with_warnings`

Zu entscheiden ist, welche Warnungen ein Release noch passieren lassen duerfen.
Das betrifft zum Beispiel historische Release-Doku-Drift, doppelte Headings,
lange Tokens, offene Review-Marker oder Tabellenkandidaten, die zwar verworfen,
aber nachvollziehbar dokumentiert wurden.

Bewertungsfrage an die Redaktion: Welche Finding-Kategorien duerfen als
akzeptiertes Restrisiko dokumentiert werden, und welche muessen vor Freigabe
behoben werden?

Empfohlene Entscheidungsvorlage:

| Finding-Art | Vorschlag | Redaktionsentscheidung |
|---|---|---|
| `blocked` | nie akzeptieren | offen |
| `fail` | nur mit explizitem Restrisiko-Eintrag | offen |
| `warn` mit Inhalts- oder Layoutwirkung | einzeln bewerten | offen |
| rein historische Doku-Drift | ggf. akzeptierbar, wenn klar historisch | offen |
| `info` | nicht gate-relevant, aber reviewbar | offen |

### 2. Feste Sample-Seiten fuer Release-Signale

Zu entscheiden ist, welche PDF-Seiten bei jedem Release als Stichprobe gelten.
Solche Seiten sollten typische Risiken sichtbar machen: Inhaltsverzeichnis,
lange Tabellen, CJK/Hangul/Kana-Text, Emoji-Fonts, Anhaenge, Rechtliches,
Kolophon und Seiten mit bekannter Layoutdichte.

Bewertungsfrage an die Redaktion: Welche konkreten Seiten oder Kapitel muessen
in jedem Release-Dossier als feste Sichtpruefung erscheinen?

Empfohlene Mindestmenge:

- Inhaltsverzeichnis oder PDF-Outline-Naehe.
- Eine tabellenlastige Seite.
- Eine Seite mit mehrsprachigem CJK/Hangul/Kana-Text.
- Eine Seite mit Emoji- und Sonderzeichenabdeckung.
- Eine Appendix- oder Referenzseite.
- Rechtliches, Attributionsseite oder Kolophon.

### 3. Abnahme pro Sprache oder pro Gesamtprojekt

Zu entscheiden ist, ob die Freigabe je Sprache einzeln erfolgt oder ob ein
Gesamtdossier fuer alle Sprachen genuegt.

Bewertungsfrage an die Redaktion: Soll eine Sprache blockieren koennen, obwohl
andere Sprachfassungen bereits freigabefaehig sind?

Empfohlener Modus:

- Primaer pro Sprache abnehmen, damit lokale redaktionelle Risiken sichtbar
  bleiben.
- Zusaetzlich ein Gesamtprojekt-Dossier als Management- und Release-Uebersicht
  fuehren.

### 4. Kennzahlen: Orientierung oder Gate

Zu entscheiden ist, welche Kennzahlen nur Hinweise sind und welche die Freigabe
hart stoppen.

Bewertungsfrage an die Redaktion: Welche Signale sind Release-blockierend,
welche nur reviewpflichtig?

Empfohlene Einordnung:

| Signal | Vorschlag |
|---|---|
| fehlendes erwartetes PDF | hartes Gate |
| nicht lesbare oder textarme Hauptseiten | hartes Gate oder Fail |
| Ersatzglyphen / Fontfallback-Probleme | Fail, bis redaktionell akzeptiert |
| Seitenzahl ausserhalb Zielkorridor | Warn oder Gate je Profil |
| lange Tokens / Tabellenrisiken | Warn mit Sichtpruefung |
| historische Release-Doku-Drift | Orientierung oder Warn |
| AI-Referenzsignale | Review-Hinweis, keine Autoritaet |

### 5. Textauszuege aus Kundendokumenten

Zu entscheiden ist, wie viel Originaltext in Reports erscheinen darf. Findings
koennen Textauszuege enthalten, damit Redakteure die Stelle schnell erkennen.
Bei Kundendokumenten kann das aber Datenschutz-, Vertraulichkeits- oder
Lizenzfragen beruehren.

Bewertungsfrage an die Redaktion: Welche Detailtiefe ist fuer Review nutzbar,
ohne zu viel Inhalt in technische Reports zu kopieren?

Empfohlene Datenschutzstufen:

| Stufe | Inhalt im Report | Geeignet fuer |
|---|---|---|
| niedrig | Datei, Regel, Seite/Zeile, kurzer Ausschnitt | interne Redaktion |
| mittel | Datei, Regel, Seite/Zeile, gekuerzter Ausschnitt | Kundenreview mit Einschraenkung |
| hoch | Datei, Regel, Seite/Zeile, kein Originaltext | vertrauliche Kundendokumente |

## Entscheidungsvorlage fuer den Kundenredakteur

Bitte markieren oder kommentieren:

- Welche Finding-Kategorien duerfen als Restrisiko akzeptiert werden?
- Welche Kategorien muessen vor Release immer behoben werden?
- Welche Seiten oder Kapitel sollen feste Sichtpruefungs-Samples werden?
- Soll die Freigabe pro Sprache, pro Gesamtprojekt oder in beiden Ebenen
  erfolgen?
- Welche Kennzahlen werden Gates, welche bleiben Hinweise?
- Welche Datenschutzstufe gilt fuer Report-Textauszuege?

## Aktuelle Bewertung des EN-Nachweislaufs

Der konfigurierte Release-Lauf beweist, dass das System echte redaktionelle
Risiken sichtbar macht. Er ist derzeit nicht release-gruen, weil DE und EN je
einen `fail` wegen moeglicher Glyphen-/Fontfallback-Probleme sowie zahlreiche
Warnungen melden. Fuer die Kundenredaktion ist deshalb nicht die Frage, ob das
Werkzeug funktioniert, sondern welche Befunde fachlich akzeptiert, priorisiert
oder inhaltlich behoben werden sollen.

## Zusammenfassung fuer die Vorlage

Das Pflichtenheft ist funktional erfuellt. Vor einer Kundenfreigabe braucht es
keine weitere Werkzeug-Implementierung, sondern eine redaktionelle Policy:
Akzeptierte Restrisiken, feste Stichproben, Gate-Regeln, Sprachscope und
Datenschutzgrad der Reports muessen festgelegt werden.