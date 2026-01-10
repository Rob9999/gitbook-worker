---
title: Startseite
description: Übersicht für das neutrale Beispielbuch
date: 2024-06-01
version: 1.0
doc_type: cover
authors:
- ERDA Team
geometry:
- paperwidth=210mm
- paperheight=297mm
- left=15mm
- right=15mm
- top=15mm
- bottom=15mm
header-includes:
- \usepackage{calc}
- \usepackage{enumitem}
- \setlistdepth{20}
- \usepackage{longtable}
- \usepackage{ltablex}
- \usepackage{booktabs}
- \usepackage{array}
- \keepXColumns
- \setlength\LTleft{0pt}
- \setlength\LTright{0pt}
---

<a id="md-index"></a>


# Willkommen zur neutralen Beispielbibliothek

Diese Startseite liefert einen schnellen Überblick über das Beispielbuch, das als neutrale Vorlage für Tests, Layoutprüfungen und internationale Text-Snippets dient. Die Kapitel enthalten Tabellen, Bilder, interne und externe Links sowie strukturierte Anhänge.

## Schnelleinstieg
- [Vorwort](#md-preface)
- [Kapitel 1 – Beobachtbare Muster](#md-chapters-chapter-01)
- [Kapitel 2 – Vergleichstabellen](#md-chapters-chapter-02)
- [Vorlagen für mehrsprachige Texte](#md-templates-multilingual-neutral-text)
- [Appendix A – Datenquellen](#md-appendices-appendix-a)
- [Emoji-Beispiele (Smileys & Personen)](#md-examples-emoji-smileys-and-people)
- [Emoji-Beispiele (Natur & Essen)](#md-examples-emoji-nature-and-food)
- [Emoji-Beispiele (Aktivitäten & Reisen)](#md-examples-emoji-activities-and-travel)
- [Emoji-Beispiele (Objekte, Symbole & Flaggen)](#md-examples-emoji-objects-symbols-flags)
- [Appendix – Emoji- & Schriftabdeckung](#md-appendices-emoji-font-coverage)
- [Zitationen & weiterführende Quellen](#md-references)

## Visuale Vorschau
<a id="visuale-vorschau"></a>
![Neutrale Formen](.gitbook/assets/neutral-grid.pdf)

Die Illustration zeigt abstrakte Formen ohne Bezug zu realen Personen oder markenrechtlich relevanten Themen. Sie kann beliebig oft wiederverwendet werden, um Bildkomponenten zu testen.

## Externe neutrale Links
- [United Nations Data](https://data.un.org/)
- [Smithsonian Open Access](https://www.si.edu/openaccess)
- [World Meteorological Organization](https://public.wmo.int/en)

Alle Links führen zu allgemein zugänglichen, neutralen Informationen und eignen sich für rechtlich unkritische Testfälle.

> Tipp: Nutze die Startseite als Template, indem du die hier gelisteten Sektionen kopierst und für deine eigene Dokumentation anpasst.


\newpage

---
title: Widmung
doc_type: dedication
order: 5
---
<a id="md-dedication"></a>


# Widmung

Wir widmen dieses Buch allen Mitwirkenden, die Wissen teilen.


\newpage

---
title: Vorwort
date: 2024-06-01
version: 1.0
doc_type: preface
---
<a id="md-preface"></a>


# Vorwort

Dieses Vorwort erläutert Zweck und Aufbau des Beispielbuchs. Alle Inhalte sind bewusst neutral formuliert, damit sie für Usability-Tests, Layout-Demos und Lokalisierungsworkflows genutzt werden können.

- **Zielgruppe:** Teams, die Text-, Bild- oder Tabellenkomponenten ohne reale Kundendaten testen möchten.
- **Struktur:** Jede Sektion enthält mindestens ein Element, das in typischen Buchproduktionen vorkommt – z. B. Abbildungen, Querverweise, Zitationen oder Tabellen.
- **Internationalität:** Die beiliegende Vorlage für mehrsprachige Texte deckt gängige Hauptsprachen ab und kann erweitert werden.

Weiterführende Hinweise finden sich in [Kapitel 1](#md-chapters-chapter-01), während [Kapitel 2](#md-chapters-chapter-02) konkrete Tabellenlayouts bietet.


\newpage

---
title: Kapitel 1 – Beobachtbare Muster
date: 2024-06-01
version: 1.0
doc_type: chapter
chapter_number: 1
---
<a id="md-chapters-chapter-01"></a>


# Kapitel 1 – Beobachtbare Muster

Dieses Kapitel stellt eine neutrale Beschreibung strukturierter Beobachtungen vor. Alle Beispiele basieren auf generischen Messpunkten, die sich leicht in neue Kontexte übertragen lassen.

## 1.1 Methodische Schritte
1. **Rahmen definieren:** Bestimme den Zweck der Beobachtung (z. B. Temperatur, Nutzungsverhalten oder Prozessdauer).
2. **Messpunkte wählen:** Lege neutrale Parameter fest, die keine personenbezogenen Daten enthalten.
3. **Dokumentation sichern:** Halte Messergebnisse tabellarisch fest und verweise auf die Quelle, z. B. öffentliche Datenkataloge.[^1]

## 1.2 Beispielbeschreibung
- *Messgebiet:* Ein fiktives Versuchsareal mit moderatem Klima.
- *Messgeräte:* Standardisierte Sensoren mit Kalibrierzertifikat.
- *Auswertung:* Durchschnittswerte über einen Vier-Wochen-Zeitraum.

Die resultierenden Daten werden weiter unten im Buch, insbesondere in [Kapitel 2](#md-chapters-chapter-02), in Tabellenform dargestellt. Detaildaten sind außerdem in [Appendix A](#md-appendices-appendix-a) abgelegt.

## 1.3 Querverweise
| Abschnitt | Zweck | Link |
|-----------|-------|------|
| Vorwort | Kontext und Zielsetzung | [Zur Einleitung](\#md-preface) |
| Bildvorlage | Grafische Darstellung | [Startseite](\#visuale-vorschau) |
| Textvorlagen | Mehrsprachige Snippets | [Templates](\#md-templates-multilingual-neutral-text) |

[^1]: Siehe [Zitationen & Quellen](#md-references).


\newpage

---
title: Kapitel 2 – Vergleichstabellen
date: 2024-06-01
version: 1.0
doc_type: chapter
chapter_number: 2
---
<a id="md-chapters-chapter-02"></a>


# Kapitel 2 – Vergleichstabellen

Die folgenden Tabellen zeigen, wie neutrale Datensätze strukturiert werden können. Alle Werte sind illustrative Mittelwerte und lassen sich problemlos durch reale Messreihen ersetzen.

## 2.1 Übersichtstabelle
| Messpunkt | Woche 1 | Woche 2 | Woche 3 | Woche 4 |
|-----------|---------|---------|---------|---------|
| Temperaturmittel (°C) | 18.2 | 18.5 | 18.4 | 18.3 |
| Luftfeuchte (\%) | 52 | 53 | 51 | 52 |
| Lichtstunden | 14 | 14 | 13 | 13 |

## 2.2 Format-Beispiel für Verhältnisse
| Kategorie | Anteil am Gesamtvolumen | Notiz |
|-----------|------------------------|-------|
| Messwerte mit direktem Sensorbezug | 40 \% | Sensoren nach ISO 17025 kalibriert |
| Berechnete Richtwerte | 35 \% | Ableitung über gleitende Mittelwerte |
| Kontextdaten | 25 \% | Stammen aus öffentlichen Katalogen[^2] |

Die Tabellen können als CSV exportiert oder in [Appendix A](#tabellenlayout) erneut eingesehen werden. Verlinke interne Abschnitte immer mit relativen Pfaden, damit das Buch offline funktioniert.

## 2.3 Referenz auf Abbildungen
![Rasterdarstellung der Messpunkte](.gitbook/assets/neutral-grid.pdf)

Die Abbildung verdeutlicht, wie Messzonen schematisch gezeigt werden können, ohne reale Orte zu benennen.

Zur Überprüfung einer eingebetteten HTML-Inlay-Variante kann zusätzlich die folgende Figur verwendet werden:

![ERDA logo](.gitbook/assets/ERDA_Logo_simple.png){fig-alt="ERDA Logo"}

[^2]: Vgl. die referenzierten offenen Kataloge in [Zitationen & weiterführende Quellen](#md-references).


\newpage

---
doc_type: epilog
title: Abschluss
version: 1.0.0
---
<a id="md-epilog"></a>


# Abschluss

Kurzer Abschlussabschnitt. Ergänze hier das Nachwort bzw. den Epilog.


\newpage

---
title: Beispiele
date: 2024-06-05
version: 1.0
doc_type: example
---
<a id="md-examples-readme"></a>


# Beispiele

Dieser Ordner sammelt umfassende Emoji-Beispiele zur Validierung der Farbdarstellung und Font-Abdeckung in generierten PDFs.

## Emoji-Kategorien

Die Beispiele sind nach Unicode-Kategorien organisiert:

- **[Smileys & Personen](#md-examples-emoji-smileys-and-people)**: Gesichtsausdrücke, Gesten, Berufsrollen und Hautfarb-Varianten (U+1F600–U+1F64F, U+1F466–U+1F9D1)
  
- **[Natur & Essen](#md-examples-emoji-nature-and-food)**: Tiere, Pflanzen, Wettersymbole und Lebensmittel (U+1F330–U+1F37F, U+1F400–U+1F4FF)
  
- **[Aktivitäten & Reisen](#md-examples-emoji-activities-and-travel)**: Sport, Hobbys, Verkehrsmittel und Orte (U+1F680–U+1F6FF, U+1F3A0–U+1F3FF)

- **[Emoji im Header – Überschriften](#md-examples-emoji-headings)**: Regressionstest für Emojis in Überschriften (H1/H2/H3), inkl. ZWJ/VS16/Flaggen.
  
- **[Objekte, Symbole & Flaggen](#md-examples-emoji-objects-symbols-flags)**: Alltags-Objekte, technische Symbole, Zeichen und internationale Flaggen (U+1F4A0–U+1F4FF, U+1F500–U+1F5FF, U+1F1E6–U+1F1FF)

## Testabdeckung

Diese Beispiele validieren:
- ✅ **Farbdarstellung**: Twemoji Mozilla COLR/CPAL Format
- ✅ **Unicode-Vollständigkeit**: Alle gängigen Emoji-Ranges
- ✅ **Modifikatoren**: Hautfarben, Geschlechts-Varianten, ZWJ-Sequenzen
- ✅ **Layout-Stabilität**: Emoji in Fließtext, Tabellen und Listen

## Verwendung

**Zweck**: 
- Automatisierte Rendering-Tests für PDF-Generierung
- Visuelle Qualitätskontrolle für Emoji-Farben
- Referenzdokumentation für Font-Stack-Konfiguration

**Technische Details**:
- Font: Twemoji Mozilla v0.7.0 (COLR/CPAL)
- Format: LuaTeX + Pandoc Lua-Filter
- Fallback: DejaVu Sans für nicht-Emoji-Zeichen

---

*Letzte Aktualisierung: Version 1.0 (2024-06-05) – Vollständige Emoji 13.1 Abdeckung*


\newpage

---
title: Emoji-Beispiele – Aktivitäten & Reisen
description: Häufige Sport-, Freizeit- und Transport-Emojis für Funktions- und Renderingtests.
date: 2024-06-05
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2024-06-05
    changes: Startversion für Aktivitäten- und Verkehrsgruppen.
---
<a id="md-examples-emoji-activities-and-travel"></a>


# Emoji-Beispiele – Aktivitäten & Reisen

Diese Sammlung kombiniert Sport, Hobbys, Büro-Workflows und Transportmittel, damit Workflows mit kombinierten Emojis getestet werden können.

## Sport & Fitness

| Kategorie | Emoji | Unicode | Hinweis |
| --- | --- | --- | --- |
| Ausdauer | 🏃‍♀️ 🏃‍♂️ 🚴‍♀️ 🚴‍♂️ 🏊‍♀️ 🏊‍♂️ | Person + Variation Selector | Lauf-, Rad- und Schwimm-Events |
| Teamsport | ⚽ 🏀 🏐 🏈 ⚾ 🥎 | U+26BD · U+1F3C0 · U+1F3D0 · U+1F3C8 · U+26BE · U+1F94E | Ballspiele |
| Präzision | 🏓 🏸 🏑 🤺 🎯 | U+1F3D3 · U+1F3F8 · U+1F3D1 · U+1F93A · U+1F3AF | Schläger-, Fecht- und Zielübungen |
| Wintersport | ⛷️ 🏂 ⛸️ 🛷 🥌 | U+26F7 · U+1F3C2 · U+26F8 · U+1F6F7 · U+1F94C | Schnee- und Eisdisziplinen |
| Siege | 🏅 🥇 🥈 🥉 🏆 | U+1F3C5 · U+1F947 · U+1F948 · U+1F949 · U+1F3C6 | Auszeichnungen |

## Kultur & Freizeit

| Thema | Emoji | Unicode | Beschreibung |
| --- | --- | --- | --- |
| Musik | 🎧 🎤 🎸 🎻 🎹 🥁 | U+1F3A7 · U+1F3A4 · U+1F3B8 · U+1F3BB · U+1F3B9 · U+1F941 | Audio- und Instrumententests |
| Kunst \& Medien | 🎨 🖌️ 🖼️ 🎬 🎞️ | U+1F3A8 · U+1F58C · U+1F5BC · U+1F3AC · U+1F39E | Kreativbereiche |
| Spiele | 🎮 ♟️ 🎲 🧩 🃏 | U+1F3AE · U+265F · U+1F3B2 · U+1F9E9 · U+1F0CF | Game- und Puzzlebeispiele |
| Lernen | 📚 🧪 🧬 🧠 📐 | U+1F4DA · U+1F9EA · U+1F9EC · U+1F9E0 · U+1F4D0 | Bildungs- und Labor-Inhalte |
| Büro | 💻 🖥️ 🖨️ 📠 📸 | U+1F4BB · U+1F5A5 · U+1F5A8 · U+1F4E0 · U+1F4F8 | Remote- und Studio-Workflows |

## Reisen & Infrastruktur

| Kategorie | Emoji | Unicode | Kontext |
| --- | --- | --- | --- |
| Landverkehr | 🚗 🚙 🚌 🚎 🚚 🚛 🚜 | U+1F697–U+1F69C | Straßenfahrzeuge |
| Bahn | 🚆 🚇 🚈 🚊 🚉 | U+1F686 · U+1F687 · U+1F688 · U+1F68A · U+1F689 | Bahntypen |
| Luftfahrt | ✈️ 🛫 🛬 🚁 🛩️ | U+2708 · U+1F6EB · U+1F6EC · U+1F681 · U+1F6E9 | Flugbewegungen |
| Wasser | ⛴️ 🚢 🛳️ 🚤 🛶 | U+26F4 · U+1F6A2 · U+1F6F3 · U+1F6A4 · U+1F6F6 | Schiffe \& Freizeitboote |
| Infrastruktur | 🛣️ 🛤️ 🛫 🧭 🗺️ | U+1F6E3 · U+1F6E4 · U+1F6EB · U+1F9ED · U+1F5FA | Navigation |

## Hinweise für Tests

- Transport-Emojis verursachen oft höhere Zeilenhöhen; verwende daher Tabellen mit fixer Höhe, wenn Layouttests reproduzierbar sein sollen.
- Nutze Mehrspalten-Layouts, damit die Twemoji-Color-Font bei dicht gepackten Abschnitten richtig anti-aliased wird.
- Kombiniere Sport- und Reiseabschnitte, um Interaktionen zwischen Personen-ZWJ-Sequenzen und Piktogrammen zu überprüfen.


\newpage

---
title: Emoji-Beispiele – Natur & Essen
description: Sammlung gängiger Natur-, Tier- und Lebensmittel-Emojis für Layouttests.
date: 2024-06-05
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2024-06-05
    changes: Erste Veröffentlichung für Natur- und Ernährungsgruppen.
---
<a id="md-examples-emoji-nature-and-food"></a>


# Emoji-Beispiele – Natur & Essen

Diese Referenzseite deckt Pflanzen, Wetterereignisse, Tiere und Lebensmittel ab. Nutze die Gruppen, um Farbkontraste und Textumbruch mit mehrfarbigen Glyphen zu prüfen.

## Wetter & Umwelt

| Thema | Emoji | Unicode | Beschreibung |
| --- | --- | --- | --- |
| Wetter | ☀️ 🌤️ ⛅ 🌧️ ⛈️ 🌩️ 🌪️ | U+2600 · U+1F324–U+1F32A | Neutrale meteorologische Symbole |
| Himmel | 🌈 🌙 ⭐ 🌌 🌠 | U+1F308 · U+1F319 · U+2B50 · U+1F30C · U+1F320 | Licht- und Nachtmotive |
| Erde | 🌍 🌎 🌏 🌐 🧭 | U+1F30D · U+1F30E · U+1F30F · U+1F310 · U+1F9ED | Globale Darstellungen |
| Pflanzen | 🌱 🌿 ☘️ 🍀 🌳 🌵 | U+1F331 · U+1F33F · U+2618 · U+1F340 · U+1F333 · U+1F335 | Vegetations-Typen |
| Elemente | 🔥 💧 🪨 🌀 🌫️ | U+1F525 · U+1F4A7 · U+1FAA8 · U+1F300 · U+1F32B | Grundelemente \& Effekte |

## Tiere

| Kategorie | Emoji | Unicode | Besonderheit |
| --- | --- | --- | --- |
| Säugetiere | 🐶 🐱 🐭 🐹 🐰 🦊 🐻 | U+1F436–U+1F43B | Haustiere und Waldtiere |
| Vögel | 🐦 🦅 🐧 🦜 🦢 | U+1F426 · U+1F985 · U+1F427 · U+1F99C · U+1F9A2 | Flug- und Wassertiere |
| Reptilien \& Amphibien | 🐢 🐍 🦎 🐸 | U+1F422 · U+1F40D · U+1F98E · U+1F438 | Terrarien und Naturkundemotive |
| Insekten | 🐝 🐞 🦋 🐜 🦟 | U+1F41D · U+1F41E · U+1F98B · U+1F41C · U+1F99F | Bestäubung und Biologie |
| Wasserleben | 🐟 🐠 🐡 🐬 🐳 🐙 | U+1F41F · U+1F420 · U+1F421 · U+1F42C · U+1F433 · U+1F419 | Aquatische Vielfalt |

## Lebensmittel & Getränke

| Kategorie | Emoji | Unicode | Beschreibung |
| --- | --- | --- | --- |
| Obst | 🍎 🍊 🍌 🍇 🍓 🥝 🍍 | U+1F34E–U+1F34A · U+1F34C · U+1F347 · U+1F353 · U+1F34F · U+1F34D | Früchte mit klaren Farben |
| Gemüse | 🥕 🥦 🧅 🧄 🌽 🥔 | U+1F955 · U+1F966 · U+1F9C5 · U+1F9C4 · U+1F33D · U+1F954 | Nahrungsvielfalt |
| Grundnahrung | 🍞 🥐 🥨 🥯 🍚 🍝 | U+1F35E · U+1F950 · U+1F968 · U+1F96F · U+1F35A · U+1F35D | Getreide- und Pastagerichte |
| Snacks | 🍿 🍪 🍩 🍰 🧁 🍫 | U+1F37F · U+1F36A · U+1F369 · U+1F370 · U+1F9C1 · U+1F36B | Süße Beispiele |
| Getränke | ☕ 🍵 🥤 🧃 🍺 🍷 🍶 | U+2615 · U+1F375 · U+1F964 · U+1F9C3 · U+1F37A · U+1F377 · U+1F376 | Heiße und kalte Getränke |

## Hinweise für Tests

- Kombiniere Pflanzen- oder Tierabschnitte mit den mehrsprachigen Textvorlagen, um Zeilenumbrüche in anderen Schriftsystemen zu prüfen.
- Verwende dunkle und helle Hintergrundfarben, um sicherzustellen, dass die Farbebenen der Emojis mit dem Twemoji-Color-Font korrekt übereinanderliegen.
- Teste Druckausgaben zusätzlich in Graustufen, um Kontraste zu bewerten.


\newpage

---
title: Emoji-Beispiele – Objekte, Symbole & Flaggen
description: Referenzlisten für Werkzeuge, Technologie, Symbole und Flaggen mit vollständiger Emoji-Abdeckung.
date: 2024-06-05
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2024-06-05
    changes: Neu angelegte Seite für Objekte, Symbole und Flaggen.
---
<a id="md-examples-emoji-objects-symbols-flags"></a>


# Emoji-Beispiele – Objekte, Symbole & Flaggen

Diese Seite deckt Gebrauchsgegenstände, Symbole und internationale Flaggen ab und dient als Ergänzung zu den anderen Emoji-Beispielsammlungen.

## Werkzeuge & Geräte

| Kategorie | Emoji | Unicode | Beschreibung |
| --- | --- | --- | --- |
| Werkstatt | 🛠️ 🔧 🔩 ⚙️ 🪛 | U+1F6E0 · U+1F527 · U+1F529 · U+2699 · U+1FA9B | Mechanische Komponenten |
| Labor | 🔬 🔭 ⚗️ 🧪 🧫 | U+1F52C · U+1F52D · U+2697 · U+1F9EA · U+1F9EB | Forschung und Analyse |
| Kommunikation | 📱 📲 📞 📡 🛰️ | U+1F4F1 · U+1F4F2 · U+1F4DE · U+1F4E1 · U+1F6F0 | Funk- und Satellitensymbole |
| Haushalt | 🧹 🧺 🧼 🪣 🪟 | U+1F9F9 · U+1F9FA · U+1F9FC · U+1FAA3 · U+1FA9F | Reinigungs- und Haushaltsgeräte |
| Energie | 💡 🔋 🔌 ♻️ 🔦 | U+1F4A1 · U+1F50B · U+1F50C · U+267B · U+1F526 | Strom- und Nachhaltigkeitsicons |

## Symbole & Zeichen

| Typ | Emoji | Unicode | Bedeutung |
| --- | --- | --- | --- |
| Warnung | ⚠️ 🚸 ⛔ 🚫 ❗ ❕ | U+26A0 · U+1F6B8 · U+26D4 · U+1F6AB · U+2757 · U+2755 | Sicherheitssymbole |
| Navigation | ⛳ 🎯 🧭 🧭 🗺️ | U+26F3 · U+1F3AF · U+1F9ED · (dupl.) · U+1F5FA | Orientierung (inkl. absichtlicher Dopplung für Redundanztests) |
| Zeit | ⏱️ ⏲️ ⏰ 🕰️ 🗓️ | U+23F1 · U+23F2 · U+23F0 · U+1F570 · U+1F5D3 | Timer \& Kalender |
| Formen | ⬛ 🟦 ⬜ 🟥 🟨 🟩 🟧 | U+2B1B · U+1F7E6 · U+2B1C · U+1F7E5 · U+1F7E8 · U+1F7E9 · U+1F7E7 | Flächentest |
| Religion | ☮️ ☯️ ✝️ ☪️ 🕉️ ✡️ | U+262E · U+262F · U+271D · U+262A · U+1F549 · U+2721 | Spirituelle Symbole |

## Flaggen

| Region | Emoji | Beschreibung |
| --- | --- | --- |
| Global | 🏳️ 🏴 🏁 🏳️‍🌈 🏳️‍⚧️ | Grundsymbole inkl. Pride-Varianten |
| Europa | 🇪🇺 🇩🇪 🇫🇷 🇪🇸 🇮🇹 🇵🇱 🇸🇪 | EU- und Länderflaggen |
| Amerika | 🇺🇳 🇺🇸 🇨🇦 🇧🇷 🇦🇷 🇨🇱 | Vereinte Nationen \& Amerikas |
| Afrika | 🇪🇬 🇳🇬 🇰🇪 🇿🇦 🇪🇹 | Nord-, West-, Ost- und Südafrika |
| Asien \& Ozeanien | 🇨🇳 🇯🇵 🇰🇷 🇮🇳 🇦🇺 🇳🇿 | Asiatisch-pazifische Staaten |

## Hinweise für Tests

- Flaggen bestehen aus regionalen Indikator-Symbolen (RIS); stelle sicher, dass der eingesetzte Font die Sequenzen korrekt kombiniert.
- Verifiziere, dass Tabellen mit Symbolen und Werkzeugen über den **DejaVu**-Satz oder eine andere lizenzkonforme Serif/Sans-Lösung gerendert werden.
- Für farbige Emojis empfiehlt sich weiterhin der Twemoji-Color-Font. In PDF-Workflows sollte `fonts.yml` als Referenz dienen, damit ZWJ-Sequenzen eingebunden werden.


\newpage

---
title: Emoji-Beispiele – Smileys & Personen
description: Übersicht über klassische Gesichts- und Personen-Emojis zur Testabdeckung.
date: 2024-06-05
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2024-06-05
    changes: Erste Sammlung für Gesichter, Gesten und Rollenprofile.
---
<a id="md-examples-emoji-smileys-and-people"></a>


# Emoji-Beispiele – Smileys & Personen

Diese Seite gruppiert häufig genutzte Emoji-Sets nach Emotionen, Gesten und Rollenprofilen. Sie dient als Referenz, um Layouts, Schriftarten und Emoji-Fallbacks zu testen.

## Smileys & Emotionen

| Kategorie | Emoji | Unicode | Kurzbeschreibung |
| --- | --- | --- | --- |
| Fröhlich | 😀 😃 😄 😁 😆 😅 | U+1F600–U+1F606 | Standard-Smileys für positive Reaktionen |
| Liebevoll | 😊 🥰 😍 😘 😻 | U+1F60A · U+1F970 · U+1F60D · U+1F618 · U+1F63B | Herzliche Reaktionen und Tier-Varianten |
| Überraschung | 🤩 😮 😯 😲 🥳 | U+1F929 · U+1F62E · U+1F62F · U+1F632 · U+1F973 | Staunen und Party-Stimmung |
| Nachdenklich | 🤔 😐 😑 😶 🤨 | U+1F914 · U+1F610 · U+1F611 · U+1F636 · U+1F928 | Neutrale oder skeptische Gesichter |
| Stress | 😰 😱 😨 😢 😭 | U+1F630 · U+1F631 · U+1F628 · U+1F622 · U+1F62D | Stress, Sorge und Traurigkeit |
| Gesundheit | 🤒 🤕 🤧 😷 😴 | U+1F912 · U+1F915 · U+1F927 · U+1F637 · U+1F634 | Medizinische Emojis und Schlaf |

## Gesten & Hände

| Typ | Emoji | Unicode | Zweck |
| --- | --- | --- | --- |
| Zustimmung | 👍 👏 🤝 🙌 | U+1F44D · U+1F44F · U+1F91D · U+1F64C | Zustimmung und Kooperation |
| Ablehnung | 👎 🙅 🙅‍♂️ 🙅‍♀️ | U+1F44E · U+1F645 · ZWJ-Sequenzen | Verneinung und Abbruch |
| Hinweise | ☝️ ✍️ 👉 👈 👆 👇 | U+261D · U+270D · U+1F449 · U+1F448 · U+1F446 · U+1F447 | Zeigende Gesten |
| Kultur | 🤲 👐 🤘 🤙 🤟 | U+1F932 · U+1F450 · U+1F918 · U+1F919 · U+1F91F | Begrüßung und Musik-Gesten |
| Inklusiv | ✋ ✋🏻 ✋🏽 ✋🏿 | U+270B + Fitzpatrick Modifiers | Hauttöne zur Barrierefreiheit |

## Personen & Rollen

| Kategorie | Emoji | Unicode | Beschreibung |
| --- | --- | --- | --- |
| Alltag | 🙂 🧑‍🦰 🧑‍🦱 🧑‍🦳 | Standardgesicht und Haarvarianten | Gesichtszüge mit neutralen Farben |
| Beruf | 👩‍💻 👨‍🔧 🧑‍🏫 🧑‍🌾 | ZWJ-Sequenzen | Berufliche Darstellungen |
| Familie | 👨‍👩‍👧 👩‍👧‍👦 👨‍👨‍👧‍👦 | Familien-ZWJ | Diversität in Haushalten |
| Hilfsdienste | 👩‍🚒 👮‍♂️ 🧑‍🚀 🧑‍⚕️ | ZWJ-Sequenzen | Uniformen und Service |
| Diversität | 🧕 🧔‍♂️ 🧑‍🦽 🧑‍🦯 | U+1F93F etc. | Kultur- und Assistenzbeispiele |

## Hinweise für Tests

- Kombiniere diese Emoji-Zeilen mit Textblöcken in verschiedenen Schriftsystemen, um Wechselwirkungen mit Zeilenhöhen zu prüfen.
- Für farbige Glyphen empfiehlt sich das Einbinden der **Twemoji Color Font**; für monochrome Tests kann Twemoji in Graustufen gerendert werden.
- Ergänze weitere Emojis mit ZWJ- oder Hautton-Modifikatoren, wenn spezifische Workflows dies erfordern.


\newpage

---
title: "🧪 Emoji im Header – Überschriften"
description: "Testseite für Emojis in Überschriften (Bookmarks/ToC) und im Frontmatter-Titel."
date: 2026-01-08
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2026-01-08
    changes: Neue Testseite für Emojis in Überschriften.
---
<a id="md-examples-emoji-headings"></a>


# 🧪 Emoji im Header – Überschriften

Diese Seite ist ein gezielter Regressionstest für Emojis in Überschriften.
Dabei wird geprüft, dass:

- Emojis in H1/H2/H3 nicht zu LaTeX-/hyperref-Fehlern führen.
- Bookmarks/Outline im PDF stabil bleiben (PDF-Strings).
- ZWJ-Sequenzen und Variation Selector (VS16) korrekt verarbeitet werden.

## 😀 Standard-Emoji im H2

Beispieltext mit Emoji in der Überschrift.

## 🧑‍💻 ZWJ-Sequenz im H2 (Person + Laptop)

Beispieltext mit ZWJ-Sequenz.

## ⚙️ VS16 im H2 (Gear mit Variation Selector)

Beispieltext mit Variation Selector.

### 🇩🇪 Flagge im H3 (Regional Indicator Sequenz)

Beispieltext mit Flaggen-Emoji.

### ✋🏽 Hauttöne im H3 (Modifier)

Beispieltext mit Fitzpatrick-Modifier.


\newpage

---
title: Vorlage für mehrsprachige neutrale Texte
date: 2024-06-02
version: 1.1
doc_type: template
show_in_summary: false
---
<a id="md-templates-multilingual-neutral-text"></a>


# Vorlage für mehrsprachige neutrale Texte

Die folgende Struktur zeigt, wie neutrale Textbausteine in mehreren Sprachen formuliert werden können. Verwende kurze Sätze, verzichte auf personenbezogene Details und vermeide kultur- oder markenspezifische Begriffe.

## Grundaufbau
```
## Kontext
Kurze Beschreibung des Szenarios.

### Sprache (ISO-Code)
Neutraler Absatz.
```

## Beispiel: Globale Wetterbeobachtung
- **Kontext:** Ein Team beschreibt einen ruhigen Tag mit moderaten Wetterwerten.

### Deutsch (de)
Ein moderater Morgen brachte gleichmäßige Temperaturen, wodurch Messgeräte ohne Anpassung betrieben werden konnten.

### Englisch (en)
The observation team noted a calm day with stable readings, enabling straightforward comparisons over the week.

### Französisch (fr)
L'équipe a enregistré une journée stable, ce qui facilite la comparaison avec les mesures précédentes.

### Spanisch (es)
El equipo observó un día sereno con datos regulares que permiten revisar tendencias sin sesgos.

### Portugiesisch (pt)
A equipe registrou um período estável, adequado para validar calibragens e rotinas de manutenção.

### Italienisch (it)
Il gruppo ha descritto una giornata equilibrata, utile per mantenere le serie temporali coerenti.

### Niederländisch (nl)
Het team rapporteerde een rustige dag met meetwaarden die zonder correcties konden worden vastgelegd.

### Bulgarisch (bg)
Екипът отбеляза спокоен ден с равномерни данни, което улеснява сравненията в рамките на седмицата.

### Kroatisch (hr)
Tim je zabilježio miran dan s ujednačenim vrijednostima koje pojednostavljuju usporedbe tijekom tjedna.

### Tschechisch (cs)
Tým zaznamenal klidný den se stabilními hodnotami, takže týdenní porovnání probíhá bez úprav.

### Dänisch (da)
Holdet noterede en rolig dag med jævne målinger, hvilket gør det let at sammenligne ugens værdier.

### Estnisch (et)
Meeskond kirjeldas rahulikku päeva ühtlaste näitudega, mis hõlbustab nädalate võrdlemist.

### Finnisch (fi)
Tiimi mukaan päivä oli tasainen ja mittaukset pysyivät muuttumattomina, mikä tukee vertailevaa seurantaa.

### Griechisch (el)
Η ομάδα κατέγραψε ήρεμη ημέρα με σταθερές μετρήσεις που διευκολύνουν τις εβδομαδιαίες συγκρίσεις.

### Ungarisch (hu)
A csapat nyugodt napot írt le, amelynek mérései stabilak maradtak, így könnyű a heti összevetés.

### Irisch (ga)
Luaigh an fhoireann lá ciúin le léamha cobhsaí a éascaíonn comparáidí seachtainiúla.

### Lettisch (lv)
Komanda aprakstīja mierīgu dienu ar vienmērīgiem rādījumiem, kas atvieglo salīdzināšanu nedēļas griezumā.

### Litauisch (lt)
Komanda užfiksavo ramią dieną su stabiliais duomenimis, todėl savaitiniai palyginimai yra paprasti.

### Maltesisch (mt)
It-tim irreġistra ġurnata kwieta b'qari stabbli li jagħmlu aktar faċli li tqabbel id-dejta tal-ġimgħa.

### Polnisch (pl)
Zespół odnotował spokojny dzień ze stałymi odczytami, co ułatwia porównania tygodniowe.

### Rumänisch (ro)
Echipa a remarcat o zi calmă cu valori stabile, ușurând comparațiile din cursul săptămânii.

### Slowakisch (sk)
Tím opísal pokojný deň so stabilnými údajmi, ktoré pomáhajú pri porovnávaní v rámci týždňa.

### Slowenisch (sl)
Ekipa je opisala miren dan z enakomernimi meritvami, kar olajša tedenske primerjave.

### Schwedisch (sv)
Teamet noterade en lugn dag med stabila värden som gör jämförelser under veckan enklare.

### Ukrainisch (uk)
Команда спостерігала спокійний день зі стабільними показниками, що спрощує тижневі порівняння.

### Arabisch (ar)
سجل الفريق يوماً هادئاً بقراءات مستقرة تسهّل مقارنة البيانات خلال الأسبوع.

### Chinesisch (zh)
观测团队记录了一个稳定的日子，数据平稳，有助于持续对比不同周的趋势。

### Japanisch (ja)
観測チームは穏やかな一日を記録し、安定したデータが週次比較を容易にすると述べました。

### Süd-Koreanisch (ko)
관측 팀은 측정값이 고르게 유지된 차분한 하루를 기록하여 주간 비교가 수월해졌다고 보고했습니다.

### Hindi (hi)
टीम ने एक शांत दिन दर्ज किया जहाँ मान स्थिर रहे और साप्ताहिक तुलना सरल हो गई।

### Indonesisch (id)
Tim melaporkan hari tenang dengan bacaan stabil sehingga peninjauan mingguan dapat dilakukan tanpa penyesuaian.

### Filipino (fil)
Iniulat ng koponan ang isang mahinahong araw na may pantay na datos, kaya mas madali ang paghahambing ng lingguhan.

### Māori (mi)
I tuhi te rōpū tirotiro i tētahi rā mārie me ngā uara tōtika, he mea māmā ai te whakataurite ā-wiki.

### Samoanisch (sm)
Na fa'amau e le 'au se aso filemu ma faitauga toniga e faafaigofie ai su'esu'ega o vaiaso ta'itasi.

### Swahili (sw)
Timu ilieleza siku tulivu yenye takwimu thabiti zinazorahisisha kulinganisha kwa wiki.

### Amharisch (am)
ቡድኑ በተመጣጣኝ መዝገቦች ያለ የተረጋጋ ቀን መመዝገቡን አግልፆ እርምጃዎችን ለአስተካክል ቀላል እንደሚያደርግ ገለጸ።

### Yoruba (yo)
Ẹgbẹ́ náà sọ pé ọjọ́ naa dakẹ́ nígbà tí àwọ́n ìwọn ṣetán bí wọ́n ṣe rí, kí iṣirò ọ̀sẹ̀ rọrùn.

### Hausa (ha)
Ƙungiyar ta lura da ranar natsuwa mai daidaitattun bayanai da ke sauƙaƙa kwatancen mako-mako.

### Inuktitut (iu)
ᐊᒥᓱᓂ ᐱᒋᐊᕐᔪᖅ ᐅᑭᐅᑎᖅ ᐃᒡᓗᓕᖅ ᑐᙵᓇᐅᑎᓪᓗᓂ ᐱᖃᓗᒍ ᐅᓇ ᐃᓄᖅᑐᐊᓕᕐᓂᖅ ᑐᓴᖅᑕᐅᔪᒥ.

### Türkisch (tr)
Ekip, ölçümlerin dengede kaldığı sakin bir gün bildirerek haftalık karşılaştırmaların kolaylaştığını belirtti.

### Aserbaidschanisch (az)
Komanda sabit göstəricilərlə sakit bir gün qeydə aldı və bu da həftəlik müqayisələri sadələşdirir.

### Kasachisch (kk)
Топ тұрақты көрсеткіштер сақталған тыныш күнді сипаттап, апталық салыстыруды жеңілдететінін айтты.

Diese Auflistung kann beliebig erweitert werden. Ergänze bei Bedarf Hinweise zum Schriftsystem oder zur Leserichtung (z. B. bei Arabisch oder Hebräisch).


\newpage

---
title: Vorlagen
date: 2024-06-02
version: 1.1
doc_type: template
---
<a id="md-templates-readme"></a>


# Vorlagen

Dieser Ordner enthält wiederverwendbare Textvorlagen für mehrsprachige, neutrale Dokumentation.

## Verfügbare Vorlagen

### [Mehrsprachige Neutrale Texte](#md-templates-multilingual-neutral-text)

Eine strukturierte Vorlage für internationale Dokumentation mit:
- **Neutraler Formulierung**: Keine kultur-, marken- oder personenspezifischen Begriffe
- **Mehrsprachigkeit**: Beispieltexte in 10+ Hauptsprachen (DE, EN, FR, ES, ZH, JA, AR, HI, RU, PT)
- **Konsistenter Aufbau**: Kontextbeschreibung → Sprachspezifische Absätze → Tabellen

**Verwendungszwecke**:
- Template für globale Dokumentationsprojekte
- Testmaterial für Unicode-Abdeckung und Font-Rendering
- Demonstrationsobjekt für mehrsprachige PDF-Generierung

## Struktur der Vorlagen

Jede Vorlage folgt diesem Schema:

```markdown
---
title: Vorlagentitel
date: YYYY-MM-DD
version: X.Y
---

# Kontext
Kurze Beschreibung des Szenarios.

## Sprache (ISO-Code)
Neutraler Absatz ohne kulturspezifische Referenzen.
```

## Best Practices

**Bei Verwendung der Vorlagen**:
- ✅ Verwende kurze, prägnante Sätze
- ✅ Vermeide idiomatische Ausdrücke
- ✅ Nutze ISO-Sprachcodes (de-DE, en-US, fr-FR, etc.)
- ✅ Dokumentiere Anpassungen im Versionsverlauf
- ❌ Keine personenbezogenen Daten
- ❌ Keine Markennamen ohne Notwendigkeit
- ❌ Keine kulturspezifischen Metaphern

## Erweiterung

Neue Vorlagen sollten:
1. YAML-Frontmatter mit `title`, `date`, `version` haben
2. Mindestens 3 Sprachen abdecken (DE, EN, +1)
3. Im Versionsverlauf dokumentiert sein
4. Neutrale, wiederverwendbare Textbausteine enthalten

---

*Dieser Ordner wird bei Bedarf erweitert. Vorschläge für neue Vorlagen sind willkommen.*


\newpage

---
title: Hinweis der Übersetzung
doc_type: translators-note
order: 6
---
<a id="md-translators-note"></a>


# Hinweis der Übersetzung

Diese Ausgabe basiert auf der deutschen Fassung und wurde mit größter Sorgfalt übertragen.


\newpage

---
title: Tabellenverzeichnis
date: 2025-12-29
version: 1.0
doc_type: list-of-tables
auto_generate: true
include_chapter_tables: true
numbering_style: "decimal"
---
<a id="md-list-of-tables"></a>


# Tabellenverzeichnis

> **Hinweis**: Dieses Tabellenverzeichnis wird in zukünftigen Versionen automatisch aus allen Kapitel- und Appendix-Tabellen generiert.

## Kapitel-Tabellen

- Tabelle 1.1: Messreihen Versuchsaufbau ..................... (Kap. 1)
- Tabelle 2.1: Vergleichswerte Layout A vs. B ................. (Kap. 2)
- Tabelle 2.2: Statistische Auswertung ........................ (Kap. 2)

## Appendix-Tabellen

- Tabelle A.1: Öffentliche Klimadatenkataloge ................. (App. A)
- Tabelle A.2: Tabellenformate Übersicht ...................... (App. A)
- Tabelle B.1: Font-Matrix für Schriftzeichen ................. (App. B)
- Tabelle B.2: Emoji-Abdeckung nach Kategorien ................ (App. B)

---

**Automatische Generierung (v2.0.1+)**:
- Alle Tabellen mit Captions werden automatisch erfasst
- Nummerierung erfolgt nach Kapitel-Zugehörigkeit
- Seitenzahlen werden aus dem generierten PDF extrahiert


\newpage

---
title: Abbildungsverzeichnis
date: 2025-12-29
version: 1.0
doc_type: list-of-figures
auto_generate: true
include_formats: [png, jpg, svg, pdf]
numbering_style: "decimal"
---
<a id="md-list-of-figures"></a>


# Abbildungsverzeichnis

> **Hinweis**: Dieses Abbildungsverzeichnis wird in zukünftigen Versionen automatisch aus allen eingebetteten Bildern generiert.

## Kapitel-Abbildungen

- Abb. 1.1: Versuchsaufbau Übersicht ........................... (Kap. 1)
- Abb. 1.2: Messkurve Temperaturverlauf ........................ (Kap. 1)
- Abb. 2.1: Diagramm Vergleichsanalyse ......................... (Kap. 2)

## Appendix-Abbildungen

- Abb. A.1: Schematischer Aufbau Datenkatalog .................. (App. A)
- Abb. B.1: Font Coverage Matrix ............................... (App. B)

## Emoji-Beispiele

- Abb. E.1: Smileys & Personen Übersicht ....................... (Beisp.)
- Abb. E.2: Natur & Essen Emoji-Palette ........................ (Beisp.)
- Abb. E.3: Aktivitäten & Reisen Kategorien .................... (Beisp.)
- Abb. E.4: Objekte, Symbole & Flaggen ......................... (Beisp.)

---

**Automatische Generierung (v2.0.1+)**:
- Alle Bilder mit Alt-Text oder Captions werden erfasst
- Nummerierung erfolgt nach Kapitel-Zugehörigkeit
- Format-Erkennung: PNG, JPG, SVG, PDF
- Seitenzahlen werden aus dem generierten PDF extrahiert


\newpage

---
title: Abkürzungsverzeichnis
doc_type: list-of-abbreviations
order: 7
---
<a id="md-list-of-abbreviations"></a>


# Abkürzungsverzeichnis

- API – Application Programming Interface
- CLI – Command Line Interface


\newpage

---
title: Appendix A – Datenquellen und Tabellenlayout
date: 2024-06-01
version: 1.0
doc_type: appendix
appendix_id: "A"
category: "technical"
---
<a id="md-appendices-appendix-a"></a>


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
- Nutze relative Links wie [Kapitel 2](#md-chapters-chapter-02) für Querverweise.
- Grafiken finden sich im Verzeichnis [`content/.github/assets`](../images/).


\newpage

---
title: Appendix – Emoji- & Schriftabdeckung
description: Nachweis geeigneter Fonts für alle Schriftzeichen und farbigen Emojis im Beispielinhalt.
date: 2024-06-05
version: 1.0
doc_type: appendix
appendix_id: "B"
category: "technical"
history:
  - version: 1.0
    date: 2024-06-05
    changes: Erstfassung mit Font-Matrix und Testhinweisen.
---
<a id="md-appendices-emoji-font-coverage"></a>


# Appendix – Emoji- & Schriftabdeckung

Diese Übersicht fasst die Fonts zusammen, die sämtliche Schriftsysteme der Beispieltexte sowie alle Emoji-Sets abdecken. Alle Fonts erfüllen die Lizenzanforderungen aus `AGENTS.md` und der Datei `LICENSE-FONTS`.

## Font-Matrix

| Kategorie | Font | Lizenz | Quelle | Abdeckung |
| --- | --- | --- | --- | --- |
| Serif/Sans/Mono | DejaVu Serif · DejaVu Sans · DejaVu Sans Mono (v2.37) | Bitstream Vera License + Public-Domain-Erweiterungen | `gitbook\_worker/defaults/fonts.yml` · `publish/ATTRIBUTION.md` | Latein, Griechisch, Kyrillisch sowie technische Symbole für Tabellen und Code |
| CJK \& weitere BMP-Glyphen | ERDA CC-BY CJK | CC BY 4.0 **oder** MIT | `.github/fonts/erda-ccby-cjk` · `LICENSE-FONTS` | Chinesisch, Japanisch, Koreanisch und zusätzliche Unicode-Blöcke aus den mehrsprachigen Vorlagen |
| Farbige Emojis | Twemoji Color Font v15.1.0 | CC BY 4.0 | https://github.com/13rac1/twemoji-color-font/releases/tag/v15.1.0 · `publish/ATTRIBUTION.md` | Alle Emoji-Kategorien einschließlich Hauttöne, ZWJ-Sequenzen und Flaggen |

## Praktische Nutzung

1. **Textabschnitte** – Die DejaVu-Familie fungiert als Standard für Fließtext (`SERIF`), UI-Elemente (`SANS`) und Code (`MONO`). Dadurch sind sämtliche europäischen Sprachen der Datei `content/templates/multilingual-neutral-text.md` abgedeckt.
2. **CJK** – Sobald Kapitel oder Beispielseiten Schriftzeichen wie 日, 学 oder 정보 verwenden, sollte das Build-System die ERDA-CC-BY-CJK-Datei aus `.github/fonts/erda-ccby-cjk/true-type/` einbetten. Das geschieht automatisch über die `CJK`-Sektion in `gitbook_worker/defaults/fonts.yml`.
3. **Emoji-Farbe** – Für die neuen Emoji-Beispielseiten wird der Twemoji-Color-Font eingebunden. Die Datei `gitbook_worker/defaults/fonts.yml` verweist auf die Download-URL, sodass CI-Builds das TTF automatisiert nachladen können.

## Testhinweise

- Führe `pytest -k emoji` aus, um sicherzustellen, dass das Font-Scanning keine unbekannten Schriften meldet.
- Prüfe PDF-Exports mit mindestens einer Seite aus jeder Emoji-Kategorie (Smileys, Natur, Aktivitäten, Objekte), um Twemoji gegen CJK-Text zu testen.
- Dokumentiere neue Fonts zusätzlich in `publish/ATTRIBUTION.md` und `LICENSE-FONTS`, falls weitere Schriftsysteme hinzukommen.


\newpage

---
doc_type: legal-notice
title: Rechtliche Hinweise
version: 1.0.0
---
<a id="md-legal-notice"></a>


# Rechtliche Hinweise

Platzhalter für Impressum oder rechtliche Hinweise.


\newpage

---
doc_type: glossary
title: Glossar
version: 1.0.0
---
<a id="md-glossary"></a>


# Glossar

Platzhalter für Begriffe und Definitionen.


\newpage

---
title: Zitationen & weiterführende Quellen
date: 2024-06-01
version: 1.0
doc_type: bibliography
citation_style: "APA"
---
<a id="md-references"></a>


# Zitationen & weiterführende Quellen

1. **United Nations Data Portal.** Zugriff am 01.06.2024. https://data.un.org/
2. **World Bank Open Data.** Zugriff am 01.06.2024. https://data.worldbank.org/
3. **World Meteorological Organization – Public Resources.** Zugriff am 01.06.2024. https://public.wmo.int/en
4. **Smithsonian Open Access.** Zugriff am 01.06.2024. https://www.si.edu/openaccess

Verweise innerhalb des Buchs nutzen nummerierte Fußnoten, um konsistent auf diese Liste zu zeigen.


\newpage

---
doc_type: index
title: Register
version: 1.0.0
---
<a id="md-index-register"></a>


# Register

Platzhalter für das Stichwortverzeichnis.


\newpage

---
title: Danksagungen & Zuschreibungen
date: 2025-12-29
version: 1.0
doc_type: attributions
include_font_licenses: true
include_contributors: true
categories:
  - fonts
  - libraries
  - contributors
---
<a id="md-attributions"></a>


# Danksagungen & Zuschreibungen

Dieses Buch wurde mit Unterstützung vieler Open-Source-Projekte und Beitragender erstellt. Wir danken allen, die ihre Arbeit der Gemeinschaft zur Verfügung stellen.

---

## Verwendete Schriften

### Twemoji Mozilla (v0.7.0)
**Lizenz**: CC BY 4.0  
**Copyright**: © Mozilla Foundation  
**Quelle**: https://github.com/mozilla/twemoji-colr  
**Verwendung**: Farbige Emoji-Darstellung (COLR/CPAL Format)

### DejaVu Fonts (v2.37)
**Lizenz**: Bitstream Vera License (permissive, GPL-compatible)  
**Copyright**: © DejaVu Fonts Team  
**Quelle**: https://dejavu-fonts.github.io/  
**Verwendung**: 
- DejaVu Serif (Fließtext)
- DejaVu Sans (Überschriften, UI-Elemente)
- DejaVu Sans Mono (Code-Blöcke)

### ERDA CC-BY CJK Font (v1.0)
**Lizenz**: CC BY 4.0  
**Copyright**: © ERDA Team  
**Verwendung**: Mehrsprachige Abdeckung (Latin, Cyrillic, Greek, CJK, Devanagari, Ethiopic)

---

## Software & Bibliotheken

### LuaTeX (v1.18.0)
**Lizenz**: GPLv2+  
**Copyright**: © LuaTeX Development Team  
**Verwendung**: PDF-Satz-Engine mit COLR-Font-Support

### Pandoc (v3.6)
**Lizenz**: GPLv2+  
**Copyright**: © John MacFarlane  
**Verwendung**: Markdown → LaTeX Konvertierung

### Python (v3.12)
**Lizenz**: PSF License  
**Copyright**: © Python Software Foundation  
**Verwendung**: Build-Automatisierung, Font-Management, Workflow-Orchestrierung

### GitBook Worker (v2.0.1)
**Lizenz**: MIT  
**Copyright**: © ERDA Team  
**Verwendung**: Multilinguales Publishing-System

---

## Beitragende

### Projektteam
- **ERDA Team** – Konzeption, Entwicklung, Dokumentation
- **GitHub Copilot** – Architektur-Support, Code-Review, Dokumentations-Assistenz

### Fachredaktion
- Neutrale Inhalte: ERDA Content Team
- Emoji-Testsammlungen: ERDA Quality Assurance
- Mehrsprachige Vorlagen: ERDA Localization Team

### Technische Illustrationen
- Font-Coverage-Matrix: Automatisch generiert
- Emoji-Übersichten: Unicode Consortium Data

---

## Datenquellen

Die neutralen Beispieldaten stammen aus öffentlich zugänglichen Quellen:

1. **United Nations Data Portal** – https://data.un.org/
2. **World Bank Open Data** – https://data.worldbank.org/
3. **World Meteorological Organization** – https://public.wmo.int/
4. **Smithsonian Open Access** – https://www.si.edu/openaccess

---

## Community & Standards

Besonderer Dank an:
- **Unicode Consortium** – Emoji-Standard und -Dokumentation
- **GitHub** – Hosting und Collaboration-Tools
- **Open Source Community** – Für die unzähligen Bibliotheken und Tools

---

**Stand**: Dezember 2025  
**Version**: 1.0  
**Aktualisierungen**: Dieses Dokument wird bei jeder Release aktualisiert


\newpage

---
doc_type: errata
title: Errata
version: 1.0.0
---
<a id="md-errata"></a>


# Errata

Platzhalter für bekannte Fehler und Korrekturen.


\newpage

---
doc_type: release-notes
title: Release Notes
version: 1.0.0
---
<a id="md-release-notes"></a>


# Release Notes

Platzhalter für Versionshinweise.


\newpage

---
title: Kolophon
date: 2025-12-29
version: 1.0
doc_type: colophon
position: "back"
include_technical_details: true
---
<a id="md-colophon"></a>


# Kolophon

**Das ERDA Buch – Mehrsprachige Publishing Platform**

Ein neutrales Beispielbuch für Tests, Layout-Demos und Lokalisierungs-Workflows.

---

## Publikationsangaben

**Titel**: Das ERDA Buch  
**Untertitel**: Neutrale Beispielbibliothek für mehrsprachige Publishing-Tests  
**Ausgabe**: 1. Auflage, Dezember 2025

**Herausgeber**: ERDA Team  
**Kontakt**: https://github.com/Rob9999/gitbook-worker

**ISBN**: –  
**eISBN (PDF)**: –

---

## Lizenz

**Textlizenz**: CC BY-SA 4.0  
Creative Commons Attribution-ShareAlike 4.0 International  
https://creativecommons.org/licenses/by-sa/4.0/

**Bedeutung**:
- ✓ Vervielfältigung und Weitergabe erlaubt
- ✓ Bearbeitung und kommerzielle Nutzung erlaubt
- ⚠ Namensnennung erforderlich
- ⚠ Weitergabe nur unter gleicher Lizenz

**Code-Lizenz**: MIT License  
https://opensource.org/licenses/MIT

---

## Technische Details

### Satz und Typografie

**Satz-Engine**: LuaTeX 1.18.0 (TeX Live 2024)  
**Konvertierung**: Pandoc 3.6  
**Build-System**: GitBook Worker 2.0.1 (Python 3.12)

**Schriftarten**:
- **Fließtext**: DejaVu Serif 2.37 (10pt)
- **Überschriften**: DejaVu Sans 2.37 (14-24pt)
- **Code**: DejaVu Sans Mono 2.37 (9pt)
- **Emojis**: Twemoji Mozilla 0.7.0 (COLR/CPAL)
- **Mehrsprachig**: ERDA CC-BY CJK 1.0 (7000+ Glyphen)

### Dokument-Eigenschaften

**Seitengröße**: A4 (210 × 297 mm)  
**Seitenränder**: 2.5cm (oben/unten), 2cm (links/rechts)  
**Zeilenhöhe**: 1.4 (Fließtext)  
**Spalten**: Einspaltig

**PDF-Version**: PDF/A-1b (Archivierung)  
**Farbmodell**: RGB (Screen-optimiert)  
**Schrift-Einbettung**: Vollständig (100%)

### Automatisierung

**Workflow-Orchestrator**: GitBook Worker Orchestrator  
**Font-Management**: FontStorageBootstrapper (Dynamic Loading)  
**Content-Konvertierung**: Markdown → LaTeX → PDF  
**Emoji-Verarbeitung**: Unicode 15.1 mit COLR-Rendering

**Git-Repository**: https://github.com/Rob9999/gitbook-worker  
**Release-Tag**: v2.0.1  
**Build-Datum**: {{ BUILD_DATE }}

---

## Druckangaben

**Druck**: –  
**Papier**: –  
**Bindung**: –

**Hinweis**: Diese digitale Version ist für Screen-Verwendung optimiert. Eine Druckversion mit CMYK-Farbraum und hoher Auflösung kann separat generiert werden.

---

## Version und Historie

**Version 1.0** (Dezember 2025)
- Erste vollständige Ausgabe
- Document-Type-System implementiert
- Automatische Verzeichnisgenerierung
- Mehrsprachige Unterstützung (DE, EN)

Vollständige Changelog:  
https://github.com/Rob9999/gitbook-worker/releases

---

## Kontakt und Feedback

**Issues**: https://github.com/Rob9999/gitbook-worker/issues  
**Diskussionen**: https://github.com/Rob9999/gitbook-worker/discussions  
**Beiträge**: Pull Requests willkommen!

---

Gesetzt mit LuaTeX und Pandoc • Entwickelt in Deutschland • Dezember 2025