from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class PdfTocEntry:
    title: str
    page: int
    level: int


class PdfTocExtractorPort(Protocol):
    """Port for extracting a PDF table of contents (outline).

    Implementations may rely on optional third-party libraries.
    """

    name: str

    def is_available(self) -> bool:
        """Return True if this extractor can run in the current environment."""

    def extract(self, *, pdf_file: Path) -> list[PdfTocEntry]:
        """Extract table-of-contents entries from a PDF.

        Implementations should raise an Exception on failure.
        """
