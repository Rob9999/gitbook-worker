import difflib
import re
from pathlib import Path

import pytest
from tools.publishing import preprocess_md


def _wide_table(tmp_path, cols: int):
    md = tmp_path / "table.md"
    header = "|" + "|".join([f"c{i}" for i in range(cols)]) + "|"
    sep = "|" + "|".join(["---"] * cols) + "|"
    row = "|" + "|".join(["1"] * cols) + "|"
    content = "\n".join(["#### Heading", "", "> note", header, sep, row])
    md.write_text(content, encoding="utf-8")
    return md


def test_html_figure_block_converted(tmp_path):
    md = tmp_path / "figure.md"
    md.write_text(
        """
<figure><img src=".gitbook/assets/example.png" alt="Sample Alt"><figcaption><p>Beispiel Caption</p></figcaption></figure>
""".strip(),
        encoding="utf-8",
    )

    out = preprocess_md.process(str(md), paper_format="a4")

    assert "<figure" not in out
    assert ".gitbook/assets/example.png" in out
    assert "![Beispiel Caption](.gitbook/assets/example.png){fig-alt=\"Sample Alt\"}" in out


def test_table_wrapped_portrait(artifact_dir):
    md = _wide_table(artifact_dir, cols=15)
    out = preprocess_md.process(str(md), paper_format="a4")
    assert_geometry(out, expected_w=420, expected_h=297)


def test_table_wrapped_landscape_enabled(artifact_dir):
    md = _wide_table(artifact_dir, cols=11)
    out = preprocess_md.process(str(md), paper_format="a4")
    assert_geometry(out, expected_w=297, expected_h=210)


# Robustes Pattern mit benannten Gruppen, toleriert Whitespace/optional "mm"
GEOM_RE = re.compile(
    r"""
    \\newgeometry\{              # Befehl
    \s*paperwidth=(?P<w>\d+)(?:mm)?   # Breite
    ,\s*paperheight=(?P<h>\d+)(?:mm)? # Höhe
    [^}]*\}                       # Rest bis zur schließenden Klammer
    """,
    re.VERBOSE,
)


# Prüfe, ob die Geometrieangaben im Text den Erwartungen entsprechen
def assert_geometry(out: str, expected_w: int, expected_h: int) -> None:
    m = GEOM_RE.search(out)
    if not m:
        snippet = out[:500] + ("..." if len(out) > 500 else "")
        pytest.fail(
            "newgeometry not found.\n"
            "--- Output snippet (first 500 chars) ---\n"
            f"{snippet}"
        )

    found_w, found_h = int(m["w"]), int(m["h"])
    if (found_w, found_h) != (expected_w, expected_h):
        start = max(0, m.start() - 80)
        ctx = out[start : m.end() + 80]  # noqa: E203
        expected_frag = (
            f"\\newgeometry{{paperwidth={expected_w}, paperheight={expected_h}"
        )
        found_frag = out[m.start() : m.end()]  # noqa: E203
        diff = "\n".join(
            difflib.unified_diff(
                [expected_frag],
                [found_frag],
                fromfile="expected",
                tofile="found",
                lineterm="",
            )
        )
        pytest.fail(
            "Geometry values mismatch.\n"
            f"Expected: (w={expected_w}, h={expected_h})\n"
            f"Found:    (w={found_w}, h={found_h})\n"
            "--- Context ---\n"
            f"{ctx}\n"
            "--- Fragment diff ---\n"
            f"{diff}"
        )

    # Unerwünschte Landscape-Artefakte gesammelt melden
    bad_bits = []
    if ",landscape" in out:
        bad_bits.append("`,landscape` present")
    if "\\begin{landscape}" in out:
        bad_bits.append("`\\begin{landscape}` present")
    if bad_bits:
        pytest.fail("Unexpected landscape markers: " + ", ".join(bad_bits))

    # Erwartetes Restore (mit klarer Meldung)
    assert "\\restoregeometry" in out, "Missing \\restoregeometry"


# Test a real-world example from the documentation

DATA_DIR = Path(__file__).resolve().parent / "data"

TABLES = [
    (
        DATA_DIR / "evol00-decks-000-015-r-korr63-roehrenmodell-exakt-sli.md",
        297,  # a4 height
        210,  # a4 width
    ),
]


@pytest.mark.parametrize(
    "path_to_table,paperheight,paperwidth",
    TABLES,
    ids=[p[0].stem for p in TABLES],
)
def test_table_roehrenmodell(
    artifact_dir, path_to_table: Path, paperheight: int, paperwidth: int
):
    out = preprocess_md.process(path_to_table, paper_format="a4")

    # Artefakt ablegen (damit du im CI reingucken kannst)
    out_file = artifact_dir / f"{path_to_table.stem}.processed.md"
    out_file.write_text(out, encoding="utf-8")

    assert_geometry(out, expected_w=paperwidth, expected_h=paperheight)
