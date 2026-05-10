---
version: 1.0.0
date: 2026-05-10
status: delivery-evidence
target_release: "v2.9.0 Qualitaetskompass"
history:
  - "1.0.0: 2026-05-10 - Konfigurierten Editorial-Quality-Lieferlauf und Artefaktpruefung dokumentiert."
---

# Editorial Quality Delivery Evidence

Dieser Nachweis schliesst die Lieferpunkte 1 und 2 aus dem
Lieferreife-Review: vollstaendige Artefakte und je konfigurierter buildbarer
lokaler Content-/Language-Version ein Dossier plus Gesamtprojekt-Dossier.

## Sicherungspunkt

Vor dem Lieferlauf wurde kein Commit erstellt, weil der Arbeitsbaum bereits
zahlreiche laufende Aenderungen enthielt. Als gleichwertiger nicht-mutierender
Sicherungspunkt wurde ein Git-Stash-Objekt erzeugt:

| Art | Wert |
|---|---|
| Sicherung | `git stash create "pre-delivery-quality-package"` |
| Hash | `dd23dba21aa16cccf509b4841c1005f8ccf677d1` |

## Ausgefuehrter Lauf

```powershell
python -m gitbook_worker.tools.workflow_orchestrator run `
  --root C:\gitbook-worker `
  --content-config C:\gitbook-worker\content.yaml `
  --profile local `
  --step editorial-quality `
  --quality-profile release `
  --quality-scope configured
```

`content.yaml` wurde dabei wie folgt ausgewertet: `de` und `en` sind lokale
buildbare Eintraege; `de-edge-cases`, `de-ref-check` und `en-edge-cases` sind
`build: false`; `ua` ist eine Git-Quelle und wird fuer diesen lokalen
Lieferumfang uebersprungen.

## Ergebnisstatus

| Prefix | Dossier-Ebene | Status | Blocked | Fail | Warn | Info |
|---|---|---|---:|---:|---:|---:|
| `de-release` | lokale Content-/Language-Version `de` | `failed` | 0 | 1 | 195 | 27 |
| `en-release` | lokale Content-/Language-Version `en` | `failed` | 0 | 1 | 172 | 18 |
| `project-release` | Gesamtprojekt `de` + `en` | `failed` | 0 | 2 | 546 | 30 |

Der Status `failed` ist Bestandteil der Lieferung. Die Fails werden nicht
unterdrueckt, sondern in der Fail-Offenlegung dokumentiert.

## Artefaktpruefung

Fuer alle drei Prefixe wurden diese Artefakte erzeugt und auf Existenz
geprueft:

| Artefakt | `de-release` | `en-release` | `project-release` |
|---|---:|---:|---:|
| `*-editorial-metrics.json` | 385236 bytes | 343859 bytes | 834000 bytes |
| `*-editorial-findings.csv` | 104858 bytes | 81221 bytes | 260265 bytes |
| `*-editorial-findings.sarif` | 218657 bytes | 180333 bytes | 549527 bytes |
| `*-editorial-acceptance.md` | 119059 bytes | 93434 bytes | 294671 bytes |
| `*-editorial-acceptance.json` | 629 bytes | 629 bytes | 629 bytes |
| `*-editorial-report.html` | 164321 bytes | 132682 bytes | 409514 bytes |
| `snapshots/<prefix>/index.html` | 651 bytes | 651 bytes | 651 bytes |

Zusaetzlich wurde `logs/quality/editorial-trends.jsonl` erzeugt; die Datei
enthaelt nach dem Lieferlauf drei Trendzeilen fuer die drei Dossier-Ebenen.

## Paketgrenze

Der Lieferlauf belegt die technische Erzeugung und Ablage des Nachweispakets.
Er ist keine fachliche Freigabe der Inhalte. Die fachliche Freigabe bleibt an
die Kundenredaktion gebunden, insbesondere fuer die beiden
`pdf.text.replacement_glyph`-Fails, die Warnungsgruppen und die gewaehlte
Datenschutzstufe fuer Evidenzauszuege.

## Review-Zusammenfassung

- Die konfigurierten lokalen Content-Versionen werden nicht hart auf DE/EN
  verdrahtet, sondern aus `content.yaml` abgeleitet.
- Remote- und `build: false`-Eintraege werden bewusst ausgelassen und im Lauf
  geloggt.
- Alle erwarteten Artefaktarten liegen fuer jede Dossier-Ebene vor.
- Die Lieferung bleibt ehrlich: `failed`-Status und Residualrisiken werden nicht
  in einen gruenen Status umgedeutet.