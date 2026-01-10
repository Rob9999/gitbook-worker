---
title: Font Attribution Generator
version: 1.0.0
date: 2026-01-10
history:
  - version: 1.0.0
    date: 2026-01-10
    changes: Initial user guide for generating ATTRIBUTION.md and LICENSE-* from fonts.yml
---

# Font Attribution Generator

GitBook Worker kann aus der zentralen Font-Konfiguration automatisch Attributions- und Lizenz-Dateien erzeugen.

## Was wird erzeugt?

In das `out_dir` des jeweiligen Publish-Targets werden geschrieben:

- `ATTRIBUTION.md`
- `LICENSE-CC-BY-4.0`
- `LICENSE-BITSTREAM-VERA`

Die Lizenztexte werden offline/deterministisch aus der Repository-Datei `LICENSE-FONTS` extrahiert.

## Voraussetzungen

- `fonts.yml` muss vollständig gepflegt sein (mindestens `name`, `license`, `license_url` pro Font).
- Die Fonts-Konfiguration ist standardmäßig: `gitbook_worker/defaults/fonts.yml`.

## Aktivierung über publish.yml (empfohlen)

### 1) Orchestrator-Profil: Step aktivieren

Wenn in `publish.yml` Profile mit expliziter `steps:`-Liste genutzt werden, muss der Step `generate_attribution` in diesen Profilen enthalten sein (typischerweise **vor** `publisher`).

Beispiel:

```yaml
profiles:
  local:
    steps:
      - converter
      - generate_attribution
      - publisher
```

### 2) Publish-Target: Generierung einschalten

Im passenden `publish:`-Eintrag:

```yaml
publish:
  - path: ./
    out_dir: ./publish
    out: the-erda-book.pdf
    build: true
    generate_attribution: true
```

Nur wenn `generate_attribution: true` gesetzt ist, wird im jeweiligen `out_dir` generiert.

## Manuelle Ausführung (CLI)

Zusätzlich gibt es einen direkten CLI-Befehl über das bestehende Font-Tool:

```bash
gitbook-worker-fonts generate-attribution --out-dir en/publish
```

Optionale Parameter:

- `--config <path>`: alternatives `fonts.yml`
- `--license-fonts <path>`: alternatives `LICENSE-FONTS`

Beispiel:

```bash
gitbook-worker-fonts generate-attribution --out-dir de/publish --config gitbook_worker/defaults/fonts.yml
```

## Troubleshooting

### “missing required fields”

Mindestens ein Font-Eintrag in `fonts.yml` hat kein `name`, `license` oder `license_url`. Bitte ergänzen.

### “Unsupported license for attribution generation”

Aktuell werden genau die Lizenzen unterstützt, die aus `LICENSE-FONTS` extrahiert werden (derzeit CC BY 4.0 und Bitstream Vera/DejaVu).

Wenn du neue Font-Lizenzen ergänzen willst, müssen:

1) die Lizenztexte in `LICENSE-FONTS` vorhanden sein, und
2) die Extraktion/Zuordnung im Generator erweitert werden.
