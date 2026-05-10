---
version: 1.0.0
date: 2026-05-10
status: delivery-evidence
target_release: "v2.9.0 Qualitaetskompass"
history:
  - "1.0.0: 2026-05-10 - Anforderungsmatrix fuer Muss-, Soll-, Kann- und ERDA-Ergaenzungspunkte erstellt."
---

# Editorial Quality Requirements Matrix

Diese Matrix schliesst Lieferpunkt 3. Sie verknuepft Pflichtenheft-Aussagen mit
Implementierungsorten, Tests und realen Lieferartefakten aus dem konfigurierten
`release`-Lauf.

| ID | Anforderung | Status | Implementierungsort | Test/Nachweis | Lieferartefakt | Offenes Risiko |
|---|---|---|---|---|---|---|
| M1 | Markdown-Metrikcollector | erfuellt | `gitbook_worker/tools/quality/editorial_metrics.py` | `test_editorial_quality.py` Markdown-Tests | `logs/quality/*-editorial-metrics.json`, `*-editorial-findings.csv` | Reale Warnungen muessen redaktionell priorisiert werden. |
| M2 | PDF-Metrikcollector | erfuellt | `editorial_metrics.analyze_pdf` | PDF-Tests mit `PdfWriter` und reale PDFs | `de/publish/das-sample-buch.pdf`, `en/publish/the-sample-book.pdf` in Metrics | Glyphen-Fails sind offen und releasekritisch. |
| M3 | Markdown-PDF-Abgleich | erfuellt | TOC-/Heading-Abgleich in `editorial_metrics.py` | Tests fuer PDF-TOC und reale Dossiers | `*-editorial-acceptance.md`, `*-editorial-report.html` | Outline-Treffer bleiben teils `info` und brauchen Sichtpruefung. |
| S1 | Profile und Schwellen | erfuellt | `editorial_common.py` Built-in-Profile | Profiltests und Exit-Code-Demo | Lauf mit `--quality-profile release` | Kunden-Policy fuer Warnungen noch fachlich festzulegen. |
| S2 | Reportformate | erfuellt | Metrics- und Acceptance-CLI | Format-Tests fuer JSON, CSV, SARIF, HTML, Markdown | JSON, CSV, SARIF, MD, HTML, Trend-JSONL, Snapshot-Index | Keine. |
| S3 | Workflow-Integration | erfuellt | `workflow_orchestrator/orchestrator.py` | Orchestrator-Tests fuer `--quality-scope configured` | `de-release`, `en-release`, `project-release` | Gate absichtlich nicht aktiviert, damit alle Dossiers entstehen. |
| S4 | Sample- und Regression-Faelle | erfuellt | `gitbook_worker/tests/test_editorial_quality.py` | Fokus-Pytest-Suites | Testnachweis im Lieferreife-Review | Weitere Kundensamples koennen Nachlieferungen ausloesen. |
| S5 | Seitenzahl-Zielkorridore | erfuellt | `PdfProfile.pdf_targets`, `expected_pages` | Tests fuer Korridor- und Sample-Seitenregeln | Metrics-Profilfelder und Dossier-Findings | Projektspezifische Zielwerte muessen kundenseitig gesetzt werden. |
| K1 | HTML-Report | erfuellt | `editorial_acceptance.py` HTML-Renderer | `test_acceptance_writes_html_trends_and_snapshot_index` | `*-editorial-report.html` | Statische Datei, kein Dashboard. |
| K2 | High-Risk-Snapshot-Index | erfuellt | Snapshot-Index in `editorial_acceptance.py` | Snapshot-Test | `logs/quality/snapshots/<prefix>/index.html` | PNGs optional; Index ist auch ohne Renderer gueltig. |
| K3 | Baseline-Vergleich | erfuellt | Baseline-Vergleich in `editorial_acceptance.py` | Baseline-Test | Dossier-Abschnitt `Baseline Comparison` | Im Lieferlauf wurde keine Baseline uebergeben. |
| K4 | Trendmetriken | erfuellt | Trend-JSONL in `editorial_acceptance.py` | Trend-Test | `logs/quality/editorial-trends.jsonl` | Trenddatei ist append-only und braucht Archivdisziplin. |
| K5 | SARIF | erfuellt | `write_findings_sarif` | SARIF-Test | `*-editorial-findings.sarif` | SARIF ersetzt keine redaktionelle Freigabe. |
| E1 | Report-Drift | erfuellt | Release-Doku-Scan | Release-Drift-Findings im Lauf | `release_docs.worker_version.stale` | Historische Release-Dokumente erzeugen viele Warnungen. |
| E2 | Publish-Scope | erfuellt | `discover_publish_scope` | Scope-Findings im Lauf | `publish.summary.*` Findings | Orphaned Markdown muss fachlich bewertet werden. |
| E3 | Tabellenstrategie | erfuellt | `analyze_table_reports` | Tabellenstrategie-Test | `tables.strategy.rejected_candidates` | Verwarfene Kandidaten bleiben Sichtpruefung. |
| E4 | Baseline-Klassifikation | erfuellt | `_compare_with_baseline` | Baseline-Test | Dossier-Abschnitt | Keine Baseline im Lieferlauf. |
| E5 | Restrisiko-Register | erfuellt | `_apply_accepted_findings` | Accepted-Findings-Test | Dossier-Abschnitt | Keine akzeptierten Restrisiken im Lieferlauf. |
| E6 | Seitenziel-Findings | erfuellt | `_check_pdf_targets` | PDF-Target-Test | Metrics- und Dossier-Findings | Zielkorridore sind projektspezifisch zu pflegen. |
| E7 | Profile | erfuellt | Built-in-Profile und `--profile-config` | Profil-/CLI-Tests | `profile: release` in JSON | Kundenspezifische Profile koennen ergaenzt werden. |
| E8 | JSON-Ausgabe | erfuellt | `write_json_report`, `--json-output` | JSON-Tests | Metrics- und Acceptance-JSON | Keine. |
| E9 | Markdown-Ausgabe | erfuellt | Dossier-Renderer | Acceptance-Test | `*-editorial-acceptance.md` | Dossier ist Review-Artefakt, keine Freigabe. |
| E10 | CSV-Ausgabe | erfuellt | `write_findings_csv` | CSV-Ausgabe im Lieferlauf | `*-editorial-findings.csv` | CSV kann Kundentext-Auszug enthalten. |
| E11 | SARIF-Ausgabe | erfuellt | `write_findings_sarif` | SARIF-Test | `*-editorial-findings.sarif` | Datenschutzstufe fuer Evidence beachten. |
| E12 | HTML-Ausgabe | erfuellt | HTML-Renderer | HTML-Test | `*-editorial-report.html` | Enthaltene Evidenzstufe beachten. |
| E13 | Trend-Ausgabe | erfuellt | Trend-Writer | Trend-Test | `editorial-trends.jsonl` | Kein Ersatz fuer Artefaktarchiv. |
| E14 | Redaktionelle Entscheidungsfragen | erfuellt | Review-Dokumente | Editor-Report und Delivery-Review | `docs/reviews/*.md` | Entscheidungen bleiben beim Kundenredakteur. |

## Testnachweise

Zuletzt validiert wurden die Orchestrator-Schnitte mit:

```powershell
python -m pytest gitbook_worker/tests/workflow-orchestrator/test_orchestrator.py -q
python -m pytest gitbook_worker/tests/test_orchestrator_validate.py gitbook_worker/tests/workflow-orchestrator/test_orchestrator.py -q
```

Die breitere Validierung fuer diese Lieferung ist im Lieferreife-Review als
auszufuehrender Fokuslauf gefuehrt, weil in dieser Phase mehrere neue
Dokumentationsartefakte entstanden sind.