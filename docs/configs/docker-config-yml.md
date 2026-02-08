---
version: 1.1.0
date: 2026-02-08
config_schema_version: "1.0.0"
history:
  - "1.1.0: 2026-02-08 — version-Feld ergänzt, SemVer-Validation in smart_merge.py"
  - "1.0.0: 2026-02-08 — Initial documentation"
---

# docker_config.yml

## Zweck

Template-basierte Namensvergabe für Docker-Images und -Container.
Verschiedene Kontexte (default, github-action, prod, test, docker-test)
erhalten eigene Namens-Templates mit Platzhaltern.

## Ort

```
gitbook_worker/defaults/docker_config.yml     (System-Default)
<repo-root>/docker_config.yml                 (Override auf Repo-Ebene)
publish.yml → docker_config: { … }            (Override pro Publish-Entry)
```

## Schema-Version

Aktuell: **1.0.0** — Feld `version` (Top-Level).

Die Merge-Schicht in `smart_merge.py` validiert das `version`-Feld per SemVer
und gibt eine Warnung aus, falls es fehlt oder ungültig ist.

## Template-Variablen

| Variable | Beschreibung |
|----------|-------------|
| `{context}` | Ausführungskontext (github-action, prod, test, docker-test) |
| `{repo_name}` | Repository-Name (z. B. `Rob9999/erda-book`) |
| `{branch}` | Git-Branch |
| `{publish_name}` | Name aus publish.yml Publish-Entry |
| `{version}` | Versions-Tag (optional) |

## Schlüssel-Referenz

| Schlüssel | Typ | Default | Status | Beschreibung |
|-----------|-----|---------|--------|--------------|
| `version` | string | – | ✅ | SemVer-Schema-Version, beim Laden validiert |
| `docker_names.default.image` | string | `"erda-gitbook-{context}:{branch}"` | 🔨 | Nutzung in `run_docker.py` zu verifizieren |
| `docker_names.default.container` | string | `"erda-{context}-{publish_name}"` | 🔨 | Nutzung in `run_docker.py` zu verifizieren |
| `docker_names.github-action.image` | string | `"ghcr.io/{repo_name}/gitbook:{branch}"` | 📝 | Für CI-Workflows |
| `docker_names.github-action.container` | string | `"gitbook-ci-{publish_name}-{branch}"` | 📝 | Für CI-Workflows |
| `docker_names.prod.image` | string | `"erda-gitbook:latest"` | 📝 | Für Produktion |
| `docker_names.prod.container` | string | `"erda-gitbook-prod"` | 📝 | Für Produktion |
| `docker_names.test.image` | string | `"erda-gitbook-test:local"` | 🔨 | Für pytest |
| `docker_names.test.container` | string | `"erda-test-{publish_name}"` | 🔨 | Für pytest |
| `docker_names.docker-test.image` | string | `"erda-gitbook-dockertest:latest"` | 🔨 | Für Integrationstests |
| `docker_names.docker-test.container` | string | `"erda-dockertest-{publish_name}"` | 🔨 | Für Integrationstests |

## Offene Punkte

- **`default.*`** — Verifizieren, ob `run_docker.py` diese Templates tatsächlich interpoliert
- **`test.*` und `docker-test.*`** — Verifizieren ob pytest-Fixtures diese lesen

## Versionshistorie

| Version | Datum | Änderung |
|---------|-------|----------|
| 1.0.0 | 2026-02-08 | `version`-Feld ergänzt, SemVer-Validation |
| – | 2025-12-05 | Initiale Konfiguration (ohne Versionsfeld) |

## Verwandte Dokumente

- [publish-yml.md](publish-yml.md) — Docker-Profile in publish.yml
