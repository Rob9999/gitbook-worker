#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV -> Markdown-Tabelle (+ optional Preview) und PNG-Chart
Usage-Beispiele siehe unten.
"""
import argparse, sys, textwrap
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def to_markdown_table(
    df: pd.DataFrame, floatfmt: str = ".3f", include_index: bool = False
) -> str:
    """Convert ``df`` to a Markdown table escaping LaTeX-sensitive chars."""

    def _escape(val: str) -> str:
        return val.replace("_", "\\_")

    # Werte formatieren (numerische Spalten)
    fmt_df = df.copy()
    for col in fmt_df.select_dtypes(include="number").columns:
        fmt_df[col] = fmt_df[col].map(lambda x: f"{x:{floatfmt}}")

    fmt_df = fmt_df.map(lambda x: _escape(x) if isinstance(x, str) else x)
    fmt_df.columns = [_escape(str(c)) for c in fmt_df.columns]
    return fmt_df.to_markdown(index=include_index)


def save_markdown(
    df: pd.DataFrame,
    out_md: Path,
    title: str | None = None,
    note: str | None = None,
    floatfmt: str = ".3f",
    include_index: bool = False,
    max_rows: int | None = None,
    title_level: int = 1,
    wide: str | None = None,
) -> None:
    out_md.parent.mkdir(parents=True, exist_ok=True)
    md_lines = []
    if wide:
        md_lines.append("```{=latex}\n" + wide + "\n```\n")
    if title:
        md_lines.append(f"{'#' * title_level} {title}\n")
    if note:
        md_lines.append(f"> {note}\n")
    if max_rows and max_rows > 0 and len(df) > max_rows:
        md_lines.append(
            f"_Hinweis: Tabelle zeigt die ersten {max_rows} von {len(df)} Zeilen._\n"
        )
        df_to_write = df.head(max_rows)
    else:
        df_to_write = df
    md_lines.append(
        to_markdown_table(df_to_write, floatfmt=floatfmt, include_index=include_index)
    )
    if wide:
        md_lines.append("```{=latex}\n\\WideEnd\n```")
    out_md.write_text("\n".join(md_lines), encoding="utf-8")


def save_chart(
    df: pd.DataFrame,
    out_png: Path,
    x: str,
    y_cols: list,
    kind: str = "line",
    title: str = None,
):
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.figure()
    if kind == "line":
        for yc in y_cols:
            plt.plot(df[x], df[yc], label=yc)
    elif kind == "bar":
        # Gruppiertes Balkendiagramm (breit nebeneinander)
        import numpy as np

        X = np.arange(len(df[x]))
        width = 0.8 / max(1, len(y_cols))
        for i, yc in enumerate(y_cols):
            plt.bar(X + i * width, df[yc], width=width, label=yc)
        plt.xticks(X + (len(y_cols) - 1) * width / 2, df[x], rotation=0)
    elif kind == "scatter":
        for yc in y_cols:
            plt.scatter(df[x], df[yc], label=yc)
    else:
        raise ValueError(f"Unbekannter Chart-Typ: {kind} (erlaubt: line, bar, scatter)")
    if title:
        plt.title(title)
    plt.xlabel(x)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=160)
    plt.close()


def main(argv=None):
    p = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Konvertiert CSV -> Markdown-Tabelle und PNG-Chart.",
        epilog=textwrap.dedent(
            """\
        Beispiele:
          1) Nur Markdown-Tabelle:
             python csv2md_and_chart.py --csv assets/csvs/deck-dimensions.csv \
                --out-md content/deck-specs-table.md \
                --title "Deck-Geometrien EVOL-00" --note "Quelle: deck-dimensions.csv" --floatfmt .2f

          2) Nur Chart:
             python csv2md_and_chart.py --csv assets/csvs/deck-dimensions.csv \
                --out-png assets/diagrams/deck-circumference.png \
                --chart-x Deck --chart-y Radius_m,Circumference_m --kind line --title "Deck-Radien & Umfänge"

          3) Beides zusammen:
             python csv2md_and_chart.py --csv assets/csvs/material-properties.csv \
                --out-md content/materials-table.md \
                --out-png assets/diagrams/material-density.png \
                --chart-x Material --chart-y Density_kg_m3 --kind bar --title "Dichte nach Material"
        """
        ),
    )
    p.add_argument("--csv", required=True, help="Pfad zur CSV-Datei")
    p.add_argument("--out-md", help="Ausgabedatei für Markdown-Tabelle (*.md)")
    p.add_argument("--out-png", help="Ausgabedatei für PNG-Chart (*.png)")
    p.add_argument("--title", help="Titel für Tabelle/Chart")
    p.add_argument(
        "--note", help="zusätzliche Notiz für die Markdown-Datei (Quelle, Version etc.)"
    )
    p.add_argument(
        "--floatfmt", default=".3f", help="Format für numerische Werte (default: .3f)"
    )
    p.add_argument(
        "--include-index", action="store_true", help="Indexspalte in Tabelle aufnehmen"
    )
    p.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="Optional: nur die ersten N Zeilen in die Tabelle schreiben",
    )
    p.add_argument(
        "--title-level",
        type=int,
        default=1,
        help="Überschriften-Level für den Tabellentitel (default: 1)",
    )
    p.add_argument(
        "--wide",
        choices=["A3", "A2", "A1"],
        help="Tabelle in Querformat mit A3/A2/A1-Papier einbetten",
    )

    # CSV-Parsing-Optionen (deutsche CSVs, Semikolon/Komma):
    p.add_argument(
        "--sep",
        default=None,
        help="Trennzeichen (z.B. ';'). Wenn leer, wird auto-erkundet.",
    )
    p.add_argument(
        "--decimal",
        default=".",
        help="Dezimaltrennzeichen ('.' oder ','); default: '.'",
    )

    # Chart-Optionen:
    p.add_argument("--chart-x", help="Spaltenname für X-Achse")
    p.add_argument("--chart-y", help="Komma-separierte Liste von Y-Spalten")
    p.add_argument(
        "--kind",
        choices=["line", "bar", "scatter"],
        default="line",
        help="Diagrammtyp (default: line)",
    )

    args = p.parse_args(argv)

    csv_path = Path(args.csv)
    if not csv_path.exists():
        sys.exit(f"CSV nicht gefunden: {csv_path}")

    df = pd.read_csv(csv_path, sep=args.sep, decimal=args.decimal)

    # Markdown
    if args.out_md:
        save_markdown(
            df=df,
            out_md=Path(args.out_md),
            title=args.title,
            note=args.note,
            floatfmt=args.floatfmt,
            include_index=args.include_index,
            max_rows=args.max_rows,
            title_level=args.title_level,
            wide={
                "A3": "\\WideStartAthree",
                "A2": "\\WideStartAtwo",
                "A1": "\\WideStartAone",
            }.get(args.wide),
        )

    # Chart
    if args.out_png:
        if not args.chart_x or not args.chart_y:
            sys.exit("--out-png erfordert --chart-x und --chart-y")
        y_cols = [c.strip() for c in args.chart_y.split(",") if c.strip()]
        for c in [args.chart_x] + y_cols:
            if c not in df.columns:
                sys.exit(
                    f"Spalte '{c}' nicht in CSV gefunden. Verfügbare Spalten: {list(df.columns)}"
                )
        save_chart(
            df=df,
            out_png=Path(args.out_png),
            x=args.chart_x,
            y_cols=y_cols,
            kind=args.kind,
            title=args.title,
        )

    if not args.out_md and not args.out_png:
        sys.exit("Nichts zu tun: Bitte --out-md und/oder --out-png angeben.")


if __name__ == "__main__":
    main()
