---
version: 1.4.0
date: 2026-05-09
history:
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
  --console-summary
```

## Minimaler Lauf

```powershell
python -m gitbook_worker.tools.quality.editorial_metrics `
  --root . `
  --markdown-root gitbook_worker/docs/concepts `
  --output build/quality-smoke/editorial-metrics.json

python -m gitbook_worker.tools.quality.editorial_acceptance `
  build/quality-smoke/editorial-metrics.json `
  --output build/quality-smoke/editorial-acceptance.md
```

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

## Orchestrator und CI-Gate

Der Workflow-Orchestrator kennt den optionalen Schritt `editorial-quality`.
Er schreibt Metrics, CSV-Findings, Markdown-Dossier und JSON-Summary nach
`logs/quality/`. Ohne `--quality-gate` bleibt der Schritt ein Bericht; mit
`--quality-gate` wird der Acceptance-Status zum CI-Gate.

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

## Exit-Codes

- `45`: harte redaktionelle Findings.
- `46`: blockierende fehlende Artefakte.
- `47`: Metrikreport nicht lesbar.
- `48`: ungueltiges Abnahmeprofil.

Beide neuen CLIs unterstuetzen `--help-exit-codes`.