---
version: 0.2.0
date: 2026-05-09
status: implemented
history:
    - "0.2.0: 2026-05-09 - Tabellenprofi implementation concept and editorial score model added."
    - "0.1.0: 2026-05-09 - Initial backlog note with current table paper strategy and editorial critique of missing layout-cost model."
---

Ich schaue mir zuerst die aktuelle Tabellen-/Papierwahl direkt im Code und in der Doku an, damit die Beschreibung nicht aus der Erinnerung kommt, sondern exakt den Stand nach v2.7.0 trifft.

Searched for regex `def paper_for_table|def paper_for_table_width|def paper_for_columns|estimate_table_width_mm|available_text_width_mm|MIN_COLS_FOR_WRAP|TABLE_WIDTH_SAFETY_FACTOR` (`**/gitbook_worker/tools/publishing/**`), 17 results

Searched for regex `wide-table|Wide-Table|paper selection|Papier|Tabelle|table width|A1` (`**/docs/**`), 74 results

Searched for regex `test_table_width_uses_usable_text_area|test_table_with_long_cells_uses_content_width|test_table_roehrenmodell|wide_content_table` (`**/gitbook_worker/tests/test_preprocess_md.py`), 5 results

Ich habe die Stellen gefunden: die eigentliche Entscheidung sitzt in preprocess_md.py, flankiert von Paper-Metadaten und ein paar Regressionstests. Ich lese jetzt die relevanten Funktionen und Tests zusammenhängend.

Read [](file:///c%3A/gitbook-worker/gitbook_worker/tools/publishing/preprocess_md.py#45-45), lines 45 to 85

Read [](file:///c%3A/gitbook-worker/gitbook_worker/tools/publishing/preprocess_md.py#340-340), lines 340 to 535

Read [](file:///c%3A/gitbook-worker/gitbook_worker/tools/publishing/preprocess_md.py#690-690), lines 690 to 735

Read [](file:///c%3A/gitbook-worker/gitbook_worker/tests/test_preprocess_md.py#1-1), lines 1 to 125

Read [](file:///c%3A/gitbook-worker/gitbook_worker/tests/test_preprocess_md.py#205-205), lines 205 to 228

Read [](file:///c%3A/gitbook-worker/gitbook_worker/tools/publishing/paper_info.py#1-1), lines 1 to 145

Read [](file:///c%3A/gitbook-worker/gitbook_worker/tools/publishing/preprocess_md.py#526-526), lines 526 to 610

Read [](file:///c%3A/gitbook-worker/gitbook_worker/tools/publishing/preprocess_md.py#610-610), lines 610 to 682

Read [](file:///c%3A/gitbook-worker/gitbook_worker/tools/publishing/preprocess_md.py#682-682), lines 682 to 710

Searched for regex `def _paper_candidates|candidate_codes` (`**/gitbook_worker/tools/publishing/preprocess_md.py`), 6 results

Read [](file:///c%3A/gitbook-worker/gitbook_worker/tools/publishing/preprocess_md.py#300-300), lines 300 to 355

**Aktuelle Strategie**

Stand `v2.7.0`: Die Tabellenlogik sitzt im Wesentlichen in preprocess_md.py, die Papierformate in paper_info.py.

```markdown
# Aktuelle Wide-Table-Papierstrategie

## 1. Tabellen-Erkennung

Eine Tabelle wird als GitHub-/Markdown-Pipe-Tabelle erkannt, wenn:

- die aktuelle Zeile ein `|` enthält
- die nächste Zeile eine Separator-Zeile ist, z. B. `|---|---|`
- nachfolgende nicht-leere Zeilen mit `|` zur Tabelle gehören

## 2. Kandidaten für Papierformate

Die Auswahl läuft über diese feste Reihenfolge:

1. aktuelles Basisformat, z. B. `a4`
2. `a4`
3. `a4-landscape`
4. `a3`
5. `a3-landscape`
6. `a2`
7. `a2-landscape`
8. `a1`
9. `a1-landscape`

Duplikate werden entfernt. Wenn das Basisformat selbst in der Liste vorkommt, startet die Suche danach.

Die verfügbare Textbreite ist:

```text
Papierbreite - linker Rand - rechter Rand
```

Beispiele:

- A4 hoch: `210 - 15 - 15 = 180 mm`
- A4 quer: `297 - 15 - 15 = 267 mm`
- A3 quer: `420 - 15 - 15 = 390 mm`
- A1 quer: `841 - 20 - 20 = 801 mm`

--> sollte default (wo sind die smart defaults) sein und darüberhinaus sollen im publish.yaml andere und custom Formate eingetragen werden können

## 3. Alte Untergrenze: Spaltenanzahl

Die alte Heuristik lebt weiter:

```text
Mindestbreite = Spaltenanzahl * 25 mm
```

Das ist `COLUMN_WIDTH_mm = 25`.

Beispiele:

- 10 Spalten → 250 mm
- 11 Spalten → 275 mm
- 15 Spalten → 375 mm

Diese Heuristik prüft gegen die rohe Papierbreite, nicht gegen die nutzbare Breite nach Rändern.

## 4. Neue v2.7.0-Heuristik: geschätzte Zelltextbreite

Zusätzlich wird die echte Tabellenbreite heuristisch geschätzt:

1. Separator-Zeilen werden ignoriert.
2. Jede Tabellenzeile wird in Zellen zerlegt.
3. Markdown wird für die Messung vereinfacht:
   - Links werden auf ihr Label reduziert.
   - Bilder werden auf ihr Alt-Label reduziert.
   - Code-Spans werden auf den Code-Inhalt reduziert.
   - HTML-Tags werden entfernt.
   - einfache Markdown-Style-Marker werden entfernt.
4. Pro Zeichen wird eine grobe Breite geschätzt:
   - CJK/fullwidth: breiter
   - Großbuchstaben: etwas breiter
   - schmale Zeichen wie `i`, `l`, `.`: schmaler
   - Symbole: relativ breit
5. Pro Spalte zählt die breiteste Zelle.
6. Jede Spalte bekommt mindestens `8 mm`.
7. Pro Spalte kommen `4.5 mm` Padding dazu.
8. Das Ergebnis wird mit `1.06` Sicherheitsfaktor multipliziert.

Kurzform:

```text
Tabellenbreite =
  Summe(maximale Zelltextbreite je Spalte)
  + Spaltenanzahl * 4.5 mm Padding

Endwert = Tabellenbreite * 1.06
```

## 5. Auswahlentscheidung

Es werden zwei Papierentscheidungen berechnet:

```text
paper_by_columns = Papier nach Spaltenanzahl
paper_by_width   = Papier nach geschätzter Zelltextbreite
```

Danach wird das größere der beiden genommen, gemessen an nutzbarer Textbreite.

Also:

```text
Wenn paper_by_width mehr nutzbare Breite hat als paper_by_columns:
    nimm paper_by_width
sonst:
    nimm paper_by_columns
```

Damit bleibt die alte Spaltenlogik als Untergrenze erhalten, aber lange Zelltexte können ein größeres Format erzwingen, auch wenn die Tabelle nur wenige Spalten hat.

## 6. Oversize-Fallback

Wenn die geschätzte Zelltextbreite größer ist als alles, was die unterstützten Standardformate bieten, passiert aktuell bewusst kein automatischer Sprung auf ein Scheinformat.

Stattdessen:

```text
Wenn geschätzte Breite > maximale Standard-Textbreite:
    Warnung loggen
    paper_by_columns behalten
```

Das schützt bestehende Sonderfälle wie extrem breite technische Tabellen, bei denen auch A1 quer nicht wirklich reichen würde.

## 7. Wann wird der Tabellenblock umgebaut?

Ein Tabellenblock wird in einen LaTeX-`longtable`-Block mit temporärer Geometrie gewandelt, wenn:

```text
gewähltes Papier != aktuelles Papier
oder
Spaltenanzahl >= 10
```

`MIN_COLS_FOR_WRAP = 10`.

Dabei werden unmittelbar vor der Tabelle stehende Überschriften, Leerzeilen und Blockquotes mit in den breiten Block gezogen. Danach wird per `\restoregeometry` wieder auf das vorherige Papierformat zurückgestellt.

## 8. Was die Strategie aktuell nicht tut

Die aktuelle Strategie misst nicht exakt mit TeX.

Sie simuliert auch nicht:

- ob Zellen auf kleinerem Papier umbrechen würden
- wie hoch Zeilen durch Umbruch werden
- ob eine größere Seite besser wäre als hohe, mehrfach umbrechende Spalten
- eine Kostenfunktion wie „lieber A3 quer als A4 mit sehr hohen Zeilen“
- konfigurierbare Schwellen pro Projekt oder pro Tabelle
- Skalierung, Landscape-Priorität oder explizite Per-Table-Overrides


--> Wir müssen das erreichen!

Die Logik ist also aktuell:

> „Nimm mindestens das Format nach Spaltenanzahl, und wenn der geschätzte ungebrochene Zelltext mehr nutzbare Breite braucht, nimm das nächstgrößere Standardformat. Wenn selbst A1 quer nicht reicht, bleib beim alten Fallback und warne.“
```

Kurz gesagt: Die v2.7.0-Strategie ist schon deutlich intelligenter als reine Spaltenzählung, aber sie hat noch kein echtes Layout-Kostenmodell. Genau dort liegt vermutlich der nächste sinnvolle Schritt: nicht nur „passt die geschätzte Breite?“, sondern „was ist lesbarer: kleineres Papier mit hohen umbrochenen Zellen oder größeres Papier mit stabilerer Zeilenhöhe?“.

## Redaktionelle Kritik zu Punkt 8

Aus redaktioneller Sicht ist Punkt 8 der Kern des Problems, aber noch zu technisch-negativ formuliert: Er beschreibt, was die Maschine nicht kann, sagt aber noch nicht klar genug, welche publizistische Qualität am Ende erreicht werden muss. Für Kundendokumente reicht „passt irgendwie auf die Seite“ nicht. Eine Tabelle muss lesbar, vergleichbar und als Tabelle erkennbar bleiben.

Die bisherige Strategie behandelt Papierwahl primär als Breitenproblem. Redaktionell ist es aber ein Layout- und Leseproblem: Wenn ein kleineres Papierformat dazu führt, dass Zellen in viele schmale Zeilen zerfallen, entstehen hohe Tabellenzeilen, unruhige Seiten, schlechte Vergleichbarkeit zwischen Spalten und im schlimmsten Fall ein formal gültiges, aber praktisch unbrauchbares PDF. Genau das muss die nächste Strategie verhindern.

### Zusätzliche redaktionelle Forderungen

- Die Entscheidung darf nicht nur fragen, ob die ungebrochene Tabelle in eine nutzbare Breite passt. Sie muss bewerten, wie stark Zelltexte auf jedem Kandidatenpapier umbrechen würden.
- Für jedes Kandidatenformat soll ein Layout-Score berechnet werden: erwartete Zeilenumbrüche pro Zelle, maximale Zeilen pro Tabellenzeile, durchschnittliche Zeilenhöhe, Anzahl sehr schmaler Spalten, Verhältnis von Inhaltsbreite zu nutzbarer Breite und erwartete Seitenwirkung.
- Ein größeres Papierformat soll gewählt werden, sobald das kleinere Format zwar technisch passt, aber redaktionell schlechte Tabellen erzeugt, etwa durch sehr hohe Zeilen, stark zerhackte Überschriften oder wiederholte 1-Wort-Zeilen.
- Die Strategie soll kleinere Standardformate bevorzugen, solange die Tabelle gut lesbar bleibt. Der Sprung auf A3/A2/A1 muss begründet sein, aber nicht zu spät kommen.
- Querformat derselben Papierklasse soll als natürlicher erster Entlastungsschritt gelten, bevor auf die nächste Papierklasse gewechselt wird.
- Für Prosa-Tabellen, Entscheidungstabellen und Governance-/Kriterienmatrizen müssen andere Schwellen gelten als für rein numerische Tabellen. Lange natürlichsprachliche Zellen brauchen mehr Breite, numerische Tabellen dürfen dichter sein.
- Tabellenüberschriften und Kopfzeilen müssen besonders gewichtet werden. Eine Tabelle mit zerbrochenen Headern ist redaktionell oft schlechter als eine Tabelle mit etwas breiterem Papier.
- Die Strategie muss Mindestbreiten pro Spaltentyp kennen oder ableiten: Code-/ID-Spalten schmal, Status-/Kurzlabel-Spalten mittel, Kommentar-/Begründungsspalten breit.
- Markdown-Links, URLs, Code-Spans, CJK/Emoji und lange zusammengesetzte deutsche Wörter müssen als eigene Risikofaktoren in die Messung eingehen.
- Oversize darf nicht still auf eine alte Heuristik zurückfallen. Wenn kein Standardpapier eine redaktionell brauchbare Lösung bietet, soll ein klarer Diagnosehinweis entstehen: Tabelle teilen, Spalten kürzen, Custom-Paper erlauben, redaktionell umstrukturieren oder bewusst per Override freigeben.
- Die Standardstrategie soll intelligent bleiben und ohne neue Konfiguration funktionieren. Steuerbarkeit ist als Escape Hatch sinnvoll, darf aber nicht zur Pflicht werden.
- Falls neue Schalter eingeführt werden, müssen sie in `publish.yml`/Defaults dokumentiert, in der Konfigurationsreferenz statusmarkiert und mit Tests abgedeckt werden.
- `publish.yml` soll perspektivisch zusätzliche Standard- und Custom-Paper-Kandidaten zulassen, damit Kundenformate oder Druckdienstleister-Vorgaben nicht hart im Code landen.
- Pro Tabelle sollte optional ein Override möglich sein, z. B. fuer bewusst gesetzte Sondertabellen. Dieser Override muss sichtbar und reviewbar sein, nicht implizit über fragilen Textinhalt.
- Die Build-Logs sollen die Entscheidung erklären: gemessene Spaltenzahl, geschätzte Breite, Kandidaten-Scores, gewähltes Format und Grund für den Sprung.
- Für QA sollte ein maschinenlesbarer Tabellenlayout-Report entstehen können, damit Kundenproblemfälle reproduzierbar geprüft werden können.
- Sample-Content muss mehrere redaktionelle Fälle abdecken: lange Prosa-Entscheidungstabelle, viele kurze numerische Spalten, sehr lange URLs/Code-Spans, CJK/Emoji-Zellen, anonyme Kundentabelle und Oversize-Fall mit erwarteter Warnung.

### Redaktionelles Zielbild

Die nächste Strategie sollte nicht „größtmögliches Papier bei breiter Tabelle“ sein, sondern eine nachvollziehbare Best-Fit-Entscheidung:

> Wähle das kleinste zulässige Papierformat, auf dem die Tabelle ohne unzumutbare Zellumbrüche, ohne extreme Zeilenhöhen und ohne Verlust der spaltenweisen Vergleichbarkeit lesbar bleibt.

Damit wird die Papierwahl zu einer redaktionellen Qualitätsentscheidung statt zu einer reinen Breitenheuristik.

## Umsetzung Tabellenprofi

Die Anforderungen werden im Release **Tabellenprofi** umgesetzt. Das
Implementierungskonzept liegt in
[gitbook_worker/docs/concepts/table-paper-strategy.md](../concepts/table-paper-strategy.md).

Wichtig: Lange Wörter sind kein deutsches Sonderproblem. Das Score-Modell
bewertet lange Token und lange Script-Runs allgemein. CJK/Hangul/Kana-Zeichen
werden als breite Glyphen in Zeilenschätzungen einbezogen, aber nicht pauschal
als ein untrennbares Latin-Token behandelt, weil natürliche CJK-Zeilenumbrüche
zeichenweise möglich sind.