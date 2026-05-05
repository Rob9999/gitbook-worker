---
version: 0.1.0
date: 2026-05-05
status: draft
history:
  - version: 0.1.0
    date: 2026-05-05
    description: Initialer Release- und Backlog-Arbeitsplan fuer v2.4.0 mit PDF-Font-/Emoji-Gates
---

# Release-Plan v2.4.0

## Ziel

v2.4.0 soll ein Stabilitaets- und QA-Release werden. Der Schwerpunkt liegt auf
zwei Achsen:

1. PDF-Regressionssicherheit fuer Emoji-, ERDA-CJK- und LuaLaTeX-Fallbacks.
2. AI-Reference-Check als auditierbares Provider-Werkzeug mit OpenAI-kompatibel,
   Gemini/GenAI und Mistral.

Ein groesserer Scope kann als `v2.4.x` fortgesetzt werden, wenn nach den
kritischen Gates noch Backlog-Arbeit offen bleibt.

## Arbeitsregel fuer diesen Release

- Jede fachliche Aenderung wird zuerst committed.
- Danach folgt direkt ein PDF-Build.
- Der PDF-Build gilt erst als geprueft, wenn mindestens diese Signale vorliegen:
  - `TwemojiMozilla` ist im PDF eingebettet.
  - `ERDACCbyCJK-Regular` ist im PDF eingebettet.
  - CJK-Zeichen werden im PDF-Textscan gefunden.
  - Build-Logs enthalten keine neuen fontbezogenen Fatal- oder Missing-Glyph-
    Regressionen gegenueber dem bekannten Stand.
- Generierte Timestamp-Artefakte werden nicht als Feature-Aenderung committet,
  ausser der Release-Prozess verlangt dies explizit.

## Priorisierung aus dem Backlog

### P0: PDF-Font-/Emoji-Regressionsgate

Quelle: `gitbook_worker/docs/backlog/publish-yml-comprehensive-testing.md`

Erste umsetzbare Scheibe:

- PDF-Font-Validator als kleines Testing-Utility erstellen.
- Fonts aus der aktuellen Konfiguration ableiten, nicht hart auf konkrete Namen
  in Tests verdrahten.
- Test fuer `TwemojiMozilla`/konfigurierten Emoji-Font und ERDA-CJK-Einbettung
  an den bestehenden Sample-PDFs oder einem fokussierten Smoke-PDF aufsetzen.
- Ergebnis als Release-Gate dokumentieren.

### P1: AI-Reference-Check Provider- und Kostenhaertung

Quelle: `gitbook_worker/docs/backlog/ai-reference-check-hardening.md`

Bereits fuer v2.4.0 erledigt:

- Report-only Default und `--apply`.
- Secret-Redaction.
- Statisches Throttling.
- Adaptiver 429-Backoff ueber `Retry-After`.
- Gemini/GenAI Default `gemini-2.5-flash`.
- Mistral-Provider ueber `mistral`/`mistral-ai`.

Naechste Scheibe:

- Deterministische Vorpruefung fuer URL, DOI, ISBN, arXiv und interne Markdown-
  Links, damit LLM-Calls nur fuer unklare Faelle genutzt werden.
- Cache fuer identische Referenzzeilen.
- Optional GitHub-Step-Summary oder SARIF.

### P1: ERDA-CJK Coverage sichtbar machen

Quellen:

- `gitbook_worker/docs/backlog/erda-ccby-cjk-glyph-coverage.md`
- `gitbook_worker/docs/backlog/erda-ccby-cjk-docs.md`

Naechste Scheibe:

- Dokumentierte Coverage-Matrix fuer konfigurierte ERDA-Fonts.
- Klare Diagnose: Font eingebettet vs. Glyph tatsaechlich abgedeckt.
- Recovery-Schritte bei LuaTeX-Cache- oder Font-Version-Mismatch.

### P2: Packaging/Pip-Installierbarkeit

Quelle: `gitbook_worker/docs/backlog/pip-install-roadmap.md`

Naechste Scheibe nach P0/P1:

- Versionierungsquelle klaeren.
- Package-Data fuer Defaults/Lua/Templates absichern.
- Wheel-Smoke in CI vorbereiten.

### P2: Font-Storage-Dynamik

Quelle: `gitbook_worker/docs/backlog/font-storage-dynamic-generation.md`

Diese Arbeit bleibt nachrangig, bis das PDF-Regressionsgate steht. Sie beruehrt
Font-Pfade und darf nur mit enger PDF-Pruefschleife umgesetzt werden.

## Release-Kandidaten-Checkliste

- [ ] P0 PDF-Font-/Emoji-Gate implementiert.
- [ ] AI-Reference Mistral-Provider dokumentiert und getestet.
- [ ] AI-Reference Vorpruefung oder Cache mindestens als erste Scheibe umgesetzt
      oder bewusst auf v2.4.x verschoben.
- [ ] `python -m pytest gitbook_worker/tests -m "not slow"` dokumentiert.
- [ ] Lokaler PDF-Build fuer `de` erfolgreich.
- [ ] Font-Auswertung fuer `de/publish/das-sample-buch.pdf` dokumentiert.
- [ ] Optional lokaler PDF-Build fuer `en` erfolgreich.
- [ ] Release Notes `docs/releases/v2.4.0.md` erstellt.
- [ ] Version-Bump in `setup.cfg` und `gitbook_worker/__init__.py` entschieden.

## Aktueller Stand am 2026-05-05

- Kein bestehender v2.4.0-Release-Plan gefunden.
- Mistral-Provider wurde als erster Provider-Backlog-Schritt gestartet.
- Die wichtigste naechste technische Arbeit ist das P0-PDF-Regressionsgate.
