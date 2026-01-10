---
title: Zitations- & Fußnoten-Beispiele
date: 2026-01-11
version: 1.0
doc_type: example
category: documentation-features
---

# Zitations- & Fußnoten-Beispiele

Diese Seite demonstriert verschiedene Zitierstile und Fußnotenverwendung in Markdown-Dokumenten.

## Fußnoten

Markdown unterstützt Fußnoten[^1], die am Seitenende erscheinen. Sie können dieselbe Fußnote mehrfach referenzieren[^1].

Hier ist eine längere Fußnote mit mehreren Absätzen[^langenote].

Inline-Fußnoten sind ebenfalls möglich.^[Dies ist eine Inline-Fußnote.]

### Benannte vs. Nummerierte Fußnoten

Sie können beschreibende Namen für Fußnoten[^wichtignote] oder einfach Zahlen verwenden[^2].

## Zitierstile

### APA-Stil (7. Auflage)

**Bücher:**

Schmidt, J. A., & Müller, M. B. (2023). *Forschungsmethoden in der Dokumentation*. Wissenschaftsverlag.

**Zeitschriftenartikel:**

Braun, L. K., Schneider, R. T., & Wagner, S. E. (2024). Fortgeschrittene Satztechniken für mehrsprachige Dokumente. *Zeitschrift für Technische Kommunikation*, 45(3), 234-256. https://doi.org/10.1234/ztk.2024.01

**Online-Quellen:**

Unicode Consortium. (2023, 12. September). *Unicode-Standard 15.1.0*. https://www.unicode.org/versions/Unicode15.1.0/

### IEEE-Stil

**Zeitschriftenartikel:**

[1] L. K. Braun, R. T. Schneider und S. E. Wagner, „Fortgeschrittene Satztechniken für mehrsprachige Dokumente", *Z. Tech. Kommun.*, Bd. 45, Nr. 3, S. 234-256, 2024, doi: 10.1234/ztk.2024.01.

**Konferenzbeitrag:**

[2] J. A. Schmidt und M. B. Müller, „Automatisierte Dokumentations-Pipelines", in *Proc. Int. Konf. Software Engineering*, London, UK, 2023, S. 123-130.

**Buch:**

[3] A. Martinez, *Moderne Dokumentations-Frameworks*, 2. Aufl. Berlin, Deutschland: Tech-Verlag, 2024.

### Chicago-Stil (Autor-Datum)

**Bücher:**

Martinez, Ana. 2024. *Moderne Dokumentations-Frameworks*. 2. Aufl. Berlin: Tech-Verlag.

**Zeitschriftenartikel:**

Braun, Laura K., Robert T. Schneider und Sarah E. Wagner. 2024. „Fortgeschrittene Satztechniken für mehrsprachige Dokumente." *Zeitschrift für Technische Kommunikation* 45 (3): 234-256. https://doi.org/10.1234/ztk.2024.01.

### Zenodo-Standard (DOI-basiert)

Zenodo bietet persistente Identifikatoren (DOIs) für Forschungsdaten und Publikationen[^zenodo].

**Datensatz:**

Schmidt, Johann A.; Müller, Maria B. (2023). Beispiel-Dokumentations-Datensatz (Version 1.2) [Datensatz]. Zenodo. https://doi.org/10.5281/zenodo.1234567

**Software:**

Braun, Laura K.; Schneider, Robert T. (2024). GitBook Worker: Automatisierte Dokumentations-Pipeline (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.7654321

**Publikation:**

Martinez, Ana; Wagner, Sarah E.; Thompson, James R. (2023). Best Practices für technische Dokumentation. *Zenodo Preprints*. https://doi.org/10.5281/zenodo.8901234

### BibTeX-Format

Für LaTeX/akademische Dokumente:

```bibtex
@article{braun2024fortgeschrittene,
  title={Fortgeschrittene Satztechniken für mehrsprachige Dokumente},
  author={Braun, Laura K and Schneider, Robert T and Wagner, Sarah E},
  journal={Zeitschrift für Technische Kommunikation},
  volume={45},
  number={3},
  pages={234--256},
  year={2024},
  doi={10.1234/ztk.2024.01}
}

@software{braun2024gitbook,
  author={Braun, Laura K and Schneider, Robert T},
  title={GitBook Worker: Automatisierte Dokumentations-Pipeline},
  version={1.0.0},
  year={2024},
  publisher={Zenodo},
  doi={10.5281/zenodo.7654321},
  url={https://doi.org/10.5281/zenodo.7654321}
}

@dataset{schmidt2023beispiel,
  author={Schmidt, Johann A and Müller, Maria B},
  title={Beispiel-Dokumentations-Datensatz},
  version={1.2},
  year={2023},
  publisher={Zenodo},
  doi={10.5281/zenodo.1234567}
}
```

## Zitate im Text

### Narrative Zitationen

Wie Schmidt und Müller (2023) zeigten, reduzieren automatisierte Dokumentations-Pipelines den manuellen Aufwand erheblich.

Braun et al. (2024) fanden heraus, dass mehrsprachige Unterstützung die Zugänglichkeit der Dokumentation um 67% verbessert.

### Parenthetische Zitationen

Jüngste Forschung zeigt verbesserte Dokumentationsqualität durch Automatisierung (Schmidt & Müller, 2023; Braun et al., 2024).

Mehrere Studien unterstützen diesen Ansatz (Martinez, 2024; Wagner & Thompson, 2023; Schneider, 2022).

## Zitation mit Fußnoten kombiniert

Laut jüngster Forschung[^forschung] zeigen automatisierte Dokumentationssysteme vielversprechende Ergebnisse[^3]. Die Studie von Braun et al. (2024) liefert empirische Belege für diese Behauptungen[^4].

## Lizenzzuschreibung (Zenodo/CC-Standard)

**Schriftzuschreibung:**

Twemoji Mozilla (2023). Twitter Emoji (Twemoji) COLRv1-Schriftart. Lizenziert unter CC BY 4.0. Verfügbar unter: https://github.com/mozilla/twemoji-colr. DOI: 10.5281/zenodo.3234567 (Beispiel-DOI).

**Datenzuschreibung:**

Dieses Dokument verwendet Sprachproben aus dem Unicode Common Locale Data Repository (CLDR), lizenziert unter Unicode License Agreement. Unicode Consortium (2023). https://www.unicode.org/copyright.html

## Querverweise

Siehe [Kapitel 1](../chapters/chapter-01.md) für mehr über Design-Patterns.

Für Details zur Emoji-Darstellung siehe [Anhang B](../appendices/emoji-font-coverage.md).

---

[^1]: Dies ist eine einfache Fußnote mit einem Rückverweis zum Text.

[^2]: Fußnoten können fortlaufend nummeriert werden.

[^langenote]: Dies ist eine längere Fußnote mit mehreren Absätzen.

    Sie können zusätzliche Absätze durch Einrückung einfügen.
    
    Sogar Codeblöcke können in Fußnoten erscheinen:
    
    ```python
    def beispiel():
        return "fussnoten code"
    ```

[^wichtignote]: Beschreibende Namen machen Fußnoten in großen Dokumenten einfacher zu verwalten.

    Sie sind besonders nützlich, wenn Sie Inhalte neu organisieren müssen.

[^zenodo]: Zenodo ist ein Open-Access-Repository, das vom CERN betrieben wird und DOIs für Forschungsergebnisse einschließlich Daten, Software, Publikationen und mehr bereitstellt. Siehe https://zenodo.org für Details.

[^forschung]: Martinez, A. (2024). *Moderne Dokumentations-Frameworks*, S. 45-67.

[^3]: Insbesondere reduzieren Build-Automatisierung und Validierungs-Pipelines Fehler um etwa 80% (Schmidt & Müller, 2023).

[^4]: Die Studie umfasste 150 Dokumentationsprojekte über 12 Organisationen über einen Zeitraum von 2 Jahren.
