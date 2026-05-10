---
version: 1.0.0
date: 2026-05-10
status: delivery-evidence
target_release: "v2.9.0 Qualitaetskompass"
history:
  - "1.0.0: 2026-05-10 - Warnungsgruppen aus dem konfigurierten release-Lieferlauf dokumentiert."
---

# Editorial Quality Warning Groups

Diese Gruppierung schliesst Lieferpunkt 5. Sie verdichtet die CSV-Findings des
konfigurierten `release`-Laufs fuer die Kundenredaktion.

## Gesamtbild

| Dossier | Warnungen | Haupttreiber |
|---|---:|---|
| `de-release` | 195 | doppelte Headings, Release-Doku-Drift, lange Tokens |
| `en-release` | 172 | doppelte Headings, Release-Doku-Drift, lange Tokens |
| `project-release` | 546 | projektweiter Heading-Abgleich ueber beide Sprachbaeume |

## Kategorien nach Dossier

| Kategorie | `de-release` | `en-release` | `project-release` | Einordnung |
|---|---:|---:|---:|---|
| `markdown.structure` | 83 | 80 | 400 | Doppelte Titel erschweren Outline, Review-Kommunikation und Querverweise. |
| `markdown.layout` | 43 | 22 | 65 | Lange Tokens koennen Umbruch und Tabellenlayout belasten. |
| `release_docs.drift` | 58 | 58 | 58 | Historische Release-Dokumente nennen aeltere Worker-Versionen. |
| `publish.scope` | 8 | 4 | 12 | Markdown-Dateien oder Appendix-Reihenfolge passen nicht voll zum Publish-Scope. |
| `markdown.editorial` | 2 | 6 | 8 | Review-Marker oder offene redaktionelle Platzhalter bleiben sichtbar. |
| `metadata.consistency` | 1 | 1 | 2 | Manifest- und Markdown-Versionen wirken nicht deckungsgleich. |
| `markdown.frontmatter` | 0 | 1 | 1 | Frontmatter fehlt in einer EN-Datei. |

## Wichtigste Regeln

| Regel | `de-release` | `en-release` | `project-release` | Healing-Step |
|---|---:|---:|---:|---|
| `markdown.heading.duplicate_title` | 83 | 80 | 400 | Titel praezisieren oder bewusst gleiche Titel im Dossier begruenden. |
| `release_docs.worker_version.stale` | 58 | 58 | 58 | Historische Releases klar kennzeichnen oder aktuelle Releaseaussagen aktualisieren. |
| `markdown.long_token` | 43 | 22 | 65 | Lange Tokens umbrechen, als Code/URL behandeln oder Tabellenstrategie pruefen. |
| `publish.summary.orphaned_markdown` | 7 | 3 | 10 | Datei in SUMMARY aufnehmen, bewusst ausschliessen oder aus dem Scope verschieben. |
| `markdown.review_marker` | 2 | 6 | 8 | TODO/FIXME/REVIEW klaeren oder als Restrisiko dokumentieren. |
| `publish.summary.appendix_order` | 1 | 1 | 2 | SUMMARY-Reihenfolge oder `summary_appendices_last` pruefen. |
| `metadata.version_mismatch` | 1 | 1 | 2 | Manifest- und Markdown-Versionen angleichen oder Abweichung begruenden. |
| `markdown.frontmatter.missing` | 0 | 1 | 1 | Frontmatter ergaenzen oder Datei aus dem Profil ausnehmen. |

## Redaktionelle Priorisierung

| Prioritaet | Gruppen | Empfehlung |
|---|---|---|
| P1 | `markdown.layout`, `publish.scope`, `markdown.editorial` | Vor Kundenfreigabe stichprobenartig pruefen, weil Layout, Vollstaendigkeit und offene Notizen betroffen sind. |
| P2 | `markdown.structure`, `metadata.consistency` | Review-Kommunikation verbessern; bei Sample-Inhalten teils akzeptierbar, wenn bewusst dokumentiert. |
| P3 | `release_docs.drift` | Historische Release-Dokumente separat bewerten; fuer aktuelle Releaseaussagen darf keine Verwechslung bleiben. |

## Nicht-Warnungen

Die `info`-Signale bleiben sichtbar, sind aber nicht gate-relevant: PDF-TOC-
Abweichungen ohne direkten Markdown-Heading-Treffer, Tabellenstrategie-
Kandidaten, AI-Referenzkandidaten und Script-Sample-Signale fuer CJK/Hangul/Kana.
Die Font-/Glyphenprobleme sind keine Warnungen, sondern `fail` und werden in
der Fail-Offenlegung separat behandelt.