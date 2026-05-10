---
version: 1.0.0
date: 2026-05-10
status: delivery-policy
target_release: "v2.9.0 Qualitaetskompass"
history:
  - "1.0.0: 2026-05-10 - Datenschutz- und Evidenzstufen fuer Editorial-Quality-Reports dokumentiert."
---

# Editorial Quality Evidence Privacy

Diese Policy schliesst Lieferpunkt 8. Sie legt fest, wie viel Originaltext aus
Kundendokumenten in Findings, CSV, SARIF, HTML und Dossiers erscheinen darf.

## Stufenmodell

| Stufe | Zweck | Erlaubte Evidenz | Nicht erlaubt | Geeignet fuer |
|---|---|---|---|---|
| niedrig | interne Redaktion | Datei, Regel, Zeile/Seite, kurzer Textauszug | komplette Kapitel oder lange Tabellenzellen | interne Entwicklung und Redaktionsreview |
| mittel | Kundenreview | Datei, Regel, Zeile/Seite, gekuerzter Textauszug | sensible Namen, vertrauliche Passagen, lange Zitate | Standard-Kundenlieferung |
| hoch | vertrauliche Kundendokumente | Datei, Regel, Zeile/Seite, Hash oder neutralisierte Evidenz | Originaltext im technischen Artefakt | vertrauliche Projekte und externe Abnahme |

## Aktueller technischer Stand

Die aktuelle Implementierung kuerzt Evidenzen zentral mit
`shorten_evidence(...)` auf kurze Auszuege und schreibt keine kompletten
Dokumentabschnitte in Findings. Eine echte Umschaltung der Evidenzstufe ist noch
kein eigener CLI-Schalter. Bis ein solcher Schalter eingefuehrt wird, gilt fuer
Kundenlieferungen der dokumentierte Profilmodus `mittel`:

- CSV, SARIF, HTML und Markdown duerfen kurze gekuerzte Evidenzauszuege
  enthalten.
- Vertrauliche Kundendokumente muessen vor Paketuebergang entweder mit Stufe
  `hoch` nachbearbeitet oder mit einem kundenspezifischen Profil ohne
  Originaltextauszuege erzeugt werden.
- Die Kundenredaktion entscheidet, ob `niedrig`, `mittel` oder `hoch` fuer das
  Projekt gilt.

## Lieferempfehlung

| Artefakt | Standardstufe | Begruendung |
|---|---|---|
| `*-editorial-acceptance.md` | mittel | Redakteure brauchen Ort, Regel und kurzen Kontext. |
| `*-editorial-findings.csv` | mittel | Tabellenarbeit braucht gruppierbare und filterbare Evidenz. |
| `*-editorial-findings.sarif` | mittel | SARIF wird technisch genutzt, kann aber Textauszuege in Scanning-UIs zeigen. |
| `*-editorial-report.html` | mittel | Archivfaehiger Reviewbericht, kein oeffentliches Dashboard. |
| `editorial-trends.jsonl` | hoch | Trenddaten brauchen keine Originaltextauszuege. |
| `snapshots/<prefix>/index.html` | mittel | Index nennt Risikoorte; optionale PNGs koennen Inhalte zeigen. |

## Abnahmeentscheidung

Vor Kundenfreigabe ist eine explizite Entscheidung erforderlich:

| Frage | Standardantwort fuer v2.9.0 |
|---|---|
| Duerfen kurze Originaltextauszuege in Reports stehen? | Ja, fuer interne und Standard-Kundenreviews mit Stufe `mittel`. |
| Duerfen komplette Tabellen oder Kapitel in Reports stehen? | Nein. |
| Duerfen Snapshots Inhalte zeigen? | Nur nach Freigabe; sonst Index-only liefern. |
| Wie werden vertrauliche Dokumente behandelt? | Stufe `hoch`, keine Originaltextauszuege in technischen Reports. |

## Nachlieferungsgrenze

Eine spaetere Nachlieferung ist angemessen, wenn der Kunde nach Sichtung eine
strengere Stufe verlangt oder Kundensamples vertrauliche Inhalte enthalten. Eine
Nachlieferung ist nicht angemessen, wenn ohne Kundenentscheidung bereits
unangemessen viele Originaltexte ausgeliefert wurden; deshalb gilt bis zur
Freigabe der konservative Standard `mittel` und bei Vertraulichkeit `hoch`.