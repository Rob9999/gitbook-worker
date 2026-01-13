from __future__ import annotations

from pathlib import Path

from gitbook_worker.core.ports.svg_to_pdf import SvgToPdfConverterPort


class CairoSvgSvgToPdfConverter(SvgToPdfConverterPort):
    name = "cairosvg"

    def __init__(self) -> None:
        try:
            from cairosvg import svg2pdf  # type: ignore

            self._svg2pdf = svg2pdf
        except Exception:
            self._svg2pdf = None

    def is_available(self) -> bool:
        return self._svg2pdf is not None

    def convert(self, *, svg_file: Path, pdf_file: Path) -> None:
        if self._svg2pdf is None:
            raise RuntimeError("cairosvg is not available")
        self._svg2pdf(url=str(svg_file), write_to=str(pdf_file))
