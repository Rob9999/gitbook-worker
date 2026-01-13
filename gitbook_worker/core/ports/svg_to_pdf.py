from __future__ import annotations

from pathlib import Path
from typing import Protocol


class SvgToPdfConverterPort(Protocol):
    """Port for converting an SVG file to a PDF file.

    Implementations may rely on optional third-party libraries.
    """

    name: str

    def is_available(self) -> bool:
        """Return True if this converter can run in the current environment."""

    def convert(self, *, svg_file: Path, pdf_file: Path) -> None:
        """Convert svg_file -> pdf_file.

        Implementations should raise an Exception on failure.
        """
