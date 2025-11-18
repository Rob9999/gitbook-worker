from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple
from tools.logging_config import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class PaperInfo:
    norm_name: str  # z.B. 'a4'
    standard: bool  # True=Standardformat, False=Customformat
    rotated: bool  # False=Hochformat, True=Querformat
    size_mm: Tuple[int, int]  # (w, h)
    margins_mm: Tuple[int, int, int, int]  # (left, top, right, bottom)

    def __str__(self):
        return (
            f"PaperInfo(norm_name={self.norm_name}, rotated={self.rotated}, "
            f"size_mm={self.size_mm}, margins_mm={self.margins_mm})"
        )

    @staticmethod
    def default():
        return PAPER_INFOS["a4"]


# ---------- Papier-Mapping (ISO 216 / DIN) ----------
BASE_SIZES_MM: Dict[str, Tuple[int, int]] = {
    "a0": (841, 1189),
    "a1": (594, 841),
    "a2": (420, 594),
    "a3": (297, 420),
    "a4": (210, 297),
    "a5": (148, 210),
    "a6": (105, 148),
}

DEFAULT_MARGINS_MM: Dict[str, Tuple[int, int, int, int]] = {
    # (left, top, right, bottom)
    "a4": (15, 15, 15, 15),
    "a3": (15, 15, 15, 15),
    "a2": (18, 18, 18, 18),
    "a1": (20, 20, 20, 20),
}

ALIASES = {
    "din a4": "a4",
    "iso a4": "a4",
    "a4p": "a4",
    "a4portrait": "a4",
    "a4l": "a4",
    "a4landscape": "a4",
}


def _get_default_margins(
    paper: str, rotated: bool = False
) -> Tuple[int, int, int, int]:
    margin = DEFAULT_MARGINS_MM.get(paper, (15, 15, 15, 15))
    if rotated:  # rotate clockwise
        margin = (
            margin[1],
            margin[2],
            margin[3],
            margin[0],
        )  # left, top, right, bottom
    return margin


def _check_alias(code: str = None) -> str:
    return (
        ALIASES.get(code.lower().replace("-", "").replace("_", ""), code.lower())
        if code
        else None
    )


def _rotate_paper_measurements(
    size_mm: Tuple[int, int],
    margins_mm: Tuple[int, int, int, int],
    rotated: bool,
) -> Tuple[Tuple[int, int], Tuple[int, int, int, int]]:
    w, h = size_mm
    l, t, r, b = margins_mm
    if rotated:
        return (h, w), (t, r, b, l)  # rotate clockwise
    return (w, h), (l, t, r, b)


def _get_custom_paper_name(
    paper: str,
    size_mm: Tuple[int, int],
    margins_mm: Tuple[int, int, int, int],
    rotated: bool = False,
) -> str:
    (w, h), (l, t, r, b) = _rotate_paper_measurements(size_mm, margins_mm, rotated)
    return f"custom_{paper}_{w}x{h}_{l}-{t}-{r}-{b}"


def make_paper_info(
    code: str,
    *,
    landscape: bool = False,
    size_mm: Tuple[int, int] = None,
    margins_mm: Tuple[int, int, int, int] = (15, 15, 15, 15),
) -> PaperInfo:
    code_norm = _check_alias(code)
    if code_norm not in BASE_SIZES_MM:
        if not size_mm:
            raise ValueError(f"Unsupported paper code: {code!r} and nor size_mm given")
        # keep custom size
        standard = False
    else:
        # set standard size
        std_size_mm = BASE_SIZES_MM[code_norm]
        standard = True
        if size_mm:
            w, h = size_mm
            if std_size_mm[0] != w or std_size_mm[1] != h:
                logger.info(
                    "Using standard paper size: %s. Discarding custom size_mm %s.",
                    code_norm,
                    size_mm,
                )
        size_mm = std_size_mm
    # Get paper name
    paper_name = (
        code_norm
        if code_norm
        else _get_custom_paper_name(
            code, size_mm=size_mm, margins_mm=margins_mm, rotated=landscape
        )
    )
    # consider rotation
    (w, h), (l, t, r, b) = _rotate_paper_measurements(size_mm, margins_mm, landscape)
    return PaperInfo(
        norm_name=paper_name,
        standard=standard,
        rotated=landscape,
        size_mm=(w, h),
        margins_mm=(l, t, r, b),
    )


PAPER_INFOS: Dict[str, PaperInfo] = {
    "a4": make_paper_info(
        "a4", landscape=False, margins_mm=_get_default_margins("a4", False)
    ),
    "a4-landscape": make_paper_info(
        "a4", landscape=True, margins_mm=_get_default_margins("a4", True)
    ),
    "a3": make_paper_info(
        "a3", landscape=False, margins_mm=_get_default_margins("a3", False)
    ),
    "a3-landscape": make_paper_info(
        "a3", landscape=True, margins_mm=_get_default_margins("a3", True)
    ),
    "a2": make_paper_info(
        "a2", landscape=False, margins_mm=_get_default_margins("a2", False)
    ),
    "a2-landscape": make_paper_info(
        "a2", landscape=True, margins_mm=_get_default_margins("a2", True)
    ),
    "a1": make_paper_info(
        "a1", landscape=False, margins_mm=_get_default_margins("a1", False)
    ),
    "a1-landscape": make_paper_info(
        "a1", landscape=True, margins_mm=_get_default_margins("a1", True)
    ),
}


# Get valid paper measurements, standard or custom
def get_valid_paper_measurements(
    paper: str = None,
    *,
    standard: bool = True,
    landscape: bool = False,
    size_mm: Tuple[int, int] = None,
    margins_mm: Tuple[int, int, int, int] = (15, 15, 15, 15),
) -> PaperInfo:
    """
    Return valid PaperInfo for given paper specification.
    If ``standard`` is True, only standard paper formats are returned.
    If ``standard`` is False, custom paper formats are also allowed.
    If ``paper`` is None, ``size_mm`` is used to find fitting standard paper.
    If ``size_mm`` is None or invalid, and no standard paper is selected then A4 size is used (landscape or portrait).
    If ``margins_mm`` is not given, default margins for standard paper are used.
    Converts ``paper`` aliases to standard names.
    Considers ``-landscape`` or ``-portrait`` suffixes in ``paper`` to set orientation.
    Returns: PaperInfo
    """
    paper_lower = paper.lower() if paper else None
    correct_paper_name = _check_alias(paper)
    # if paper is None, check size_mm
    if not paper and size_mm:
        # find fitting standard paper
        w = size_mm[0] if size_mm[0] and size_mm[0] > 0 else 0
        h = size_mm[1] if size_mm[1] and size_mm[1] > 0 else 0
        logger.info("Finding fitting standard paper for size_mm=%s", size_mm)
        # use fitting standard paper
        for _, paper_info in sorted(PAPER_INFOS.items(), key=lambda x: x[1].size_mm):
            max_w = paper_info.size_mm[0]
            max_h = paper_info.size_mm[1]
            if w > max_w or h > max_h:
                logger.debug(
                    "desired %smm x%smm - %s too small %smm x%smm",
                    w,
                    h,
                    paper_info.norm_name,
                    max_w,
                    max_h,
                )
                continue
            logger.info(
                "For desired %smm x%smm - using standard paper %s %smm x%smm",
                w,
                h,
                paper_info.norm_name,
                max_w,
                max_h,
            )
            return paper_info
        if standard:
            # return biggest standard paper
            return PAPER_INFOS.get("a1-landscape")
        else:
            # no fitting standard paper found, return custom paper with given size_mm
            logger.warning(
                "No fitting standard paper found for size_mm=%s. Using custom paper.",
                size_mm,
            )
            size_mm = (w if w > 0 else 210, h if h > 0 else 297)
            return make_paper_info(
                (
                    correct_paper_name
                    if correct_paper_name
                    else _get_custom_paper_name(
                        paper, size_mm=size_mm, margins_mm=margins_mm, rotated=landscape
                    )
                ),
                landscape=landscape,
                size_mm=size_mm,
                margins_mm=margins_mm,
            )

    # check for landscape/portrait suffix
    if paper_lower and paper_lower.endswith("-landscape"):
        landscape = True
        paper = paper[: -len("-landscape")]  # remove '-landscape'
    elif paper_lower and paper_lower.endswith("landscape"):
        landscape = True
        paper = paper[: -len("landscape")]  # remove 'landscape'
    elif paper_lower and paper_lower.endswith("-portrait"):
        landscape = False
        paper = paper[: -len("-portrait")]  # remove '-portrait'
    elif paper_lower and paper_lower.endswith("portrait"):
        landscape = False
        paper = paper[: -len("portrait")]  # remove 'portrait'
    # prioritize standard paper if requested

    # get correct paper code
    correct_paper_name = _check_alias(paper)
    # first try to find standard paper
    preferred_key = correct_paper_name
    if landscape and correct_paper_name:
        landscape_key = f"{correct_paper_name}-landscape"
        if landscape_key in PAPER_INFOS:
            preferred_key = landscape_key

    paper_info = PAPER_INFOS.get(preferred_key, None)
    if paper_info and standard:
        return paper_info
    # then try matching standard paper with correct orientation
    if paper_info and not standard:
        # check measurements, if given: if match, return standard paper
        if size_mm:
            if (
                paper_info.size_mm == size_mm
                and paper_info.rotated == landscape
                and paper_info.margins_mm == margins_mm
            ):
                return paper_info
        else:
            # no size_mm given, return standard paper if orientation and margins match
            if paper_info.rotated == landscape and paper_info.margins_mm == margins_mm:
                return paper_info

    # --- No standard paper found or requested, check custom paper ---

    # no or invalid size_mm given, take "a4" sizes
    if size_mm is None or size_mm[0] <= 0 or size_mm[1] <= 0:
        size_mm = BASE_SIZES_MM.get("a4", (210, 297))
    # finally, create custom paper
    return make_paper_info(
        (
            correct_paper_name
            if correct_paper_name
            else _get_custom_paper_name(paper, size_mm, margins_mm, rotated=landscape)
        ),
        landscape=landscape,
        size_mm=size_mm,
        margins_mm=margins_mm,
    )
