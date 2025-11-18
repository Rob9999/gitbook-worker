from __future__ import annotations

import pytest
from tools.publishing import paper_info


def test_make_paper_info_standard_landscape() -> None:
    info = paper_info.make_paper_info("a4", landscape=True)
    assert info.size_mm == (297, 210)
    assert info.rotated is True
    assert info.standard is True


@pytest.mark.parametrize(
    "alias",
    ["din a4", "ISO A4", "A4p", "a4L"],
)
def test_get_valid_paper_measurements_alias(alias: str) -> None:
    info = paper_info.get_valid_paper_measurements(alias)
    assert info == paper_info.PAPER_INFOS["a4"]


def test_get_valid_paper_from_size() -> None:
    info = paper_info.get_valid_paper_measurements(paper=None, size_mm=(200, 300))
    assert info.norm_name == "a3"


def test_make_custom_paper_requires_size() -> None:
    with pytest.raises(ValueError):
        paper_info.make_paper_info("unknown")


def test_get_valid_custom_paper() -> None:
    info = paper_info.get_valid_paper_measurements(
        "myformat",
        standard=False,
        size_mm=(100, 200),
        margins_mm=(1, 2, 3, 4),
    )
    assert info.standard is False
    assert info.norm_name == "myformat"
