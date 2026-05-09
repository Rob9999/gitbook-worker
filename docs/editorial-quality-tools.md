---
version: 1.0.0
date: 2026-05-09
history:
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

## Exit-Codes

- `45`: harte redaktionelle Findings.
- `46`: blockierende fehlende Artefakte.
- `47`: Metrikreport nicht lesbar.
- `48`: ungueltiges Abnahmeprofil.

Beide neuen CLIs unterstuetzen `--help-exit-codes`.