---
version: 1.0.0
date: 2026-05-09
history:
  - "1.0.0: 2026-05-09 — Accepted residual-risk register for editorial acceptance documented."
---

# editorial accepted findings

Optionale YAML- oder JSON-Datei fuer
`gitbook_worker.tools.quality.editorial_acceptance --accepted-findings`.

Sie dokumentiert bewusst akzeptierte Restrisiken anhand stabiler Finding-IDs.
Die Befunde werden dadurch nicht versteckt. Das Dossier markiert sie als
akzeptiert, zaehlt ungenutzte Registereintraege und erzeugt ein hartes Finding,
wenn eine Akzeptanz abgelaufen ist.

## Schema-Version

Aktuell: `version: 1.0.0`.

## Beispiel

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

## Schluessel

| Schluessel | Typ | Status | Beschreibung |
|---|---|---|---|
| `version` | string | ✅ | SemVer der Datei |
| `accepted_findings` | array | ✅ | Liste bewusst akzeptierter Findings |
| `accepted_findings[].finding_id` | string | ✅ | Exakte Finding-ID aus dem Metrikreport |
| `accepted_findings[].reason` | string | ✅ | Begruendung der Akzeptanz |
| `accepted_findings[].role` | string | ✅ | Rolle der akzeptierenden Person |
| `accepted_findings[].date` | string | ✅ | Datum der Entscheidung (`YYYY-MM-DD`) |
| `accepted_findings[].expires` | string | ✅ | Ablaufdatum der Akzeptanz |
| `accepted_findings[].release` | string | ✅ | Optionaler Releasebezug |

## Status

✅ Implementiert:

- Einlesen ueber `--accepted-findings`.
- Matching ueber `finding_id`.
- Dossier-Markierung aktiver Akzeptanzen.
- harte Findings fuer abgelaufene Akzeptanzen.
- Warnungen fuer unvollstaendige Akzeptanzdatensaetze.
- Zaehlen nicht mehr passender Registereintraege.