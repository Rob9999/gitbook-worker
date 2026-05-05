---
version: 0.1.0
date: 2026-05-05
status: triaged
priority: high
labels: [customer-feedback, ai-reference-check, v2.0.1, release-2.4]
history:
  - version: 0.1.0
    date: 2026-05-05
    description: Kundenwunschliste aus produktiver v2.0.1-Nutzung aufgenommen und gegen v2.4.0-Stand gemappt.
---

# Kundenfeedback: AI-Reference-Check aus v2.0.1-Nutzung

## Kontext

Ein Kunde auf `gitbook_worker` v2.0.1 hat aus produktiven Problemen eine
konkrete Wunschliste fuer `gitbook_worker.tools.quality.ai_references`
geliefert. Der lokale Wrapper des Kunden dient als Prototyp fuer Upstream-
Haertungen.

## Must Have

- [x] Throttling direkt im Tool: aktuell ueber `--requests-per-minute`,
  `--min-request-interval`, `--throttle-jitter`; kompatible Aliase
  `--delay-seconds` und `--jitter-seconds` wurden fuer Kundenskripte ergaenzt.
- [x] 429-Behandlung: `Retry-After` plus begrenzter Backoff; kompatible Aliase
  `--cooldown-on-429-seconds` und `--max-consecutive-429` wurden ergaenzt.
- [x] Secret-Schutz: API-Keys und `?key=`/`api_key=` werden in Fehlern und
  JSON-Reports redigiert.
- [x] Aktuelles Pruefdatum: `--as-of-date YYYY-MM-DD` setzt Prompt-Regel und
  erzwingt `validation_date` im Ergebnis auf dieses Datum.
- [ ] Inline-Links/DOIs erkennen: Bare URLs, Markdown-Links und Frontmatter-DOIs
  muessen ueber die Quellenblock-Extraktion hinaus erfasst werden.

## Should Have

- [x] Gemini-Unterstuetzung: `genai`/`google-genai`, automatische
  `models/<model>:generateContent`-URL und aktuelles Default-Modell.
- [x] Env-Aliase: `AI_API_KEY`, `AI_URL`, `AI_PROVIDER` zusaetzlich zu
  `AI_REFERENCE_*`.
- [x] Dry-Run/Report-first: Ohne `--apply` werden keine Markdown-Dateien
  veraendert.
- [ ] Ergebnissemantik weiter schaerfen: `confidence`,
  `requires_manual_review`, `reason`, `evidence_url_status`, `rate_limited`.
- [ ] Resume-/Batch-Modus: `--files-list`, `--max-tasks`,
  `--resume-from-report`, Teilreports pro Batch.

## Nice To Have

- [ ] Technischer Link-/DOI-Check vor LLM-Aufruf.
- [ ] DOI-Handle/API speziell behandeln.
- [x] Projektroot-Log ergaenzt: das Tool loggt den effektiven `--root` separat
  als `AI reference project root`, auch wenn Paketpfad-Logs anders lauten.

## Naechste Scheibe

Die naechste technische Scheibe sollte Inline-Link-/DOI-Extraktion plus eine
deterministische Vorpruefung sein. Das reduziert LLM-Aufrufe und legt die Basis
fuer Batch/Resume, ohne die bestehende Report-first-Semantik zu brechen.
