---
version: 1.0.0
date: 2026-05-04
status: implemented
priority: high
labels: [quality, ai-reference-check, throttling, hexagonal-architecture]
history:
  - "1.0.0: 2026-05-04 - Backlog und Umsetzung fuer AI-Reference-Check-Haertung"
---

# Backlog: AI-Reference-Check haerten

## Ziel

Der optionale Orchestrator-Schritt `ai-reference-check` soll von einem
LLM-gestuetzten Spezialhelfer zu einem auditierbaren QA-Werkzeug reifen:
report-first, secret-sicher, sprachbewusst, throttelbar und testbar ohne echte
Provider-Aufrufe.

## Motivation

Die vorhandene Implementierung konnte Quellen aus Markdown extrahieren,
Provider anfragen, JSON-Reports schreiben und bestaetigte Korrekturen anwenden.
Technisch fehlten aber wichtige Sicherheits- und Betriebsleitplanken:

- Reports durften keine API-Keys serialisieren.
- LLM-Korrekturen sollten nicht implizit in Markdown geschrieben werden.
- Provider-Rate-Limits brauchen CLI- und Env-gesteuertes Throttling.
- Der Orchestrator muss den aktuellen Sprachkontext weitergeben.
- Gemini/GenAI braucht ein aktuelles Default-Modell und korrekte
  `generateContent`-URLs.
- Die Kernpolicy sollte hexagonal testbar aus der Tool-IO-Schicht geloest werden.

## Umsetzung

- [x] Application-Slice `core/application/ai_reference_check.py` fuer
  Throttling, Secret-Redaction, Report-Summary und Exit-Code-Policy.
- [x] `ai_references.py` laedt optional `<root>/.env`, redigiert Secrets im
  JSON-Report und schreibt Aenderungen nur noch mit `--apply`.
- [x] CLI-Throttling ueber `--requests-per-minute`, `--min-request-interval`
  und `--throttle-jitter` plus Env-Fallbacks.
- [x] Adaptiver 429-Backoff mit `Retry-After`-Headern und begrenztem
  Exponential-Fallback.
- [x] Mistral-API-Adapter mit `MISTRAL_API_KEY`/`MISTRAL_KEY`, Default-Endpoint
  `https://api.mistral.ai/v1/chat/completions` und Default-Modell
  `mistral-small-latest`.
- [x] GenAI-Default auf `gemini-2.5-flash` und robuste
  `models/<model>:generateContent`-URL-Ableitung.
- [x] Optionaler CI-Hard-Fail mit `--fail-on-failed` und Exit-Code 44.
- [x] Orchestrator reicht `ctx.language_id` und vorhandene `content/SUMMARY.md`
  an den AI-Reference-Check weiter.
- [x] Testcontent unter `de-ref-check/content` mit guten, fehlerhaften und
  exotischen Referenzformen.
- [x] Unit-Tests ohne Netzwerk fuer Throttling, Secret-Redaction,
  report-only/apply-Verhalten, Env-Laden und GenAI-URL.

## Folgearbeiten

- [ ] Deterministische Vorpruefungen fuer URL, DOI, ISBN, arXiv und interne
  Markdown-Links vor jedem LLM-Aufruf einbauen.
- [ ] Optional SARIF oder GitHub-Step-Summary aus dem JSON-Report erzeugen.
- [ ] Provider-Adapter weiter entkoppeln, falls weitere Backends produktiv
  genutzt werden.
- [ ] Cache fuer identische Referenzzeilen einfuehren, um Kosten und Rate-Limits
  weiter zu senken.

## Manuelle Pruefung

Mit vorhandener `.env` kann ein vorsichtiger Smoke-Lauf so gestartet werden:

```bash
python -m gitbook_worker.tools.quality.ai_references \
  --root . \
  --files de-ref-check/content/standard-good.md de-ref-check/content/broken-references.md de-ref-check/content/exotic-references.md \
  --language de \
  --ai-provider genai \
  --model gemini-2.5-flash \
  --requests-per-minute 12 \
  --json-report de-ref-check/publish/reports/ai-reference-smoke.json \
  --no-progress
```

Ohne `--apply` bleibt der Lauf report-only.
