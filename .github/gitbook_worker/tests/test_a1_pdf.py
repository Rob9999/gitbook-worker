import locale
import pathlib
import re
import shutil
import subprocess

import pytest

from . import GH_TEST_ARTIFACTS_DIR, GH_TEST_OUTPUT_DIR, GH_TEST_LOGS_DIR

pytestmark = pytest.mark.skipif(
    shutil.which("lualatex") is None or shutil.which("pdfinfo") is None,
    reason="lualatex or pdfinfo not installed",
)


def test_generate_a1_pdf():
    # Make sure test artifacts directory exists
    test_dir = GH_TEST_ARTIFACTS_DIR / "test_generate_a1_pdf"
    test_dir.mkdir(exist_ok=True)

    # Make text file for A1 paper size (594mm x 841mm)
    name = "a1"
    tex_content = r"""
\documentclass{article}
\usepackage{geometry}
\geometry{paperwidth=594mm, paperheight=841mm, margin=20mm}
\begin{document}
A1 Test
\end{document}
"""
    tex_file = test_dir / f"{name}.tex"
    tex_file.write_text(tex_content, encoding="utf-8")

    subprocess.run(
        ["lualatex", "-interaction=nonstopmode", tex_file.name],
        cwd=test_dir,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    pdf_path = test_dir / f"{name}.pdf"
    assert pdf_path.is_file()

    info = subprocess.check_output(
        ["pdfinfo", str(pdf_path)],
        encoding=locale.getpreferredencoding(False),
        errors="replace",
    )
    print(info)
    match = re.search(r"Page size:\s+(\d+(?:\.\d+)?) x (\d+(?:\.\d+)?) pts", info)
    assert match, "pdfinfo output missing page size"
    width, height = float(match.group(1)), float(match.group(2))
    assert 1680 < width < 1690
    assert 2380 < height < 2390
    print(f"PDF saved to {test_dir / f'{name}.pdf'}")


def test_generate_a4_a1_a4_pdf():
    # Make sure test artifacts directory exists
    test_dir = GH_TEST_ARTIFACTS_DIR / "test_generate_a4_a1_a4_pdf"
    test_dir.mkdir(exist_ok=True)

    # Make text file for A1 paper size (594mm x 841mm)
    name = "a4_a1_a4_sequence"
    tex_content = r"""
\documentclass[a4paper]{article}
\usepackage{geometry}
\usepackage{lipsum}

\begin{document}
Normale A4-Seite mit Text.
\clearpage
\newgeometry{paperwidth=594mm, paperheight=841mm, margin=20mm}
\pagewidth=594mm
\pageheight=841mm
Dies sollte jetzt auf A1 laufen.
\clearpage
\restoregeometry
\pagewidth=210mm
\pageheight=297mm
Wieder A4.
\end{document}
"""
    tex_file = test_dir / f"{name}.tex"
    tex_file.write_text(tex_content, encoding="utf-8")

    subprocess.run(
        ["lualatex", "-interaction=nonstopmode", tex_file.name],
        cwd=test_dir,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    pdf_path = test_dir / f"{name}.pdf"
    assert pdf_path.is_file()

    # alle Seiteninfos holen
    info = subprocess.check_output(
        ["pdfinfo", "-f", "1", "-l", "3", str(pdf_path)],
        encoding=locale.getpreferredencoding(False),
        errors="replace",
    )
    print(info)

    # pro Seite die Größe auslesen
    page_sizes = re.findall(
        r"Page\s+\d+ size:\s+(\d+(?:\.\d+)?) x (\d+(?:\.\d+)?) pts", info
    )
    assert len(page_sizes) == 3

    # Punkte in mm umrechnen (1 pt = 1/72 in ≈ 0.35278 mm)
    pt_to_mm = 25.4 / 72.0
    sizes_mm = [(float(w) * pt_to_mm, float(h) * pt_to_mm) for w, h in page_sizes]

    # Erwartete Größen in mm
    expected = [
        (210, 297),  # A4
        (594, 841),  # A1
        (210, 297),  # A4
    ]

    for (w, h), (ew, eh) in zip(sizes_mm, expected):
        assert abs(w - ew) < 5, f"Breite stimmt nicht: {w} mm statt {ew} mm"
        assert abs(h - eh) < 5, f"Höhe stimmt nicht: {h} mm statt {eh} mm"

    print(f"PDF saved to {test_dir / f'{name}.pdf'}")
