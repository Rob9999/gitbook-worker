---
version: 1.3.0
date: 2026-05-09
history:
  - "1.3.0: 2026-05-09 — editorial quality profile reference bumped to 1.1.0"
  - "1.2.0: 2026-05-09 — editorial quality profile reference added"
  - "1.1.1: 2026-05-09 — publish.yml schema version 0.1.3 for table_paper_strategy"
  - "1.1.0: 2026-02-08 — Schema-Versionen aktualisiert (book.json 1.0.0, docker_config.yml 1.0.0)"
  - "1.0.0: 2026-02-08 — Initial index"
---

# Konfigurationsdatei-Referenz / Config File Reference

Jede Konfigurationsdatei hat ein eigenes Dokument mit Zweck, Schema-Version,
Schlüssel-Tabelle und Änderungshistorie.

| Datei | Schema-Version | Ort | Dok |
|-------|---------------|-----|-----|
| `content.yaml` | 1.0.0 | Repo-Root | [content-yaml.md](content-yaml.md) |
| `publish.yml` | 0.1.3 | `<lang>/publish.yml` | [publish-yml.md](publish-yml.md) |
| `book.json` | 1.0.0 | `<lang>/book.json` | [book-json.md](book-json.md) |
| `fonts.yml` | 1.0.0 | `gitbook_worker/defaults/` | [fonts-yml.md](fonts-yml.md) |
| `frontmatter.yml` | 1.0.0 | `gitbook_worker/defaults/` | [frontmatter-yml.md](frontmatter-yml.md) |
| `readme.yml` | 1.0.0 | `gitbook_worker/defaults/` | [readme-yml.md](readme-yml.md) |
| `smart.yml` | 1.0.0 | `gitbook_worker/defaults/` | [smart-yml.md](smart-yml.md) |
| `docker_config.yml` | 1.0.0 | `gitbook_worker/defaults/` | [docker-config-yml.md](docker-config-yml.md) |
| editorial quality profile | 1.1.0 | CLI `--profile-config` | [editorial-quality-profile.md](editorial-quality-profile.md) |

Alle Konfigurationsdateien haben nun ein `version`-Feld (Config-Completeness-Policy AGENTS.md §29).

## Verwandte Dokumente

- [docs/configuration-reference.md](../configuration-reference.md) — Kompakt-Referenz aller Schlüssel
- [AGENTS.md](../../AGENTS.md) §25–28 — Config-Completeness-Policy
- [Backlog: Config Completeness](../../gitbook_worker/docs/backlog/config-completeness-and-documentation.md)
