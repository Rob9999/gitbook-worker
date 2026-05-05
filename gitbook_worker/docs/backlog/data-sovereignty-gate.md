---
version: 0.1.0
date: 2026-05-05
status: draft
priority: high
labels: [quality, privacy, data-sovereignty, release-gate, compliance]
history:
  - "0.1.0: 2026-05-05 - Eigenen Vorschlag fuer ein Data-Sovereignty-Gate als Backlog-Draft angelegt"
---

# Backlog: Data-Sovereignty-Gate fuer technische EU-/Privacy-Pruefung

## Kurzfazit

Ein technisches Data-Sovereignty-Gate passt gut zu GitBook Worker, aber es soll
nicht als juristischer EU-Konformitaetsbeweis verkauft werden. Der passende
Scope ist: reproduzierbare technische Pruefung auf harte Nicht-EU-Defaults,
stille Provider-Fallbacks, oeffentliche CDN-/Analytics-Endpunkte und fehlende
Privacy-Schutzsignale in Reports.

Dieser Draft ist eine eigenstaendige Spezifikation fuer dieses Repository. Er
uebernimmt keinen Code aus privaten Projekten, sondern beschreibt eine neue,
repo-spezifische Umsetzungsidee.

## Ziel

GitBook Worker soll vor Releases und optional in CI einen auditierbaren Report
erzeugen koennen, der technische Data-Sovereignty-Risiken sichtbar macht:

- hart verdrahtete US- oder globale Cloud-/AI-Endpunkte,
- stille Fallbacks auf nicht freigegebene Provider oder Regionen,
- oeffentliche CDN-, Font- oder Analytics-Endpunkte in produktiven Defaults,
- Default-Dependencies auf nicht-EU Provider-SDKs,
- fehlende oder unklare Dokumentation fuer bewusst optionale Provider,
- Secret-Leakage-Risiken in Reports, Fehlertexten oder Logs.

Das Gate soll als Release-Beleg funktionieren: JSON-Report, stabile
Regelversion, Tree-Digest, Report-Digest und klare Exit-Codes.

## Nicht-Ziele

- Kein Rechtsgutachten und keine automatische DSGVO-/EU-Rechtskonformitaet.
- Kein pauschales Verbot optionaler Provider-Adapter wie OpenAI, Gemini oder
  Mistral, solange sie nicht als harter Default oder stiller Fallback wirken.
- Kein verpflichtender Commit-Hook in der ersten Scheibe.

## Vorgeschlagene erste Scheibe

Neues Tool:

```text
gitbook_worker.tools.quality.data_sovereignty_gate
```

Beispielaufruf:

```powershell
python -m gitbook_worker.tools.quality.data_sovereignty_gate `
  --git-tracked `
  --json-report logs/data-sovereignty-gate.json `
  --check
```

Report-Felder:

```json
{
  "tool": "data_sovereignty_gate",
  "tool_version": "0.1.0",
  "status": "PASS",
  "timestamp_utc": "2026-05-05T00:00:00+00:00",
  "requested_paths": ["--git-tracked"],
  "files_scanned": 0,
  "findings_count": 0,
  "ruleset_sha256": "...",
  "tree_sha256": "...",
  "report_sha256": "...",
  "findings": []
}
```

## Regelentwurf

### DS-001: Harte Nicht-EU-Region als produktiver Default

Findet verwendbare Defaults wie `AWS_REGION=us-east-1`, `AZURE_REGION=eastus`,
`location: westus2` oder vergleichbare US-only Regionen in Konfigurations- und
Skriptpfaden.

Unterdrueckung nur, wenn der Treffer klar als Risiko, Negativbeispiel,
Ausschluss oder Testfixture markiert ist.

### DS-002: Globaler AI-Endpunkt als Default oder Fallback

Findet Endpunkte wie `api.openai.com`, `api.anthropic.com` oder
`generativelanguage.googleapis.com`, wenn sie als sofort nutzbarer Default,
Fallback oder Failover erscheinen.

Wichtig fuer GitBook Worker: optionale Provider-Adapter sind erlaubt, aber sie
muessen report-first, secret-redacted und explizit konfigurierbar bleiben.

### DS-003: Stiller Fallback auf nicht freigegebenen Provider

Findet Logik, die bei Fehlern automatisch zu globalen AI-Providern,
US-Regionen oder oeffentlichen Endpunkten wechselt, ohne CLI-/Config-Opt-in und
ohne deutlichen Report-Hinweis.

### DS-004: Oeffentliche CDN-, Font- oder Analytics-Endpunkte

Findet produktive Defaults auf `fonts.googleapis.com`, `fonts.gstatic.com`,
`google-analytics.com`, `googletagmanager.com`, `cdn.jsdelivr.net`,
`unpkg.com` oder vergleichbare externe Runtime-Abhaengigkeiten.

Fuer GitBook Worker ist besonders wichtig: Font-Quellen duerfen dokumentiert und
downloadbar sein, aber PDF-Builds sollen keine stillen Runtime-CDN-Abhaengigkeiten
haben.

### DS-005: Nicht-EU Provider-SDK in Default-Dependencies

Findet Provider-SDKs wie `openai` oder `anthropic`, wenn sie in
Default-Installationspfaden auftauchen. Optional dokumentierte Extras waeren nur
dann ok, wenn sie nicht automatisch installiert werden und ein Privacy-Hinweis
vorhanden ist.

### DS-006: Secret-Sanitizer-Regressionssignal fehlt

Prueft, ob AI-/Provider-Reports weiterhin technische Secret-Redaction abdecken.
Die erste Umsetzung kann statisch auf vorhandene Tests und Tool-Funktionen
pruefen, spaeter mit einem kleinen Fixture-Report.

Aktuelle Anker im Repo:

- `core/application/ai_reference_check.py`: `redact_secrets`
- `tools/quality/ai_references.py`: Provider-Fehler-Sanitizer
- `tests/test_ai_references.py`: Redaction-Regressionen

## Scoping und Suppression

Das Gate soll git-getrackte Textdateien scannen, aber nicht jedes Vorkommen als
Fehler behandeln. Vorgeschlagene Regeln:

- Testfixtures und Rule-Quellen duerfen Treffer enthalten.
- Backlog-, Release- und Architektur-Doku duerfen Treffer enthalten, wenn der
  Kontext klar Risiko, Verbot, Ausschluss, Beispiel oder Follow-up benennt.
- Produktive Defaults, Dockerfiles, Workflow-Dateien, Package-Metadaten und
  Runtime-Code sind strenger zu behandeln.
- Grossdateien und binaere Artefakte werden ausgelassen.

## Exit-Code-Vorschlag

Die endgueltigen Codes muessen bei Umsetzung in
`gitbook_worker/docs/attentions/exit-codes.md` und in die CLI-Hilfe aufgenommen
werden.

| Code | Bedeutung |
|------|-----------|
| 0 | Gate sauber oder Bericht erfolgreich erzeugt |
| 45 | Data-Sovereignty-Findings gefunden |
| 46 | Konfigurations-, Git- oder IO-Fehler im Gate |

## Dokumentationsanker

Bei Umsetzung sollen diese Stellen aktualisiert werden:

- `docs/customer-installation.md`: Kundenhinweis zu technischem Gate und Grenzen.
- `docs/HANDBOOK.md`: Entwicklungs- und Release-Workflow.
- `gitbook_worker/docs/how-to-release/release-procedure.md`: Release-Gate-Schritt.
- `docs/releases/<version>.md`: Verifikationsstatus.
- `gitbook_worker/docs/attentions/exit-codes.md`: Exit-Code-Tabelle.

## Teststrategie

- Unit-Tests ohne Netzwerk fuer jede Regel.
- Fixture-Dateien fuer produktive Treffer, erlaubte Doku-Kontexte und Tests.
- JSON-Report-Snapshot mit stabilen Digests oder stabilisierter Uhr.
- CLI-Test fuer `--check`, `--json-report`, `--paths` und `--git-tracked`.
- Regression, dass optionale AI-Provider-Dokumentation nicht faelschlich als
  produktiver Default blockiert wird.

## Phasenplan

### Phase 1: Report-only Gate

- Tool implementieren.
- Regeln DS-001 bis DS-006 als erste Scheibe.
- JSON-Report und Exit-Codes.
- Release-Doku und Customer Guide ergaenzen.
- Nicht automatisch commithookend.

### Phase 2: CI-Integration

- GitHub Actions Step als nicht-destruktiver Check.
- Optional zunaechst warnend, danach hard-fail fuer produktive Defaults.
- Artefakt-Upload des JSON-Reports.

### Phase 3: Commit-Proof optional

- Optionaler `--write-proof`-Modus.
- Optionaler Commit-Message-Trailer.
- Nur einfuehren, wenn der Workflow im Repo stabil genug ist und keine
  Entwicklerergonomie bricht.

## Offene Produktfragen

- Soll das Gate fuer v2.4.x warnend starten oder direkt hard-failen?
- Sollen AI-Provider-SDKs in optionalen Extras erlaubt werden?
- Welche EU-Provider/Regionen gelten als ausdruecklich freigegeben?
- Brauchen wir Projektkonfiguration fuer erlaubte Provider statt harter Listen?
- Soll der Report in `logs/`, `publish/reports/` oder `.git/` gespeichert werden?

## Meine Empfehlung

Als naechste Scheibe nach v2.4.0 lohnt sich Phase 1: report-only,
netzwerkfrei, gut getestet, ohne Commit-Trailer. Damit bekommen wir ein starkes
technisches Release-Signal, ohne kurz vor Release juristische Behauptungen oder
schwere Hook-Mechanik einzubauen.