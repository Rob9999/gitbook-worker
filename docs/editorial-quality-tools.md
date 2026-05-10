---
version: 1.8.0
date: 2026-05-10
history:
  - "1.8.0: 2026-05-10 - Konfigurierten release-Liefernachweis fuer de/en/project dokumentiert."
  - "1.7.0: 2026-05-10 - Orchestrator quality-scope configured fuer Sprach- und Gesamtprojekt-Dossiers dokumentiert."
  - "1.6.0: 2026-05-10 - Statische HTML-Reports, Trend-JSONL, SARIF und High-Risk-Snapshot-Index dokumentiert."
  - "1.5.0: 2026-05-10 - Dossier-Lesehilfe und lokaler EN-Nachweis fuer die Definition of Done ergaenzt."
  - "1.4.0: 2026-05-09 - Pflicht-/Soll-Schnitt mit wiederverwendeten Signalen, Sample-Seiten, Release-Doku-Scan, CSV/Console und Orchestrator-Gate dokumentiert."
  - "1.3.0: 2026-05-09 - Tabellenstrategie-Problemfaelle und Kandidatenkontext beschrieben."
  - "1.2.0: 2026-05-09 - Baseline-Vergleich und akzeptierte Restrisiken dokumentiert."
  - "1.1.0: 2026-05-09 - Publish-Scope, PDF-Zielkorridore und Drift-Pruefungen ergaenzt."
  - "1.0.0: 2026-05-09 - First user guide for editorial quality metrics and acceptance tools."
---

# Editorial Quality Tools

`v2.9.0 Qualitaetskompass` startet mit zwei CLIs fuer redaktionelle
Qualitaetsberichte:

- `python -m gitbook_worker.tools.quality.editorial_metrics`
- `python -m gitbook_worker.tools.quality.editorial_acceptance`

`editorial_metrics` sammelt Markdown-, PDF- und Tabellenstrategie-Signale in
einem JSON-Report. `editorial_acceptance` verdichtet einen oder mehrere
Metrikreports zu einem Markdown-Dossier mit Status, Befunden, Healing-Steps und
manueller Freigabevorlage.

Wenn kein `--markdown-root` angegeben ist, nutzt `editorial_metrics` die lokale
`content.yaml` und die jeweiligen `publish.yml`-Dateien als Scope: `build: true`,
`use_summary`, `out`, `out_dir`, erwartete PDFs, erwartete Tabellenreports und
SUMMARY-verwaiste Markdown-Dateien werden in `metrics.publish_scope` sichtbar.
PDFs aus `build: true` Publish-Eintraegen werden automatisch als erwartete
Artefakte geprueft.

Tabellenstrategie-JSONL-Reports werden nicht nur gezaehlt. Fallbacks,
Overrides und verworfene Papierkandidaten erscheinen als Befunde mit
Report-Zeile, optionaler Markdown-Quelle, Tabellenindex, nahem Heading,
ausgewaehltem Papier und kurzer Kandidatenbewertung. Overrides bleiben als
redaktionelle Entscheidung sichtbar; Fallbacks und knappe Kandidatenwahlen
bleiben reviewbar.

Der Collector wiederverwendet vorhandene Einzelchecks: doppelte Titel und
TODO-Signale aus `link_audit`, Referenzkandidaten aus `ai_references` und
Frontmatter-Syntaxsignale aus dem Frontmatter-Checker. PDF-Reports enthalten
zusaetzlich rekonstruierbare Build-Worker-Versionen aus Metadaten,
modellierte URL-/DOI-Overflow-Signale, CJK/Hangul/Kana-Stichproben und
projektdefinierte Sample-Seitenregeln.

Optional entstehen tabellarische Findings und eine kurze Konsolenzeile:

```powershell
python -m gitbook_worker.tools.quality.editorial_metrics `
  --root . `
  --lang en `
  --output logs/quality/en-editorial-metrics.json `
  --csv-output logs/quality/en-editorial-findings.csv `
  --sarif-output logs/quality/en-editorial-findings.sarif `
  --console-summary
```

`--sarif-output` schreibt dieselben Findings als SARIF 2.1.0. Markdown-Findings
mit `line N` im Ort erhalten eine SARIF-Region; PDF- und Report-Findings bleiben
als artefaktbezogene Ergebnisse sichtbar.

## Minimaler Lauf

```powershell
python -m gitbook_worker.tools.quality.editorial_metrics `
  --root . `
  --markdown-root gitbook_worker/docs/concepts `
  --output build/quality-smoke/editorial-metrics.json

python -m gitbook_worker.tools.quality.editorial_acceptance `
  build/quality-smoke/editorial-metrics.json `
  --output build/quality-smoke/editorial-acceptance.md `
  --html-output build/quality-smoke/editorial-acceptance.html `
  --trend-output build/quality-smoke/editorial-trends.jsonl `
  --snapshot-dir build/quality-smoke/snapshots `
  --snapshot-renderer none
```

Der HTML-Report ist eine einzelne statische Datei ohne CDN, externe Fonts oder
Telemetry. Er ist kein gehostetes Dashboard, sondern ein archivfester
Review-Artefakt fuer Redaktionen und Releases. `--trend-output` haengt pro Lauf
eine kompakte JSONL-Zeile mit Status, Finding-Zahlen, PDF-Anzahl und
Seitenzahlen an. `--snapshot-dir` schreibt immer einen HTML-/JSON-Index fuer
High-Risk-PDF-Seiten; wenn `pdftoppm` im System verfuegbar ist und
`--snapshot-renderer auto` gilt, werden zusaetzlich PNG-Seitenbilder erzeugt.
Fehlt der Renderer, bleibt der Index bewusst ehrlich als "index only" erhalten.

## Mehrsprachiges Profil

Profile koennen ueber `--profile-config` geladen werden. Das Modell ist nicht an
Deutsch/Englisch gebunden, sondern arbeitet mit Rollen und frei waehlbaren
Locales:

```yaml
version: 1.0.0
profiles:
  multilingual-release-candidate:
    network: false
    markdown:
      locale_field: content_lang
      identity_key: content_id
      source_link_field: source
      source_locale: ja
      target_locales:
        - pl
        - hr
        - no
      required_frontmatter_by_role:
        source:
          - content_id
          - content_lang
        target:
          - content_id
          - content_lang
          - source
          - status
      allowed_translation_status:
        - draft
        - in-review
        - approved
```

Weitere Profilfelder stehen in der
[Configuration Reference](configuration-reference.md#6-editorial-quality-profile-cli-option---profile-config)
und in der Per-File-Dokumentation
[editorial-quality-profile.md](configs/editorial-quality-profile.md).

`pdf.pdf_targets` kann projektspezifische Seitenzahlkorridore definieren:

```yaml
pdf:
  pdf_targets:
    publish/sample.pdf:
      target_pages_min: 120
      target_pages_max: 140
      warn_pages_max: 150
```

`pdf.expected_pages` drueckt feste Sample-Seiten als Regeln aus:

```yaml
pdf:
  expected_pages:
    publish/sample.pdf:
      - page: 1
        label: cover sample
        min_text_lines: 3
        must_contain: Sample
```

`editorial_acceptance` prueft zusaetzlich, ob ein Report mit einer alten
Worker-Version erzeugt wurde oder ob ein PDF-Artefakt neuer ist als der Report.
Die Schalter `documentation.fail_on_stale_worker_version` und
`documentation.fail_on_stale_page_count` steuern, ob diese Drift-Signale warnen
oder die Abnahme scheitern lassen.

## Baseline und Restrisiken

`editorial_acceptance` kann einen frueheren Metrikreport als Baseline lesen und
Befunde als `new`, `existing`, `changed` oder `resolved` einordnen:

```powershell
python -m gitbook_worker.tools.quality.editorial_acceptance `
  logs/quality/editorial-metrics.json `
  --baseline logs/quality/editorial-metrics.previous.json `
  --output logs/quality/editorial-acceptance.md
```

Bewusst akzeptierte Restrisiken werden ueber `--accepted-findings` eingebunden.
Sie bleiben im Dossier sichtbar; abgelaufene Akzeptanzen erzeugen ein hartes
Finding, damit alte Freigaben nicht stillschweigend weitergelten:

```yaml
version: 1.0.0
accepted_findings:
  - finding_id: tables.strategy.lowest-score-fallback:abc123def456
    reason: Known layout trade-off for this release candidate.
    role: editor
    date: 2026-05-09
    expires: 2026-06-30
    release: v2.9.0
```

Schema und Pflichtfelder stehen in
[editorial-accepted-findings.md](configs/editorial-accepted-findings.md).

## Dossier lesen

Ein Dossier wird von oben nach unten als Abnahmeprotokoll gelesen:

- `Executive Summary`: Profil, Gesamtstatus und Finding-Zahlen. `blocked` und
  `fail` sind zuerst zu klaeren; `warn` bleibt sichtbar fuer bewusste
  redaktionelle Entscheidungen.
- `Inputs`: zeigt, welche Metrikreports Grundlage der Abnahme sind. Alte oder
  falsche Reports duerfen hier nicht als aktuelle Freigabequelle gelten.
- `PDF Artifacts`: nennt Seitenzahl, Dateigroesse, CreationDate und
  Aenderungszeitpunkt pro PDF, damit Report-Frische nachvollziehbar bleibt.
- `Baseline Comparison` und `Accepted Residual Risks`: zeigen, ob Befunde neu,
  bestehend, geloest, bewusst akzeptiert oder abgelaufen sind.
- `Findings`: sortiert nach Severity. Jeder Befund nennt Artefakt, Ort,
  Evidenz, redaktionelle Wirkung und Healing-Step.
- `Review Notes`: grenzt technische Link-/AI-/Compliance-Signale von
  inhaltlicher Wahrheit, autoritativer Quellenpruefung und Rechtsberatung ab.
- `Human Decision`: bleibt absichtlich leer. Die finale Freigabe ist eine
  menschliche Entscheidung und wird nicht vom Tool gesetzt.

## Orchestrator und CI-Gate

Der Workflow-Orchestrator kennt den optionalen Schritt `editorial-quality`.
Er schreibt Metrics, CSV-Findings, SARIF, Markdown-Dossier, JSON-Summary,
statischen HTML-Report, Trend-JSONL und Snapshot-Index nach `logs/quality/`.
Ohne `--quality-gate` bleibt der Schritt ein Bericht; mit
`--quality-gate` wird der Acceptance-Status zum CI-Gate.
Standardmaessig erzeugt der Schritt Artefakte fuer die mit `--lang` gewaehlte
Content-Version. Fuer ein Lieferpaket mit allen konfigurierten buildbaren
lokalen Sprachversionen plus Gesamtprojekt-Dossier wird `--quality-scope
configured` genutzt. Dabei entstehen pro Sprache `logs/quality/<lang>-<profile>-
editorial-*` und zusaetzlich `logs/quality/project-<profile>-editorial-*`.
Eintraege mit `build: false` sowie nicht-lokale Content-Quellen werden in diesem
Scope uebersprungen.

```powershell
python -m gitbook_worker.tools.workflow_orchestrator run `
  --root . `
  --content-config content.yaml `
  --lang en `
  --profile local `
  --step publisher `
  --step editorial-quality `
  --quality-profile release `
  --quality-gate
```

Lieferlauf fuer alle buildbaren lokalen `content.yaml`-Versionen:

```powershell
python -m gitbook_worker.tools.workflow_orchestrator run `
  --root . `
  --content-config content.yaml `
  --profile local `
  --step editorial-quality `
  --quality-profile release `
  --quality-scope configured
```

## Exit-Codes

- `45`: harte redaktionelle Findings.
- `46`: blockierende fehlende Artefakte.
- `47`: Metrikreport nicht lesbar.
- `48`: ungueltiges Abnahmeprofil.

Beide neuen CLIs unterstuetzen `--help-exit-codes`.

## Lokaler Nachweis

Am 2026-05-10 wurde ein lokaler EN-Sample-Lauf mit PDF-Build und
`editorial-quality` ausgefuehrt:

```powershell
python -m gitbook_worker.tools.workflow_orchestrator run `
  --root C:\gitbook-worker `
  --content-config content.yaml `
  --lang en `
  --profile local `
  --step publisher `
  --step editorial-quality `
  --quality-profile local
```

Der Lauf erzeugte:

- `logs/quality/en-local-editorial-metrics.json`
- `logs/quality/en-local-editorial-findings.csv`
- `logs/quality/en-local-editorial-findings.sarif`
- `logs/quality/en-local-editorial-acceptance.md`
- `logs/quality/en-local-editorial-acceptance.json`
- `logs/quality/en-local-editorial-report.html`
- `logs/quality/editorial-trends.jsonl`
- `logs/quality/snapshots/en-local/index.html`

Das Dossier ist bewusst nicht als „gruen“ behauptet: Der Sample-Status war
`failed` mit `1 fail`, `172 warn` und `19 info`. Das ist fuer den
Qualitaetskompass ein gueltiger Nachweis, weil der Build ein lesbares Dossier
erzeugt und reale redaktionelle Restarbeit sichtbar macht.

## Konfigurierter Liefernachweis

Am 2026-05-10 wurde zusaetzlich ein konfigurierter `release`-Lieferlauf ohne
Gate ausgefuehrt:

```powershell
python -m gitbook_worker.tools.workflow_orchestrator run `
  --root C:\gitbook-worker `
  --content-config C:\gitbook-worker\content.yaml `
  --profile local `
  --step editorial-quality `
  --quality-profile release `
  --quality-scope configured
```

Der Lauf erzeugte vollstaendige Artefaktpakete fuer `de-release`, `en-release`
und `project-release`. Die Detailnachweise stehen unter
[reviews/editorial-quality-delivery-evidence.md](reviews/editorial-quality-delivery-evidence.md).
Alle drei Dossiers sind absichtlich `failed`, weil reale
`pdf.text.replacement_glyph`-Fails nicht versteckt werden.