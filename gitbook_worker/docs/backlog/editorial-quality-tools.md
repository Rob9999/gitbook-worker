---
version: 1.8.0
date: 2026-05-10
status: proposed
priority: high
target_release: "v2.9.0 Qualitaetskompass"
labels: [quality, editorial-acceptance, metrics, pdf, markdown, multilingual]
history:
  - "1.8.0: 2026-05-10 - Orchestrator --quality-scope configured fuer Sprach- und Gesamtprojekt-Dossiers als Umsetzungsschnitt ergaenzt."
  - "1.7.0: 2026-05-10 - Kann-Artefakte HTML-Report, Trend-JSONL, SARIF und Snapshot-Index als umgesetzt markiert."
  - "1.6.0: 2026-05-10 - Definition of Done mit lokalem EN-Dossier-Nachweis formal geschlossen; Baseline-Kann-Punkt als erledigt markiert."
  - "1.5.0: 2026-05-09 - Alle offenen Muss- und Soll-Punkte als implementierten Verantwortungs-Schnitt markiert."
  - "1.4.0: 2026-05-09 - Tabellenstrategie-Problemfaelle mit Kontext als erledigten Schnitt markiert."
  - "1.3.0: 2026-05-09 - Baseline-Vergleich und akzeptierte Restrisiken als erledigten Schnitt markiert."
  - "1.2.0: 2026-05-09 - Backlog-Status nach Publish-Scope-, PDF-Zielkorridor- und Drift-Schnitt synchronisiert."
  - "1.1.0: 2026-05-09 - Anonymisiertes Kundenreview als Muss-Anforderungen und Abnahmeszenarien aufgenommen."
  - "1.0.0: 2026-05-09 - Backlog-Pflichtenheft fuer redaktionelle Qualitaetsmetriken und Abnahme erstellt."
---

# Backlog: Redaktionelle Qualitaetswerkzeuge

## Ziel

Das naechste Release soll GitBook Worker um ein redaktionelles
Qualitaets- und Abnahmesystem erweitern. Es soll Metriken aus Markdown-Quellen
und PDF-Artefakten sammeln, vorhandene Einzelchecks integrieren und daraus ein
reviewbares Abnahmedossier erzeugen.

Konzept: [../concepts/editorial-quality-tools.md](../concepts/editorial-quality-tools.md)

Kundenreview: [../concepts/editorial-quality-tools-customer-review.md](../concepts/editorial-quality-tools-customer-review.md)

## Release-Arbeitstitel

**v2.9.0 Qualitaetskompass**

Der Arbeitstitel ist bewusst redaktionell: Das Release soll Richtung geben,
nicht nur Fehler zaehlen.

## Ausgangslage

Vorhandene Bausteine:

- `gitbook_worker.tools.quality.link_audit`
- `gitbook_worker.tools.quality.ai_references`
- `gitbook_worker.tools.quality.sources`
- `gitbook_worker.tools.validators.frontmatter_checker`
- `gitbook_worker.tools.testing.pdf_validator`
- `gitbook_worker.tools.utils.pdf_toc_extractor`
- `gitbook_worker.core.application.pdf_toc`
- Tabellenlayout-JSONL-Reports aus der Tabellenprofi-Strategie

Aktuelles Problem: Diese Signale sind wertvoll, aber verteilt. Eine Redaktion
braucht ein gebuendeltes Abnahmebild mit klarer Priorisierung, Evidenz und
Healing-Steps.

## Kundenreview: Ergebnis

Das anonymisierte Kundenreview nimmt die Stossrichtung als Entwicklungsauftrag an, macht die
Abnahme aber von zusaetzlichen Anforderungen abhaengig. Diese Punkte werden in
diesem Backlog nicht als optionale Kundenwuensche behandelt, sondern als
verbindliche Abnahmeergaenzungen fuer `v2.9.0 Qualitaetskompass`.

Kern der Ergaenzung:

- Report-Drift und Artefakt-Frische muessen messbar werden.
- Wenigzeiler und leere Seiten muessen als PDF-Metriken sichtbar werden.
- Projekt- und locale-spezifische Frontmatter- und Uebersetzungsregeln muessen
  generisch profilierbar sein.
- Publikationsscope, SUMMARY und PDF-TOC muessen zusammen bewertet werden.
- Tabellenstrategie-Reports muessen aggregiert statt nur abgelegt werden.
- Abnahmeprofile, manuelle Restrisikoentscheidung und Baseline-Vergleich
  muessen Teil des Dossiers werden.

## Muss-Anforderungen

### M1 Markdown-Metrikcollector

- [x] ✅ CLI `python -m gitbook_worker.tools.quality.editorial_metrics` anlegen.
- [x] ✅ Markdown-Dateien aus `content.yaml` und optional aus einem direkten Root
  erkennen.
- [x] ✅ Datei-, Kapitel-, Heading-, Frontmatter-, Link-, Medien-, Tabellen- und
  Codeblock-Metriken sammeln.
- [x] ✅ TODO/FIXME/Review-Notizen als redaktionelle Findings ausgeben.
- [x] ✅ Link-Audit-, AI-Referenz- und Frontmatter-Signale wiederverwenden, nicht
  parallel neu erfinden.

Akzeptanzkriterien:

- JSON-Report enthaelt `schema_version`, `generated_at`, `project`, `inputs`,
  `metrics`, `findings` und `summary`.
- Ein fehlendes Pflicht-Frontmatter-Feld erzeugt ein `warn` oder `fail` Finding
  mit Healing-Step.
- Eine Markdown-Tabelle mit langen Tokens erzeugt ein nachvollziehbares
  Tabellenrisiko oder referenziert die vorhandene Tabellenstrategie.

### M2 PDF-Metrikcollector

- [x] ✅ PDF-Dateien aus Publish-Artefakten oder CLI-Argumenten erkennen.
- [x] ✅ Seitenzahl, Seitengroessen, Orientierung und Sondergeometrien ermitteln.
- [x] ✅ PDF-TOC/Outline extrahieren.
- [x] ✅ Font-Embedding-, Emoji- und CJK-Signale aus `pdf_validator` integrieren.
- [x] ✅ Textarme/leere Seiten und auffaellige Ersatzglyphen melden.
- [x] ✅ Tabellenlayout-Reports mit PDF-Artefakten verknuepfen.

Akzeptanzkriterien:

- JSON-Report enthaelt pro PDF ein stabiles Metrikobjekt.
- Ein PDF ohne extrahierbaren Text erzeugt mindestens `warn`, bei fehlendem
  Haupttext `fail`.
- Fehlende erwartete Fonts werden nicht nur geloggt, sondern als Findings
  ausgegeben.

### M3 Markdown-PDF-Abgleich

- [x] ✅ Markdown-Headings gegen PDF-TOC/Outline pruefen.
- [x] ✅ erwartete Sample-Seiten als Regeln ausdruecken koennen.
- [x] ✅ Projektversion, Sprache und Titel zwischen Manifest, Markdown und PDF
  plausibilisieren.
- [x] ✅ Publish-Eintraege ohne erzeugtes Artefakt als `blocked` melden.

Akzeptanzkriterien:

- Ein fehlender TOC-Eintrag fuer eine publishte H2/H3-Ueberschrift erzeugt ein
  Finding mit Datei- und Titelkontext.
- Ein fehlendes PDF fuer einen `build: true` Publish-Eintrag blockiert die
  Abnahme.

### M4 Redaktionelle Abnahme-CLI

- [x] ✅ CLI `python -m gitbook_worker.tools.quality.editorial_acceptance`
  anlegen.
- [x] ✅ Einen oder mehrere Metrikreports lesen.
- [x] ✅ Findings nach Severity aggregieren.
- [x] ✅ Gesamtstatus `passed`, `passed_with_warnings`, `failed` oder `blocked`
  berechnen.
- [x] ✅ Markdown-Dossier mit Executive Summary, Befunden und Healing-Steps
  erzeugen.

Akzeptanzkriterien:

- Blockierende Findings fuehren zu einem nicht-null Exit-Code.
- Warnungen koennen je Profil erlaubt oder blockierend behandelt werden.
- Das Dossier ist ohne Terminal-Log verstaendlich.

### M5 Exit-Codes und Hilfe

- [x] ✅ Neue Exit-Codes in
  [../attentions/exit-codes.md](../attentions/exit-codes.md) dokumentieren.
- [x] ✅ `--help-exit-codes` fuer neue CLIs bereitstellen.
- [x] ✅ Eindeutige Codes fuer fehlende Artefakte, harte Findings,
  unlesbare Reports und ungueltige Profile definieren.

Akzeptanzkriterien:

- Tests pruefen Exit-Code-Ausgabe und mindestens einen blockierenden Exit.
- Dokumentation und CLI-Ausgabe verwenden dieselben Texte.

### M6 Report-Drift und Artefakt-Frische

- [x] ✅ Installierte Worker-Version im Metrikreport ausweisen.
- [x] ✅ Build-Worker-Version pro PDF-Artefakt erfassen, soweit rekonstruierbar.
- [x] ✅ PDF `CreationDate`, Dateigroesse und Seitenzahl in das Dossier aufnehmen.
- [x] ✅ Metrikreport-Zeitstempel gegen Artefakt-Zeitstempel pruefen.
- [x] ✅ Release-Dokumente auf alte Worker-Versionen, alte Seitenzahlen und alte
  Layoutbefunde scannen.
- [x] ✅ Profilregel `fail_on_stale_worker_version` unterstuetzen.
- [x] ✅ Profilregel `fail_on_stale_page_count` unterstuetzen.

Akzeptanzkriterien:

- Ein absichtlich veralteter Report wird nicht als aktuelle Freigabegrundlage
  akzeptiert.
- Ein Drift-Sample mit alter Worker-Version oder alter Seitenzahl erzeugt je
  Profil `warn` oder `fail`.
- Das Dossier nennt die verglichenen Artefakte und die jeweilige Evidenz.

### M7 Wenigzeiler- und Leerseiten-Metrik

- [x] ✅ `pages_total` pro PDF ermitteln.
- [x] ✅ `low_text_pages_le_15` zaehlen; reine Seitenzahl-Footer ignorieren.
- [x] ✅ `very_low_text_pages_le_5` zaehlen.
- [x] ✅ `empty_text_pages` zaehlen.
- [x] ✅ `low_text_reason_hint` ableiten: Tabelle, Bild/Caption, Kapitelstart,
  Quellen-/URL-Seite oder unbekannt.
- [x] ✅ Schwellen `low_text_page_threshold` und `very_low_text_page_threshold`
  profilierbar machen.

Akzeptanzkriterien:

- Ein Sample-PDF mit textarmer Seite erzeugt eine reproduzierbare Metrik.
- Kapitelstart- und Bildseiten werden nicht automatisch als harte Fehler
  bewertet, bleiben aber im Dossier sichtbar.

### M8 Generisches Frontmatter- und Uebersetzungsprofil

- [x] ✅ Profilierbare Sprachrollen `source` und `target` unterstuetzen.
- [x] ✅ Frei waehlbare `source_locale` und `target_locales` unterstuetzen, z. B.
  `ja` als Source sowie `pl`, `hr` und `no` als Targets.
- [x] ✅ Profilierbare Pflichtfelder fuer Source-Content unterstuetzen.
- [x] ✅ Profilierbare Pflichtfelder fuer Target-Content unterstuetzen.
- [x] ✅ Statuswerte fuer Target-Content projektspezifisch begrenzen koennen.
- [x] ✅ `approved` separat zaehlen und als bewusste Freigabe sichtbar machen.
- [x] ✅ Verbotene Keys wie `lang`, `language`, `lang-version` als Findings
  melden.
- [x] ✅ Target-`source` repo-relativ validieren.
- [x] ✅ Source/Target-`content_id`-Drift erkennen.

Akzeptanzkriterien:

- Eine Target-Datei ohne `source` oder `status` erzeugt ein Finding.
- Eine falsche oder fehlende `content_id`-Zuordnung zwischen Source und Target
  erzeugt ein Translation-Drift-Finding.
- Sonderdateien wie `SUMMARY.md` koennen ausgenommen werden.

### M9 Publikationsprofil, SUMMARY und Heading-Abgleich

- [x] ✅ Publizierte, nicht publizierte und verwaiste Dateien getrennt zaehlen.
- [x] ✅ `use_summary: true` und GitBook-SUMMARY-Reihenfolge beruecksichtigen.
- [x] ✅ Ausschlussordner wie `desktop/`, `tmp/`, `logs/`, `release-docs/` und
  `publish/` profilieren.
- [x] ✅ PDF-Outline-Eintraege ohne Markdown-Heading melden.
- [x] ✅ Markdown-Headings ohne erwarteten PDF-Outline-Eintrag melden.
- [x] ✅ doppelte Titel im gleichen Dokument oder in direkter PDF-Naehe melden.
- [x] ✅ Kapitel-/Anhang-Reihenfolge gegen `summary_appendices_last` pruefen.

Akzeptanzkriterien:

- Ein fehlender SUMMARY-Eintrag erscheint als eigener Befund.
- Ein Heading-Sprung wird nicht nur gezaehlt, sondern mit nahem Kontext
  ausgegeben.

### M10 Tabellenstrategie-Aggregation

- [x] ✅ Tabellenlayout-JSONL-Reports lesen und validieren.
- [x] ✅ Anzahl erkannter Markdown-Pipe-Tabellen aggregieren.
- [x] ✅ Papierentscheidungen nach Format zaehlen.
- [x] ✅ Methoden wie `editorial-best-fit`, `lowest-score-fallback`, `override`,
  `disabled` und `oversize-preserve-column-heuristic` zaehlen.
- [x] ✅ Fallbacks, Overrides und abgelehnte Kandidaten als Problemfaelle melden.
- [x] ✅ Datei, Tabellenindex oder naheliegenden Heading-Kontext ausgeben.
- [x] ✅ Layout-Trade-offs sichtbar machen, insbesondere horizontale Entlastung
  gegen geringere vertikale Kapazitaet bei Landscape-Seiten.

Akzeptanzkriterien:

- Ein Sample mit Landscape- oder Fallback-Entscheidung erscheint im Dossier.
- Ein Override ist als bewusste redaktionelle Entscheidung erkennbar.

### M11 PDF-Layout, Fonts und Textextraktion

- [x] ✅ BBox-/Overflow-Findings mit Seite, Art, Ueberstand in Punkten und
  Millimetern, gekuerztem Textauszug, Ursache und Healing-Step modellieren.
- [x] ✅ Kleine DOI-/URL-Ueberstaende profilierbar als `warn` statt `fail`
  behandeln.
- [x] ✅ Projektfonts aus Profil gegen eingebettete PDF-Fonts pruefen.
- [x] ✅ Ersatzglyphen wie `□`, `�` und `.notdef` als Befunde melden.
- [x] ✅ CJK/Hangul/Kana-Stichproben pruefen, wenn solche Scripts im publizierten
  Scope vorkommen.

Akzeptanzkriterien:

- Ein fehlender Pflichtfont kann ein `failed` erzeugen.
- Ein kleiner URL-Ueberstand bleibt sichtbar, darf aber je Profil als Warnung
  akzeptiert werden.

### M12 Quellen-, Rechts- und AI-Hinweise im Dossier

- [x] ✅ Dossier muss erklaeren, dass Linkstatus technische Erreichbarkeit ist,
  keine inhaltliche Quellenwahrheit.
- [x] ✅ Dossier muss erklaeren, dass AI-Referenzchecks Such- und
  Plausibilitaetshilfen sind, keine autoritative Validierung.
- [x] ✅ Dossier muss erklaeren, dass Rechts-/Konformitaetsbefunde
  Review-Signale sind, keine Rechtsberatung.

Akzeptanzkriterien:

- Diese Disclaimer erscheinen im Markdown-Dossier, sobald die jeweiligen
  Signalgruppen enthalten sind.

### M13 Abnahmeprofile und manuelle Freigabe

- [x] ✅ Profile `local-preview`, `release-candidate`, `publish-final` und
  `docs-only` bereitstellen.
- [x] ✅ generisches Profil `multilingual-release-candidate` dokumentieren und
  testen.
- [x] ✅ `human_decision`-Vorlage in Markdown-Dossier erzeugen.
- [x] ✅ Tool darf `human_decision` nicht automatisch setzen.
- [x] ✅ Restrisiken mit `finding_id`, Grund, Rolle und Datum dokumentierbar
  machen.

Akzeptanzkriterien:

- `publish-final` blockiert bei harten Findings.
- `local-preview` erlaubt Warnungen ohne blockierenden Exit.
- Das Dossier enthaelt eine unausgefuellte Freigabevorlage.

### M14 Stabile IDs, Baselines und Datenschutz

- [x] ✅ Stabile Finding-ID aus Regel-ID, relativer Datei, nahem Heading,
  normalisiertem Evidenztext und optional Seite erzeugen.
- [x] ✅ Baseline-Vergleich mit `new`, `existing`, `resolved`, `changed`
  unterstuetzen.
- [x] ✅ Bewusst akzeptierte Befunde mit Ablaufdatum oder Releasebezug
  unterstuetzen.
- [x] ✅ Markdown-Reports mit workspace-relativen Pfaden erzeugen.
- [x] ✅ Absolute Pfade in JSON optional und deaktivierbar machen.
- [x] ✅ Evidenzauszuege kurz halten.
- [x] ✅ Netzwerkchecks im Report sichtbar als aktiviert/deaktiviert markieren.

Akzeptanzkriterien:

- Gleicher Befund bleibt bei kleiner Seitenverschiebung wiedererkennbar.
- Ein akzeptierter Befund kann in einem spaeteren Release wieder faellig werden.

## Soll-Anforderungen

### S1 Profile und Schwellen

- [x] ✅ Profile `local`, `release`, `customer-handover` vorsehen.
- [x] ✅ Schwellen fuer Warnungen und Fehler konfigurierbar machen.
- [x] ✅ Neue Konfigurationsschluessel nur zusammen mit
  `docs/configuration-reference.md` und Tests einfuehren.

### S2 Reportformate

- [x] ✅ JSON als kanonisches Format.
- [x] ✅ Markdown fuer redaktionelle Abnahme.
- [x] ✅ CSV fuer tabellarische Metriken optional.
- [x] ✅ Konsolenausgabe kurz und scanbar halten.

### S3 Workflow-Integration

- [x] ✅ Orchestrator kann nach dem PDF-Build optional Metriken und Abnahme laufen
  lassen.
- [x] ✅ Reports landen unter `logs/quality/` oder einem konfigurierten Outputpfad.
- [x] ✅ CI kann den Abnahmestatus als Gate verwenden.
- [x] ✅ Orchestrator kann mit `--quality-scope configured` je buildbarer lokaler
  `content.yaml`-Version ein Dossier plus `project-<profile>`-Gesamtdossier
  erzeugen; Remote- und `build: false`-Eintraege werden bewusst uebersprungen.

### S4 Sample- und Regression-Faelle

- [x] ✅ Mehrsprachige Samples mit absichtlich ausloesbaren Warnungen ergaenzen.
- [x] ✅ Mindestens ein Fehler-Sample fuer fehlende Artefakte.
- [x] ✅ Mindestens ein Warnungs-Sample fuer redaktionelle Notizen.
- [x] ✅ Snapshot- oder strukturierte JSON-Assertions fuer stabile Reports.

### S5 Seitenzahl-Zielkorridore

- [x] ✅ Optionale `pdf_targets` pro Profil unterstuetzen.
- [x] ✅ `target_pages_min`, `target_pages_max` und `warn_pages_max` je PDF
  auswerten.
- [x] ✅ Seitenzahlkorridore als projektspezifisch kennzeichnen, nicht als
  Worker-Default.

Beispiel:

```yaml
acceptance_profile:
  pdf_targets:
    source/publish/source-book.pdf:
      target_pages_min: 820
      target_pages_max: 850
      warn_pages_max: 875
    target-pl/publish/translated-book.pdf:
      target_pages_min: 820
      target_pages_max: 850
```

## Kann-Anforderungen

- [x] ✅ Statischen HTML-Report aus JSON-Reports generieren. Bewusst kein
  gehostetes Dashboard: `editorial_acceptance --html-output` erzeugt eine
  archivfeste Einzeldatei fuer Redaktion und Release-Review.
- [x] ✅ Visuelle Seiten-Snapshots fuer High-Risk-Seiten automatisiert
  vorbereiten. `--snapshot-dir` erzeugt immer einen HTML-/JSON-Index; wenn
  `pdftoppm` verfuegbar ist, werden PNG-Seitenbilder gerendert, sonst bleibt
  der Index als ehrlicher Fallback erhalten.
- [x] ✅ Baseline-Vergleich zwischen zwei Builds anbieten. Durch M14 umgesetzt;
  `editorial_acceptance --baseline` klassifiziert Befunde als `new`,
  `existing`, `changed` und `resolved`.
- [x] ✅ Trendmetriken fuer Seitenzahl, Findings und Warnungen ueber Releases
  sammeln. `--trend-output` haengt pro Acceptance-Lauf eine JSONL-Zeile an.
- [x] ✅ SARIF-Ausgabe fuer Code-Scanning-Oberflaechen pruefen.
  `editorial_metrics --sarif-output` schreibt SARIF 2.1.0 mit Severity- und
  Source-Line-Mapping, soweit Findings quelladressierbar sind.

## Generisches mehrsprachiges Abnahmeprofil Entwurf

```yaml
profiles:
  multilingual-release-candidate:
    network: false
    markdown:
      locale_field: content_lang
      identity_key: content_id
      source_link_field: source
      source_locale: ja
      target_locales:
        - pl
        - hr
        - no
      forbidden_frontmatter_keys:
        - lang
        - language
        - lang-version
      required_frontmatter_by_role:
        source:
          - content_id
          - content_lang
        target:
          - content_id
          - content_lang
          - source
          - status
      allowed_translation_status:
        - draft
        - in-review
        - approved
    pdf:
      low_text_page_threshold: 15
      very_low_text_page_threshold: 5
      overflow_warn_pt: 0.1
      overflow_fail_pt: 12.0
      required_fonts:
        - DejaVuSerif
        - DejaVuSans
        - DejaVuSansMono
        - TwemojiMozilla
        - ProjectCJK-Regular
    documentation:
      fail_on_stale_worker_version: true
      fail_on_stale_page_count: true
```

## Ergaenzte Abnahmeszenarien

| Szenario | Erwartung | Nachweis |
|---|---|---|
| Sauberes Sample | `passed` mit Markdown- und PDF-Metrikreport plus Markdown-Dossier. | `test_acceptance_passes_clean_sample` |
| Warnungs-Sample | `passed_with_warnings`, z. B. lange URL mit kleinem PDF-Ueberstand. | `test_metrics_writes_optional_csv_and_console_summary` |
| Fehler-Sample | `failed`, z. B. verbotener Frontmatter-Key, fehlender PDF-Font oder nicht lesbares Pflichtartefakt. | `test_acceptance_writes_dossier_and_returns_failure` und lokaler EN-Sample-Lauf vom 2026-05-10 |
| Blocked-Sample | `blocked`, wenn erwartete PDF/Markdown-Artefakte fehlen. | `test_publish_scope_uses_summary_and_blocks_missing_pdf` |
| Drift-Sample | `failed` oder `warn`, wenn Release-Doku eine alte Worker-Version oder alte Seitenzahlen behauptet. | `test_acceptance_derives_stale_report_findings` und `test_publish_metadata_summary_order_and_release_docs_drift` |
| Translation-Sample | Target-Datei ohne `source`/`status` oder mit falscher `content_id` erzeugt Befund. | `test_markdown_metrics_detect_generic_target_frontmatter_rules` und `test_markdown_metrics_detect_translation_content_id_mismatch` |
| Table-Sample | Tabellenstrategie-Report wird aggregiert und mindestens ein Landscape-/Fallback-Fall erscheint im Dossier. | `test_table_report_aggregation_flags_fallbacks` |
| Wenigzeiler-Sample | Textarme und leere Seiten werden reproduzierbar gezaehlt. | `test_pdf_metrics_detect_empty_text_layer` und `test_pdf_expected_page_rules_and_overflow_signals` |

## Finding-Modell

Jedes Finding soll diese Felder tragen:

| Feld | Bedeutung |
|---|---|
| `id` | stabile maschinenlesbare Finding-ID |
| `severity` | `info`, `warn`, `fail`, `blocked` |
| `category` | z. B. `markdown.structure`, `pdf.fonts`, `links`, `tables` |
| `artifact` | betroffene Datei, PDF oder Report |
| `location` | Datei, Zeile, Heading, PDF-Seite oder logisch beschriebene Stelle |
| `evidence` | knappe technische Evidenz |
| `editorial_impact` | redaktionelle Bedeutung in Klartext |
| `healing` | naechster sinnvoller Schritt |

## Implementierungsreihenfolge

1. Gemeinsames Report- und Finding-Modell definieren.
2. Stabile Finding-IDs und Baseline-Modell entwerfen.
3. Markdown-Metrikcollector mit strukturiertem JSON implementieren.
4. PDF-Metrikcollector auf vorhandenen PDF-Tools aufbauen.
5. Report-Drift, Artefakt-Frische und Seitenzahlkorridore implementieren.
6. Generisches Frontmatter- und Translation-Profil implementieren.
7. Tabellenstrategie-Aggregation und PDF-Layout-Findings integrieren.
8. Acceptance-Aggregator und Markdown-Dossier implementieren.
9. Manuelle Freigabevorlage und Restrisiko-Protokoll erzeugen.
10. Exit-Codes und Hilfetexte dokumentieren.
11. Orchestrator-Integration optional schalten.
12. Sample-Content und Regressionstests ergaenzen.

## Definition of Done

- [x] ✅ Konzept und Backlog sind aktuell verlinkt.
- [x] ✅ Anonymisiertes Kundenreview ist als Abnahmeergaenzung dokumentiert und
  umgesetzt.
- [x] ✅ Neue CLIs haben Tests, Typannotationen und klare Logs.
- [x] ✅ `python -m pytest gitbook_worker/tests -m "not slow"` bleibt gruen.
- [x] ✅ Mindestens ein lokaler DE- oder EN-Sample-Build erzeugt ein
  Abnahmedossier.
- [x] ✅ Alle acht ergaenzten Abnahmeszenarien sind als Tests oder Sample-Runs
  nachweisbar.
- [x] ✅ Die Doku erklaert, wie ein Redakteur das Dossier liest.
- [x] ✅ Neue Konfigurationsschluessel sind in der Konfigurationsreferenz
  statusmarkiert.
- [x] ✅ Exit-Codes sind dokumentiert und per CLI abrufbar.

Nachweis vom 2026-05-10:

- Lokaler EN-Sample-Lauf:
  `python -m gitbook_worker.tools.workflow_orchestrator run --root C:\gitbook-worker --content-config content.yaml --lang en --profile local --step publisher --step editorial-quality --quality-profile local`
- Erzeugte Dossier-Datei:
  `logs/quality/en-local-editorial-acceptance.md`
- Ergebnis: `failed` mit `1 fail`, `172 warn`, `19 info`; der Lauf ist damit
  ein ehrlicher Abnahmenachweis und kein Scheingruen.

## Offene redaktionelle Entscheidungen

- Welche Findings duerfen in `passed_with_warnings` verbleiben?
- Welche Sample-Seiten gelten als feste Release-Signale?
- Soll die Abnahme pro Sprache getrennt oder pro Gesamtprojekt erfolgen?
- Welche Kennzahlen sind reine Orientierung und welche koennen ein Gate werden?
- Wie stark duerfen Reports Textauszuege aus Kundendokumenten enthalten?