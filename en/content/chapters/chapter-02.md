---
title: Chapter 2 – Comparative tables
date: 2024-06-01
version: 1.0
doc_type: chapter
chapter_number: 2
---

# Chapter 2 – Comparative tables

The following tables show how neutral datasets can be structured. All values are illustrative averages and can easily be replaced with real measurement series.

## 2.1 Overview table
| Measurement point | Week 1 | Week 2 | Week 3 | Week 4 |
|-----------|---------|---------|---------|---------|
| Mean temperature (°C) | 18.2 | 18.5 | 18.4 | 18.3 |
| Relative humidity (%) | 52 | 53 | 51 | 52 |
| Hours of daylight | 14 | 14 | 13 | 13 |

## 2.2 Format example for ratios
| Category | Share of total volume | Note |
|-----------|------------------------|-------|
| Measurements with direct sensor reference | 40% | Sensors calibrated to ISO 17025 |
| Derived reference values | 35% | Computed using moving averages |
| Context data | 25% | Sourced from public catalogues[^2] |

The tables can be exported as CSV or revisited in [Appendix A](../appendices/appendix-a.md#table-layout). Always link internal sections using relative paths so the book works offline.

## 2.3 Reference to figures
![Grid representation of measurement points](../.gitbook/assets/neutral-grid.svg)

The figure illustrates how measurement zones can be shown schematically without naming real locations.

To verify an embedded HTML inlay variant, the following figure can additionally be used:

<div><figure><img src="../.gitbook/assets/ERDA_Logo_simple.png" alt="ERDA Logo"><figcaption><p>ERDA logo</p></figcaption></figure></div>

[^2]: Cf. the referenced open catalogues in [Citations & further reading](../references.md).
