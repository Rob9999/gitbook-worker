---
title: Appendix A – Datenquellen und Tabellenlayout
date: 2024-06-01
version: 1.0
doc_type: appendix
appendix_id: "A"
category: "technical"
---

# Appendix A – Datenquellen und Tabellenlayout

## A.1 Datenquellen
1. Öffentliche Klimadatenkataloge regionaler Wetterdienste.
2. Neutrale Beispielwerte aus firmeninternen Sandbox-Systemen.
3. Internationale Open-Data-Repositorien wie [UN Data](https://data.un.org/) oder [World Bank Open Data](https://data.worldbank.org/).

## A.2 Tabellenlayout
<a id="tabellenlayout"></a>
| Spalte | Datentyp | Beschreibung |
|--------|----------|--------------|
| `timestamp` | ISO-8601 | Zeitstempel der Messung |
| `metric` | String | Messgröße (Temperatur, Feuchte, etc.) |
| `value` | Dezimalzahl | Gemessener Wert |
| `unit` | String | Zugehörige Einheit |
| `notes` | Freitext | Kontext oder Hinweise |

## A.3 Weiterverwendung
- Die Tabelle kann direkt in Dataframes importiert werden.
- Nutze relative Links wie [Kapitel 2](../chapters/chapter-02.md) für Querverweise.
- Grafiken finden sich im Verzeichnis [`content/.github/assets`](../images/).
