---
title: Kapitel 2 – Vergleichstabellen
date: 2024-06-01
version: 1.0
doc_type: chapter
chapter_number: 2
---

# Kapitel 2 – Vergleichstabellen

Die folgenden Tabellen zeigen, wie neutrale Datensätze strukturiert werden können. Alle Werte sind illustrative Mittelwerte und lassen sich problemlos durch reale Messreihen ersetzen.

## 2.1 Übersichtstabelle
| Messpunkt | Woche 1 | Woche 2 | Woche 3 | Woche 4 |
|-----------|---------|---------|---------|---------|
| Temperaturmittel (°C) | 18.2 | 18.5 | 18.4 | 18.3 |
| Luftfeuchte (%) | 52 | 53 | 51 | 52 |
| Lichtstunden | 14 | 14 | 13 | 13 |

## 2.2 Format-Beispiel für Verhältnisse
| Kategorie | Anteil am Gesamtvolumen | Notiz |
|-----------|------------------------|-------|
| Messwerte mit direktem Sensorbezug | 40 % | Sensoren nach ISO 17025 kalibriert |
| Berechnete Richtwerte | 35 % | Ableitung über gleitende Mittelwerte |
| Kontextdaten | 25 % | Stammen aus öffentlichen Katalogen[^2] |

Die Tabellen können als CSV exportiert oder in [Appendix A](../appendices/appendix-a.md#tabellenlayout) erneut eingesehen werden. Verlinke interne Abschnitte immer mit relativen Pfaden, damit das Buch offline funktioniert.

## 2.3 Referenz auf Abbildungen
![Rasterdarstellung der Messpunkte](../.gitbook/assets/neutral-grid.svg)

Die Abbildung verdeutlicht, wie Messzonen schematisch gezeigt werden können, ohne reale Orte zu benennen.

Zur Überprüfung einer eingebetteten HTML-Inlay-Variante kann zusätzlich die folgende Figur verwendet werden:

<div><figure><img src="../.gitbook/assets/ERDA_Logo_simple.png" alt="ERDA Logo"><figcaption><p>ERDA logo</p></figcaption></figure></div>

[^2]: Vgl. die referenzierten offenen Kataloge in [Zitationen & weiterführende Quellen](../references.md).
