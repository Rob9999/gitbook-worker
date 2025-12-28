from __future__ import annotations

from pathlib import Path

import pytest

from gitbook_worker.tools.utils.image_info import get_image_width


@pytest.fixture()
def svg_file(tmp_path: Path) -> Path:
    path = tmp_path / "demo.svg"
    path.write_text("<svg width='20' height='10'></svg>", encoding="utf-8")
    return path


def test_vector_images_return_zero_and_skip(svg_file: Path, caplog):
    caplog.set_level("INFO")

    width = get_image_width(svg_file)

    assert width == 0
    assert any("Vektorbild" in msg for msg in caplog.messages)


def test_missing_file_returns_zero(tmp_path: Path):
    missing = tmp_path / "missing.png"

    assert get_image_width(missing) == 0


def test_raster_image_width(tmp_path: Path):
    pytest.importorskip("PIL.Image")
    from PIL import Image

    path = tmp_path / "img.png"
    Image.new("RGB", (123, 45), color="red").save(path)

    assert get_image_width(path) == 123
