---
title: Appendix A – Data sources and table layout
date: 2024-06-01
version: 1.0
---

# Appendix A – Data sources and table layout

## A.1 Data sources
1. Public climate data catalogues from regional weather services.
2. Neutral example values from internal sandbox systems.
3. International open-data repositories such as [UN Data](https://data.un.org/) or [World Bank Open Data](https://data.worldbank.org/).

## A.2 Table layout
<a id="table-layout"></a>
| Column | Data type | Description |
|--------|----------|-------------|
| `timestamp` | ISO-8601 | Timestamp of the measurement |
| `metric` | String | Measurement (temperature, humidity, etc.) |
| `value` | Decimal number | Measured value |
| `unit` | String | Associated unit |
| `notes` | Free text | Context or notes |

## A.3 Reuse
- The table can be imported directly into dataframes.
- Use relative links such as [Chapter 2](../chapters/chapter-02.md) for cross-references.
- Graphics can be found in the [`content/.github/assets`](../images/) directory.
