---
title: Markdown Erweiterte Features
date: 2026-01-11
version: 1.0
doc_type: example
category: documentation-features
---

# Markdown Erweiterte Features

Diese Seite demonstriert erweiterte Markdown-Syntax und Features über die Grundformatierung hinaus.

## Aufgabenlisten

- [x] Grundlegende Markdown-Syntax dokumentiert
- [x] Emoji-Unterstützung implementiert
- [x] Mehrsprachiger Inhalt getestet
- [ ] Interaktive Beispiele hinzugefügt
- [ ] Video-Tutorials erstellt
- [ ] Community-Feedback eingearbeitet

### Verschachtelte Aufgabenlisten

- [x] Phase 1: Planung
  - [x] Anforderungsanalyse
  - [x] Architektur-Design
- [x] Phase 2: Implementierung
  - [x] Kernfunktionen
  - [ ] Erweiterte Funktionen
- [ ] Phase 3: Release
  - [ ] Beta-Tests
  - [ ] Dokumentations-Review

## Durchgestrichen

~~Dieser Text ist durchgestrichen.~~

Sie können Durchstreichung mit anderer Formatierung kombinieren: ~~**fett und durchgestrichen**~~ oder ~~*kursiv und durchgestrichen*~~.

Dies ist nützlich, um ~~veraltete~~ obsolete Features oder Korrekturen anzuzeigen.

## Tiefgestellt und Hochgestellt

### Tiefgestellt

Wassermolekül: H~2~O

Chemische Formel: C~6~H~12~O~6~ (Glucose)

### Hochgestellt

Mathematische Notation: E = mc^2^

Fußnoten-Referenz^[1]^

Potenzen: 2^10^ = 1024

## Hervorhebung / Markierung

Dies ist ==hervorgehobener Text== unter Verwendung der Mark-Syntax.

Sie können ==**Hervorhebung mit Fettschrift kombinieren**== oder ==*mit Kursivschrift*==.

Verwenden Sie Hervorhebung, um ==Aufmerksamkeit auf wichtige Informationen zu lenken==.

## Definitionslisten

Begriff 1
: Definition von Begriff 1 mit Inline-`Code`.

Begriff 2
: Erste Definition von Begriff 2.
: Zweite Definition von Begriff 2.

API
: Application Programming Interface
: Eine Reihe von Protokollen und Werkzeugen zum Erstellen von Softwareanwendungen.

Markdown
: Eine leichtgewichtige Auszeichnungssprache mit Klartext-Formatierungssyntax.
: Erstellt von John Gruber im Jahr 2004.

## Abkürzungen

Die HTML-Spezifikation wird vom W3C gepflegt.

*[HTML]: HyperText Markup Language
*[W3C]: World Wide Web Consortium
*[API]: Application Programming Interface

Dieses Dokument verwendet UTF-8-Kodierung und folgt ISO-Standards.

*[UTF-8]: 8-Bit Unicode Transformation Format
*[ISO]: Internationale Organisation für Normung

## Mathematische Gleichungen

### Inline-Mathematik

Der Satz des Pythagoras lautet $a^2 + b^2 = c^2$.

Einsteins berühmte Gleichung: $E = mc^2$.

Die quadratische Formel: $x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$.

### Display-Mathematik

$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$

Matrix-Notation:

$$
\begin{bmatrix}
a & b \\
c & d
\end{bmatrix}
\begin{bmatrix}
x \\
y
\end{bmatrix}
=
\begin{bmatrix}
ax + by \\
cx + dy
\end{bmatrix}
$$

Griechische Buchstaben und Symbole:

$$
\alpha + \beta = \gamma \quad \sum_{i=1}^{n} i = \frac{n(n+1)}{2}
$$

## Callouts / Hinweisboxen

> **Hinweis:**  
> Dies ist ein informativer Hinweis unter Verwendung der Blockquote-Syntax.
> Verwenden Sie Hinweise für zusätzlichen Kontext oder Klärungen.

> **Warnung:**  
> Dies ist eine Warnmeldung über potenzielle Probleme.
> Warnungen machen Nutzer auf häufige Fehler oder Risiken aufmerksam.

> **Tipp:**  
> Dies ist ein hilfreicher Tipp oder Best Practice.
> Tipps bieten Anleitungen für optimale Nutzung.

> **Wichtig:**  
> Kritische Informationen, die Nutzer lesen müssen.
> Verwenden Sie dies für wesentliche Details, die die Funktionalität beeinflussen.

## Erweiterte Code-Features

### Code mit Zeilennummern

```python {.numberLines startFrom="10"}
def berechne_fibonacci(n):
    if n <= 1:
        return n
    return berechne_fibonacci(n-1) + berechne_fibonacci(n-2)

ergebnis = berechne_fibonacci(10)
print(f"Fibonacci(10) = {ergebnis}")
```

### Code mit Hervorhebung

```javascript {highlight=[2,5-7]}
function verarbeiteDaten(daten) {
    const gefiltert = daten.filter(item => item.aktiv);  // hervorgehoben
    const sortiert = gefiltert.sort((a, b) => a.wert - b.wert);
    
    return sortiert.map(item => ({  // start hervorhebung
        id: item.id,
        wert: item.wert * 2
    }));  // ende hervorhebung
}
```

### Code mit Dateinamen

```python title="beispiel.py"
# beispiel.py
def gruesse(name):
    return f"Hallo, {name}!"

if __name__ == "__main__":
    print(gruesse("Welt"))
```

## Tabellen mit Ausrichtung

### Komplexe Tabelle

| Feature      | Basis | Professional | Enterprise   |
|:-------------|:-----:|:------------:|-------------:|
| Nutzer       | 5     | 50           | Unbegrenzt   |
| Speicher     | 10GB  | 100GB        | 1TB          |
| Support      | E-Mail| Priorität    | 24/7         |
| Preis        | Frei  | 50€/Monat    | 200€/Monat   |

### Tabelle mit Formatierung

| Code | Ausgabe | Beschreibung |
|------|---------|--------------|
| `**fett**` | **fett** | Fettschrift |
| `*kursiv*` | *kursiv* | Kursivschrift |
| `~~durch~~` | ~~durch~~ | Durchgestrichen |
| `==mark==` | ==mark== | Hervorgehoben |
| `H~2~O` | H~2~O | Tiefgestellt |
| `X^2^` | X^2^ | Hochgestellt |

## Tastaturkürzel

Drücken Sie <kbd>Strg</kbd> + <kbd>C</kbd> zum Kopieren.

Verwenden Sie <kbd>Strg</kbd> + <kbd>Umschalt</kbd> + <kbd>P</kbd> zum Öffnen der Befehlspalette.

Speichern mit <kbd>Strg</kbd> + <kbd>S</kbd> (Windows/Linux) oder <kbd>⌘</kbd> + <kbd>S</kbd> (macOS).

## HTML-Entities und Sonderzeichen

### Pfeile und Symbole

← → ↑ ↓ ↔ ↕ ⇐ ⇒ ⇔

✓ ✗ ☐ ☑ ☒

★ ☆ ♠ ♣ ♥ ♦

### Mathematische Symbole

± × ÷ ≠ ≈ ≤ ≥ ∞ ∑ ∏ ∫ √ ∂

### Währungen und Einheiten

£ € $ ¥ ¢ ° º ª

### Typografie

– — … ' ' " " « » ‹ ›

© ® ™ § ¶

## Details / Akkordeon

<details>
<summary>Klicken zum Erweitern: Installationsanweisungen</summary>

So installieren Sie die Software:

1. Laden Sie die neueste Version herunter
2. Entpacken Sie das Archiv
3. Führen Sie das Installationsprogramm aus
4. Folgen Sie dem Setup-Assistenten

```bash
wget https://example.com/software.tar.gz
tar -xzf software.tar.gz
cd software/
./install.sh
```

</details>

<details>
<summary>Fehlerbehebung bei häufigen Problemen</summary>

### Problem 1: Installation schlägt fehl

**Lösung:** Stellen Sie sicher, dass Sie Administratorrechte haben.

### Problem 2: Schriftdarstellungsprobleme

**Lösung:** Aktualisieren Sie Ihren Font-Cache mit `fc-cache -fv`.

</details>

## Horizontale Trennlinien mit verschiedenen Stilen

---

***

___

<!-- Jede erstellt eine horizontale Trennlinie -->

## Escape-Zeichen

Verwenden Sie Backslash zum Escapen von Sonderzeichen:

\*Nicht kursiv\* \**Nicht fett\** \`Kein Code\`

\# Keine Überschrift

\[Kein Link\](url)

## Zeilenumbrüche und Abstände

Regulärer Zeilenumbruch  
mit zwei Leerzeichen am Ende.

Harter Umbruch mit Backslash\
funktioniert genauso.

Verwenden Sie `<br>` für explizite Umbrüche:<br>So wie hier.

## Kommentare

<!-- Dies ist ein Kommentar und erscheint nicht in der Ausgabe -->

<!--
Mehrzeilige Kommentare
können mehrere Zeilen umfassen
und sind nützlich für Notizen
-->

## Emojis mit Shortcodes

:smile: :heart: :thumbsup: :rocket: :tada:

:warning: :information_source: :question: :exclamation:

:checkmark: :x: :heavy_check_mark: :cross_mark:

## Links mit Referenzen

Dies ist ein [Referenz-Link][1] und ein weiterer [Referenz-Link][ref].

[1]: https://example.com "Beispiel-Website"
[ref]: https://github.com "GitHub"

Auto-Erkennung: https://example.com wird zu einem Link.

E-Mail: <benutzer@example.com>

## Kombinierte erweiterte Features

Hier ist ein vollständiges Beispiel, das mehrere Features kombiniert:

> **Wichtig:** Datenverarbeitungs-Pipeline  
> Die neue Pipeline verarbeitet ==1 Million Datensätze/Sekunde==.[^perf]
>
> Wichtige Verbesserungen:
> - [x] Latenz um 50% reduziert
> - [x] Durchsatz erhöht: ~~10k~~ → **1M** Ops/Sek
> - [ ] Echtzeit-Monitoring hinzufügen
>
> Leistungsformel: $T = \frac{N}{R \times E}$ wobei:
> - T = Gesamtzeit
> - N = Anzahl der Datensätze  
> - R = Datensätze pro Sekunde
> - E = Effizienzfaktor (0,8-0,95)
>
> Drücken Sie <kbd>Strg</kbd> + <kbd>R</kbd> zum Ausführen.

[^perf]: Gemessen in Testumgebung: Intel Xeon E5-2699 v4, 128GB RAM, NVMe-SSD-Speicher. Tatsächliche Leistung kann variieren.

---

*Diese Seite demonstriert das vollständige Spektrum erweiterter Markdown-Syntax, die von modernen Dokumentationssystemen unterstützt wird.*
