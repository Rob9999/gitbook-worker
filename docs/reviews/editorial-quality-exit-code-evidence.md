---
version: 1.0.0
date: 2026-05-10
status: delivery-evidence
target_release: "v2.9.0 Qualitaetskompass"
history:
  - "1.0.0: 2026-05-10 - Exit-Code-Demo fuer editorial_acceptance dokumentiert."
---

# Editorial Quality Exit-Code Evidence

Diese Evidenz schliesst Lieferpunkt 6. Die Exit-Codes wurden mit temporaeren
BOM-freien JSON-Metrikreports gegen `editorial_acceptance` ausgefuehrt.

## Beobachtetes Ergebnis

| Demo-Fall | Erwarteter Status | Beobachteter Exit-Code | Bedeutung |
|---|---|---:|---|
| clean report | `passed` | 0 | Keine Findings, Gate kann passieren. |
| warn report | `passed_with_warnings` | 0 | Warnungen sind im Profil `local` nicht hart gate-relevant. |
| fail report | `failed` | 45 | Harte redaktionelle Findings. |
| blocked report | `blocked` | 46 | Blockierende fehlende oder unbrauchbare Artefakte. |

Zusaetzlich wurde im ersten Demo-Versuch unbeabsichtigt ein UTF-8-BOM-Report
erzeugt. Der Reader lehnte diesen Report ab und lieferte Exit-Code `47` fuer
einen nicht lesbaren Metrikreport. Das bestaetigt die Fehlerklasse ebenfalls.

## Stabile Exit-Codes

| Exit-Code | Komponente | Bedeutung | Healing-Step |
|---:|---|---|---|
| 0 | `editorial_acceptance` | `passed` oder `passed_with_warnings` | Dossier pruefen, Warnungen ggf. redaktionell akzeptieren. |
| 45 | `editorial_acceptance`, `editorial_metrics --fail-on-findings` | Harte Findings (`fail`) | Findings beheben oder explizit als Restrisiko dokumentieren. |
| 46 | `editorial_acceptance`, `editorial_metrics --fail-on-findings` | Blockierende Findings (`blocked`) | Fehlende/unlesbare Artefakte erzeugen oder Scope korrigieren. |
| 47 | `editorial_acceptance` | Metrikreport nicht lesbar | JSON-Encoding, Pfad und Schema pruefen; BOM-frei speichern. |
| 48 | beide CLIs | Ungueltiges Profil | Profilname oder `--profile-config` korrigieren. |

## Reproduktionshinweis

Bei Windows PowerShell 5.1 muss fuer JSON-Fixtures BOM-freies UTF-8 verwendet
werden, zum Beispiel:

```powershell
$utf8 = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText($reportPath, $json, $utf8)
```

`Set-Content -Encoding UTF8` erzeugt in dieser Umgebung eine BOM und ist fuer
diese Demo ungeeignet.