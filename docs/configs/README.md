---
version: 1.0.0
date: 2026-02-08
history:
  - "1.0.0: 2026-02-08 — Initial index"
---

# Konfigurationsdatei-Referenz / Config File Reference

Jede Konfigurationsdatei hat ein eigenes Dokument mit Zweck, Schema-Version,
Schlüssel-Tabelle und Änderungshistorie.

| Datei | Schema-Version | Ort | Dok |
|-------|---------------|-----|-----|
| `content.yaml` | 1.0.0 | Repo-Root | [content-yaml.md](content-yaml.md) |
| `publish.yml` | 0.1.1 | `<lang>/publish.yml` | [publish-yml.md](publish-yml.md) |
| `book.json` | – (kein Feld) | `<lang>/book.json` | [book-json.md](book-json.md) |
| `fonts.yml` | 1.0.0 | `gitbook_worker/defaults/` | [fonts-yml.md](fonts-yml.md) |
| `frontmatter.yml` | 1.0.0 | `gitbook_worker/defaults/` | [frontmatter-yml.md](frontmatter-yml.md) |
| `readme.yml` | 1.0.0 | `gitbook_worker/defaults/` | [readme-yml.md](readme-yml.md) |
| `smart.yml` | 1.0.0 | `gitbook_worker/defaults/` | [smart-yml.md](smart-yml.md) |
| `docker_config.yml` | – (fehlt!) | `gitbook_worker/defaults/` | [docker-config-yml.md](docker-config-yml.md) |

> **Hinweis**: `docker_config.yml` und `book.json` haben kein `version`-Feld.
> Laut Config-Completeness-Policy (AGENTS.md §25) muss ein `version`-Feld
> ergänzt werden — siehe Backlog.

## Verwandte Dokumente

- [docs/configuration-reference.md](../configuration-reference.md) — Kompakt-Referenz aller Schlüssel
- [AGENTS.md](../../AGENTS.md) §25–28 — Config-Completeness-Policy
- [Backlog: Config Completeness](../../gitbook_worker/docs/backlog/config-completeness-and-documentation.md)
