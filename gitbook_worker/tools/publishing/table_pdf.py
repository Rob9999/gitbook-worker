"""Helpers for exporting wide tables to PDF with automatic paper sizing."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

# Paper sizes in millimetres (landscape orientation: width > height)
PAPER_SIZES_MM = {
    "A4": (297, 210),
    "A3": (420, 297),
    "A2": (594, 420),
    "A1": (841, 594),
}
PAPER_SEQUENCE = ["A4", "A3", "A2", "A1"]


def choose_paper_size(
    num_columns: int, col_width_mm: float = 20, margin_mm: float = 20
) -> str:
    """Return the smallest paper size that fits the table.

    Parameters
    ----------
    num_columns:
        Number of columns in the table.
    col_width_mm:
        Assumed width of each column in millimetres.
    margin_mm:
        Margin around the table in millimetres.
    """
    required_width = num_columns * col_width_mm + 2 * margin_mm
    for size in PAPER_SEQUENCE:
        if required_width <= PAPER_SIZES_MM[size][0]:
            return size
    return "A1"


def save_table_pdf(
    df: pd.DataFrame,
    out_path: Path,
    *,
    col_width_mm: float = 20,
    row_height_mm: float = 8,
    margin_mm: float = 20,
    font_size: int = 6,
) -> str:
    """Save *df* to *out_path* as a PDF with automatically selected paper size.

    Returns the chosen paper size.
    """
    flat_df = df.copy()
    flat_df.columns = [
        (
            " ".join(map(str, c)).strip()
            if isinstance(c, Iterable) and not isinstance(c, str)
            else str(c)
        )
        for c in flat_df.columns
    ]
    paper = choose_paper_size(len(flat_df.columns), col_width_mm, margin_mm)
    page_w, page_h = PAPER_SIZES_MM[paper]
    fig, ax = plt.subplots(figsize=(page_w / 25.4, page_h / 25.4))
    ax.axis("off")
    table = ax.table(
        cellText=flat_df.values,
        colLabels=flat_df.columns,
        loc="upper left",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    scale_x = (page_w - 2 * margin_mm) / (len(flat_df.columns) * col_width_mm)
    scale_y = row_height_mm / 10
    table.scale(scale_x, scale_y)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out_path) as pdf:
        pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)
    return paper
