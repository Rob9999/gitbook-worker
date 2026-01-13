from __future__ import annotations

from pathlib import Path
from typing import Iterable

from gitbook_worker.core.ports.pdf_toc import PdfTocEntry, PdfTocExtractorPort


class PyPdfTocExtractor(PdfTocExtractorPort):
    name = "pypdf"

    def __init__(self) -> None:
        try:
            from pypdf import PdfReader  # type: ignore

            self._PdfReader = PdfReader
        except Exception:
            self._PdfReader = None

    def is_available(self) -> bool:
        return self._PdfReader is not None

    def _flatten_outline(
        self, outline: Iterable, reader, *, level: int = 1
    ) -> list[PdfTocEntry]:
        entries: list[PdfTocEntry] = []
        for item in outline:
            if isinstance(item, list):
                entries.extend(self._flatten_outline(item, reader, level=level + 1))
                continue

            title = getattr(item, "title", None) or str(item)
            try:
                page_index = reader.get_destination_page_number(item)
                page_num = page_index + 1
            except Exception:
                page_num = -1

            entries.append(
                PdfTocEntry(title=str(title).strip(), page=page_num, level=level)
            )
        return entries

    def extract(self, *, pdf_file: Path) -> list[PdfTocEntry]:
        if self._PdfReader is None:
            raise RuntimeError("pypdf is not available")

        reader = self._PdfReader(str(pdf_file))
        outline = getattr(reader, "outline", None) or getattr(reader, "outlines", None)
        if not outline:
            return []
        return self._flatten_outline(outline, reader)
