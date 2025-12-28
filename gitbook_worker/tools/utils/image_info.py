from __future__ import annotations

from pathlib import Path
from typing import Optional

from gitbook_worker.tools.logging_config import get_logger

try:  # Pillow is optional; we degrade gracefully when unavailable
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover - Pillow may be missing in some environments
    Image = None  # type: ignore

logger = get_logger(__name__)

_VECTOR_EXTENSIONS = {".svg", ".pdf"}


def get_image_width(path: Path) -> int:
    """Return image width in pixels or 0 if unknown.

    Vector formats (SVG/PDF) are intentionally skipped because they scale
    without loss; we log and return 0. Raster images are probed via Pillow
    when available. Any error yields 0 to keep preprocessing resilient.
    """

    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in _VECTOR_EXTENSIONS:
        logger.info("Überspringe Größenbestimmung für Vektorbild '%s'", path)
        return 0

    if not Image:
        logger.debug(
            "Pillow nicht verfügbar – überspringe Größenermittlung für %s", path
        )
        return 0

    if not path.exists():
        return 0

    try:
        abs_path = path.resolve()
    except Exception:
        abs_path = path

    try:
        with Image.open(abs_path) as im:
            return int(im.width)
    except Exception as exc:  # pragma: no cover - best effort only
        logger.warning("Could not open image '%s' to get size: %s", abs_path, exc)
        return 0
