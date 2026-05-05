---
version: 1.2.0
date: 2026-05-05
status: draft
history:
  - version: 1.2.0
    date: 2026-05-05
    description: Anwenderanleitung v2.4.0 als review-ready Release-Artefakt und finale Testzahlen dokumentiert.
  - version: 1.1.0
    date: 2026-05-05
    description: Paket-Hygiene, sauberer Wheel-Inhalt und Wheel-Smoke fuer v2.4.0 dokumentiert.
  - version: 1.0.1
    date: 2026-05-05
    description: Finale PDF-Gate-Dokumentation auf robuste CJK-Signalformulierung umgestellt.
  - version: 1.0.0
    date: 2026-05-05
    description: Version-Bump auf 2.4.0 und finale DE/EN PDF-Gates dokumentiert.
  - version: 0.9.0
    date: 2026-05-05
    description: Non-slow Testsuite nach Dockerfix erfolgreich dokumentiert.
  - version: 0.8.0
    date: 2026-05-05
    description: Dockerfile.dynamic gegen CTAN-TeX-Live-Jahreswechsel gehaertet.
  - version: 0.7.0
    date: 2026-05-05
    description: AI-Reference Inline-Erkennung, Precheck, Batch/Resume, Ergebnisstatus und PDF-JSON-Fix in v2.4.0 aufgenommen.
  - version: 0.6.0
    date: 2026-05-05
    description: Kundenfeedback aus v2.0.1-Nutzung aufgenommen; as-of-date und AI_* Kompatibilitaet als v2.4.0-Scheibe markiert.
  - version: 0.5.0
    date: 2026-05-05
    description: Log-Gate auf warnenden Default mit explizitem --fail-on-log-pattern-Ratchet umgestellt
  - version: 0.4.0
    date: 2026-05-05
    description: PDF-Gate um optionale Missing-Glyph-/notdef-Logpruefung erweitert; Verzeichnisse pruefen den neuesten Log-Satz
  - version: 0.3.0
    date: 2026-05-05
    description: Englischen PDF-Build und Font-Gate als erfolgreich verifiziert dokumentiert
  - version: 0.2.0
    date: 2026-05-05
    description: PDF-Font-Gate als implementierte P0-Scheibe und Release-Run-Kommando dokumentiert
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

- [x] PDF-Font-Validator als kleines Testing-Utility erstellen.
- [x] Fonts aus der aktuellen Konfiguration ableiten, nicht hart auf konkrete Namen
  in Tests verdrahten.
- [x] Test fuer `TwemojiMozilla`/konfigurierten Emoji-Font und ERDA-CJK-Einbettung
  an den bestehenden Sample-PDFs oder einem fokussierten Smoke-PDF aufsetzen.
- [x] Ergebnis als Release-Gate dokumentieren.

Release-Run-Kommando:

```powershell
python -m gitbook_worker.tools.testing.pdf_validator --pdf de/publish/das-sample-buch.pdf
python -m gitbook_worker.tools.testing.pdf_validator --pdf en/publish/the-sample-book.pdf
python -m gitbook_worker.tools.testing.pdf_validator --pdf de/publish/das-sample-buch.pdf --log de/publish/_latex-debug
```

`--log` meldet bekannte Missing-Glyph-Signale zunaechst als Warnung. Sobald eine
saubere oder akzeptierte Baseline vorliegt, kann `--fail-on-log-pattern` als
harter Ratchet aktiviert werden.

### P1: AI-Reference-Check Provider- und Kostenhaertung

Quelle: `gitbook_worker/docs/backlog/ai-reference-check-hardening.md`

Bereits fuer v2.4.0 erledigt:

- Report-only Default und `--apply`.
- Secret-Redaction.
- Statisches Throttling.
- Adaptiver 429-Backoff ueber `Retry-After`.
- Gemini/GenAI Default `gemini-2.5-flash`.
- Mistral-Provider ueber `mistral`/`mistral-ai`.
- Kundenkompatible Aliase fuer Throttling/429: `--delay-seconds`,
  `--jitter-seconds`, `--cooldown-on-429-seconds`, `--max-consecutive-429`.
- `--as-of-date YYYY-MM-DD` mit erzwungenem `validation_date` im Ergebnis.
- Env-Aliase `AI_API_KEY`, `AI_URL`, `AI_PROVIDER`.
- Inline-Erkennung fuer Bare URLs/DOIs, optionale Markdown-Links und optionale
  Frontmatter-DOIs.
- No-network Precheck fuer URL-/DOI-/arXiv-/ISBN-Syntax und interne
  Markdown-Links.
- Batch/Resume: `--files-list`, `--max-tasks`, `--resume-from-report`.
- Berichtszustaende `suggested`, `validated`, `failed`, `rate_limited`; ein
  Vorschlag wird nicht mehr als Reparatur gezaehlt, solange `--apply` ihn nicht
  schreibt.

Naechste Scheibe:

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

Bereits fuer v2.4.0 erledigt:

- Versionierungsquelle klaeren.
- `gitbook_worker.tests` aus der Paket-Discovery ausschliessen.
- `MANIFEST.in` prune fuer Testfixtures und Cache-Artefakte ergaenzen.
- Sauberen lokalen Wheel-Build aus leerem `build/`/`dist/` pruefen.
- Wheel-Inhalt verifizieren: keine Tests, keine `__pycache__`-Eintraege;
  TeXMF-Daten inklusive `deeptex.sty` weiterhin enthalten.
- Wheel-Smoke in frischem temporaerem Venv: Installation, Version `2.4.0`,
  `workflow_orchestrator --help`.

Naechste Scheibe nach v2.4.0:

- Package-Data fuer Archiv-/Engineering-Dokumente weiter verkleinern, falls das
  Distributionsartefakt schlanker werden soll.
- Wheel-Smoke in CI vorbereiten.

### P1: Docker-Image gegen TeX-Live-Jahreswechsel haerten

Quelle: Non-slow-Testlauf am 2026-05-05

- [x] `Dockerfile.dynamic` loest den installierten TeX-Live-Pfad dynamisch auf.
- [x] Stabiler Symlink `/usr/local/texlive/current` ersetzt harte
  Jahrespfade wie `/usr/local/texlive/2025`.
- [x] Statischer Regressionstest verhindert neue hartcodierte TeX-Live-Jahre.

### P2: Font-Storage-Dynamik

Quelle: `gitbook_worker/docs/backlog/font-storage-dynamic-generation.md`

Diese Arbeit bleibt nachrangig, bis das PDF-Regressionsgate steht. Sie beruehrt
Font-Pfade und darf nur mit enger PDF-Pruefschleife umgesetzt werden.

## Release-Kandidaten-Checkliste

- [x] P0 PDF-Font-/Emoji-Gate implementiert.
- [x] AI-Reference Mistral-Provider dokumentiert und getestet.
- [x] AI-Reference Kundenfeedback v2.0.1 triagiert und erste Must-have-Scheibe umgesetzt.
- [x] AI-Reference Vorpruefung oder Cache mindestens als erste Scheibe umgesetzt
      oder bewusst auf v2.4.x verschoben.
- [x] `python -m pytest gitbook_worker/tests -m "not slow"` dokumentiert.
- [x] Lokaler PDF-Build fuer `de` erfolgreich.
- [x] Font-Auswertung fuer `de/publish/das-sample-buch.pdf` dokumentiert.
- [x] Optional lokaler PDF-Build fuer `en` erfolgreich.
- [x] Release Notes `docs/releases/v2.4.0.md` erstellt.
- [x] Zentrale Anwenderanleitung `docs/customer-installation.md` fuer v2.4.0
  auf `review-ready` ausgebaut.
- [x] Version-Bump in `setup.cfg` und `gitbook_worker/__init__.py` entschieden.
- [x] Sauberer Package-Build und Wheel-Smoke fuer `2.4.0` erfolgreich.
- [x] Docker-Tests inklusive `Dockerfile.dynamic` Build/Run erfolgreich.

## Aktueller Stand am 2026-05-05

- Kein bestehender v2.4.0-Release-Plan gefunden.
- Mistral-Provider ist implementiert und gezielt getestet.
- Kundenfeedback aus produktiver v2.0.1-Nutzung ist in
  `gitbook_worker/docs/backlog/customer-v2-0-1-ai-reference-feedback.md`
  triagiert.
- Das P0-PDF-Regressionsgate ist als erste Scheibe implementiert und fuer `de`
  und `en` erfolgreich geprueft.
- Die naechste technische Arbeit ist die AI-Reference-Vorpruefung/Cache-Scheibe
  oder die Integration des PDF-Gates in CI/Workflow-Orchestrator-Profile.
- Non-slow Testsuite nach Dockerfix: 515 passed, 11 skipped, 10 deselected,
  4 warnings.
- Docker-Tests inklusive echtem `Dockerfile.dynamic` Build/Run: 4 passed.
- Finale DE/EN PDF-Font-Gates: Twemoji und ERDA-CJK eingebettet, positiver
  CJK-Textscan in beiden PDFs.
- Sauberer v2.4.0-Paketbuild: Wheel enthaelt keine Tests und keine
  `__pycache__`-Eintraege; Wheel-Smoke in frischem Temp-Venv erfolgreich.
- Zentrale Anwenderanleitung fuer v2.4.0 ist in
  `docs/customer-installation.md` review-ready und im Docs-Index verlinkt.
