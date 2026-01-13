from __future__ import annotations

import os
from pathlib import Path

from gitbook_worker.core.ports.svg_to_pdf import SvgToPdfConverterPort


class SvglibSvgToPdfConverter(SvgToPdfConverterPort):
    name = "svglib"

    def __init__(self) -> None:
        try:
            from svglib.svglib import svg2rlg  # type: ignore
            from reportlab.graphics import renderPDF  # type: ignore

            self._svg2rlg = svg2rlg
            self._renderPDF = renderPDF
        except Exception:
            self._svg2rlg = None
            self._renderPDF = None

    def is_available(self) -> bool:
        return self._svg2rlg is not None and self._renderPDF is not None

    def convert(self, *, svg_file: Path, pdf_file: Path) -> None:
        if self._svg2rlg is None or self._renderPDF is None:
            raise RuntimeError("svglib/reportlab are not available")

        # svglib can be sensitive to working directory and relative paths.
        old_cwd = os.getcwd()
        try:
            os.chdir(svg_file.parent)
            drawing = self._svg2rlg(str(svg_file.name))
            if not drawing:
                raise ValueError("svglib could not parse SVG")
            self._renderPDF.drawToFile(drawing, str(pdf_file.name))
        finally:
            os.chdir(old_cwd)
