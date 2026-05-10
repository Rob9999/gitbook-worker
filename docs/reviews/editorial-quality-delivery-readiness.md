---
version: 1.2.0
date: 2026-05-10
status: technical-package-ready-with-open-fails
target_release: "v2.9.0 Qualitaetskompass"
history:
  - "1.2.0: 2026-05-10 - Acht Vorlieferungspunkte mit Lieferlauf, Artefakten und Review-Nachweisen geschlossen."
  - "1.1.0: 2026-05-10 - Dossierumfang auf eine buildbare lokale Version je Sprache plus project-Gesamtdossier geschaerft."
  - "1.0.0: 2026-05-10 - Lieferreife-Bewertung und Vorlieferungsauflagen fuer die redaktionellen Qualitaetswerkzeuge erstellt."
---

# Lieferreife-Review: Editorial Quality Tools

Dieser Review bewertet den Stand vor Kundenlieferung. Er trennt bewusst drei
Dinge: technische Paketuebergabe, fachliche Kundenabnahme und moegliche
Nachlieferung nach Reproduktionslauf oder Kundenfeedback.

## Ampel

| Bereich | Bewertung |
|---|---|
| Pflichtenheft-Abdeckung nach Bericht | gruen |
| Nachweisbarkeit vor Lieferung | gruen-gelb |
| Werkzeug-Design | gruen |
| Kunden-/Release-Abnahme | rot |
| Lieferfreigabe zum Paketuebergang | ja, mit Bedingungen |

## Bewertung

Das Werkzeugdesign ist liefernah: Metriken, Dossier, Profile, Baseline,
Restrisiko-Register, Publish-Scope, Tabellenstrategie, Seitenkorridore und die
verschiedenen Ausgabeformate passen zum geforderten Zielbild.

Die technische Nachweisbarkeit ist jetzt hergestellt: Der konfigurierte
Lieferlauf erzeugt `de-release`, `en-release` und `project-release` mit
Metrics, CSV, SARIF, Markdown-Dossier, Acceptance-JSON, HTML, Trend-JSONL und
Snapshot-Index. Die Dossiers bleiben bewusst `failed`, weil echte Font-/Glyphen-
Fails offen sind.

Die technische Lieferung kann zur Pruefung erfolgen, wenn diese Bedingungen
transparent im Paket liegen. Eine fachliche Abnahme oder Kundenfreigabe darf
erst nach Sichtung der Artefakte, Reproduktionslauf im ERDA-Repo und
redaktioneller Policy-Entscheidung erfolgen.

## Aktueller Liefernachweis

| Nachweis | Datei |
|---|---|
| Lieferlauf und Artefaktpaket | [editorial-quality-delivery-evidence.md](editorial-quality-delivery-evidence.md) |
| Anforderungsmatrix | [editorial-quality-requirements-matrix.md](editorial-quality-requirements-matrix.md) |
| Warnungsgruppen | [editorial-quality-warning-groups.md](editorial-quality-warning-groups.md) |
| Fail-Offenlegung | [editorial-quality-fail-disclosure.md](editorial-quality-fail-disclosure.md) |
| Exit-Code-Demo | [editorial-quality-exit-code-evidence.md](editorial-quality-exit-code-evidence.md) |
| Datenschutz-/Evidenzstufen | [editorial-quality-evidence-privacy.md](editorial-quality-evidence-privacy.md) |

Der konfigurierte Lauf am 2026-05-10 ergab:

| Prefix | Status | Blocked | Fail | Warn | Info |
|---|---|---:|---:|---:|---:|
| `de-release` | `failed` | 0 | 1 | 195 | 27 |
| `en-release` | `failed` | 0 | 1 | 172 | 18 |
| `project-release` | `failed` | 0 | 2 | 546 | 30 |

## Vor Lieferung geschlossen

| Nr. | Punkt | Status | Nachweis |
|---:|---|---|---|
| 1 | Vollstaendige Artefaktlieferung | geschlossen | Delivery Evidence |
| 2 | Dossier pro buildbarer lokaler Version plus Gesamtprojekt | geschlossen | Delivery Evidence |
| 3 | Anforderungsmatrix | geschlossen | Requirements Matrix |
| 4 | Offenlegung der `fail`-Befunde | geschlossen | Fail Disclosure |
| 5 | Gruppierung der Warnungen | geschlossen | Warning Groups |
| 6 | Exit-Code-Demo | geschlossen | Exit-Code Evidence |
| 7 | Test- und Snapshot-Nachweise | geschlossen | Requirements Matrix und Delivery Evidence |
| 8 | Datenschutzstufen fuer Evidenzauszuege | geschlossen als dokumentierter Profilmodus | Evidence Privacy |

## Anforderungsmatrix geschlossen

Die vollstaendige Matrix steht in
[editorial-quality-requirements-matrix.md](editorial-quality-requirements-matrix.md).
Die folgende Tabelle bleibt als Kurzuebersicht erhalten.

| ID | Anforderung | Erwarteter Nachweis |
|---|---|---|
| M1 | Markdown-Metrikcollector | JSON-Report, CSV, Tests, Sample mit Frontmatter-/Review-Findings |
| M2 | PDF-Metrikcollector | PDF-Metriken, Font-/Glyphenfinding, PDF-TOC, Tests |
| M3 | Markdown-PDF-Abgleich | TOC/Heading-Abgleich, fehlende Artefakte, Sample-Seitenregeln |
| S1 | Profile und Schwellen | Profilkonfigurationen `local`, `release`, `customer-handover` |
| S2 | Reportformate | JSON, Markdown, CSV, Konsole |
| S3 | Workflow-Integration | Orchestrator-Lauf und Logs unter `logs/quality/` |
| S4 | Sample- und Regression-Faelle | Tests und Sample-Runs fuer Warnungen und Fehler |
| S5 | Seitenzahl-Zielkorridore | `pdf_targets`-Nachweis und Finding bei Abweichung |
| K1 | HTML-Report | Statische HTML-Datei |
| K2 | High-Risk-Snapshots | Snapshot-Index, optional PNGs |
| K3 | Baseline-Vergleich | Baseline-Dossier mit `new`, `existing`, `changed`, `resolved` |
| K4 | Trendmetriken | JSONL-Trenddatei |
| K5 | SARIF | SARIF 2.1.0-Datei |
| E1 | Report-Drift | Release-Doku-Drift-Findings |
| E2 | Publish-Scope | Orphaned-/Missing-Artefact-Findings |
| E3 | Tabellenstrategie | Tabellenlayout-Report und rejected-candidates-Findings |
| E4 | Baseline-Vergleich | Baseline-Klassifikation im Acceptance-Dossier |
| E5 | Restrisiko-Register | Accepted-findings-Auswertung |
| E6 | Seitenzahl-Zielkorridore | Profilbasierte Seitenziel-Findings |
| E7 | Profile | Profilnamen, Schwellen und Exit-Verhalten |
| E8 | JSON-Ausgabe | Metrik- und Acceptance-JSON |
| E9 | Markdown-Ausgabe | Dossier als Markdown |
| E10 | CSV-Ausgabe | Findings-CSV |
| E11 | SARIF-Ausgabe | SARIF-Datei mit Severity-Mapping |
| E12 | HTML-Ausgabe | statischer HTML-Report |
| E13 | Trend-Ausgabe | JSONL-Trenddatensatz |
| E14 | Redaktionelle Entscheidungsfragen | Review-Report mit Policy-Fragen |

## Fail-Befund offengelegt

Der konfigurierte Lauf meldet zwei harte Glyphen-/Fontfallback-Fails:
`de/publish/das-sample-buch.pdf` mit 5131 replacement glyph signals und
`en/publish/the-sample-book.pdf` mit 5166 replacement glyph signals. Details
stehen in [editorial-quality-fail-disclosure.md](editorial-quality-fail-disclosure.md).

Zur fachlichen Freigabe muss dazu stehen:

- betroffene PDF-Datei und, soweit technisch moeglich, Seite oder Textbereich,
- Severity-Regel und Schwelle,
- erkannter Umfang des Signals,
- Healing-Step,
- visuelle Gegenpruefung oder dokumentierte Begrenzung, falls die Seite nicht
  automatisch lokalisierbar ist.

Font-/Glyphenprobleme bleiben im Release-Kontext grundsaetzlich `fail`, bis sie
visuell und technisch geklaert sind.

## Warnungen gruppiert

Die Warnungen sind in
[editorial-quality-warning-groups.md](editorial-quality-warning-groups.md)
gruppiert. Die wichtigsten Klassen sind:

- Layout und lange Tokens,
- Frontmatter und Metadaten,
- Publish-Scope,
- Release-Doku-Drift,
- Tabellenstrategie,
- Links und Quellen/AI,
- Review-Marker,
- Datenschutz oder Evidenzauszuege.

Jede Gruppe enthaelt Anzahl, Risiko und Healing-Step.

## Policy-Empfehlung

| Severity oder Signal | Empfehlung |
|---|---|
| `blocked` | nie akzeptieren |
| `fail` | in echten Release-Laeufen blockierend; nur mit explizit dokumentiertem Restrisiko uebergangsweise akzeptierbar |
| `warn` | akzeptierbar, wenn gruppiert, erklaerbar und mit Healing-Step versehen |
| historische Doku-Drift | Preview: `warn`; Release-Final: `fail`, wenn aktuelle Releaseaussagen verfaelscht werden |
| `info` | nicht gate-relevant |
| AI-/Quellen-Signale | Review-Hinweis, keine Wahrheits- oder Rechtsbehauptung |
| Font-/Glyphenprobleme | `fail`, bis visuell und technisch geklaert |

## Nachlieferung sauber abgrenzen

Eine Nachlieferung ist vertretbar, wenn die technische Lieferung komplett ist,
aber im Kunden- oder ERDA-Reproduktionslauf neue Umgebungs-, Inhalts- oder
Policy-Fragen sichtbar werden.

Nachlieferung ist angemessen bei:

- kundenseitigen Inhaltsbefunden, die erst im ERDA-Repo sichtbar werden,
- redaktionell geaenderter Gate-Policy,
- zusaetzlichen Datenschutzvorgaben fuer Evidenzauszuege,
- fehlenden Systemtools fuer optionale Snapshots, wenn der Snapshot-Index
  korrekt als Fallback geliefert wurde,
- neuen realen Glyphen-/Fontfaellen, die andere Fonts oder Samples erfordern.

Nachlieferung ist nicht angemessen fuer:

- fehlende Basisartefakte,
- fehlende DE-/EN-/Gesamtprojekt-Nachweise,
- nicht dokumentierte Exit-Codes oder Profile,
- unklare `fail`-Befunde ohne Healing-Step,
- eine fehlende Anforderungsmatrix.

Diese Punkte muessen vor Paketuebergang geschlossen werden.

## Empfohlener Ablauf

1. Vorlieferungspaket komplett erzeugen.
2. Anforderungsmatrix und Warnungsgruppierung beilegen.
3. Internen Reproduktionslauf dokumentieren.
4. Paket als technische Lieferung mit Bedingungen uebergeben.
5. Kundenredaktion entscheidet Gate-, Warnungs- und Datenschutz-Policy.
6. ERDA-Reproduktionslauf auswerten.
7. Nur echte kundenseitige oder policybedingte Punkte als Nachlieferung planen.