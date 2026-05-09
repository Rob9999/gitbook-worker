import difflib
import json
import re
from pathlib import Path

import pytest
from gitbook_worker.tools.publishing import preprocess_md


def _wide_table(tmp_path, cols: int):
    md = tmp_path / "table.md"
    header = "|" + "|".join([f"c{i}" for i in range(cols)]) + "|"
    sep = "|" + "|".join(["---"] * cols) + "|"
    row = "|" + "|".join(["1"] * cols) + "|"
    content = "\n".join(["#### Heading", "", "> note", header, sep, row])
    md.write_text(content, encoding="utf-8")
    return md


def _wide_content_table(tmp_path):
    md = tmp_path / "wide-content-table.md"
    content = "\n".join(
        [
            "#### Wide content table",
            "",
            "| Entity | Code | Stability | Charter status | Entry conditions | "
            "Cooperation | Partnership level | Core potential | Comment |",
            "|---|---|---|---|---|---|---|---|---|",
            "| Region Alpha-Verbund | REG-A1 | stabil-hoch | verfassungsklar "
            "mit nachweisbarer Kontrollkette | Auditierte Aufnahmebedingungen "
            "und abgestimmte Schutzklauseln | technische Kooperation, "
            "Datenraum, Krisenuebung | assoziierte Partnerschaft | "
            "mittelfristig plausibel | Anonymisierter Kommentar mit langer "
            "fachlicher Begruendung |",
        ]
    )
    md.write_text(content, encoding="utf-8")
    return md


def _cjk_content_table(tmp_path):
    md = tmp_path / "cjk-content-table.md"
    cjk_sequence = "生命共同体治理结构连续性评估" * 8
    content = "\n".join(
        [
            "#### CJK content table",
            "",
            "| Area | Script signal | Editorial comment |",
            "|---|---|---|",
            f"| Region Delta | {cjk_sequence} | Long script run without spaces "
            "must be treated as a layout risk beyond German compounds |",
        ]
    )
    md.write_text(content, encoding="utf-8")
    return md


def _english_wide_decision_table(tmp_path):
    md = tmp_path / "english-wide-decision-table.md"
    content = "\n".join(
        [
            "### Wide Decision Table (Anonymized)",
            "",
            "| Area | Code | Governance grade | Charter status | Entry conditions | Cooperation | Partnership level | Core-group potential | Comment |",
            "|---|---|---|---|---|---|---|---|---|",
            "| Area Alpha Network | A-A1 | high stable | charter frame reviewed, control path documented | Entry conditions with audit path, privacy impact review, and aligned safeguard clause | Professional cooperation, data room, crisis exercise | Associated with expansion path | plausible in the medium term | Anonymized long note with rationale, risk marker, and open review task |",
            "| Area Beta Corridor | A-B2 | moderately stable | transition status with external quality assurance | Integration only after evidence of reliable operating processes and consistent reporting duties | Pilot cooperation, training, shared situation report | Observing partnership | depends on follow-up review | Anonymized assessment with intentionally long text width for PDF table stress |",
            "| Area Gamma Mesh | A-C3 | uneven | charter comparison started, decision open | Preconditions: clarify responsibilities, finish data classification, confirm audit window | Expert dialogue and technical inventory | Preparatory cooperation | not currently robust | Neutral sample row without customer names, original places, or political classification |",
        ]
    )
    md.write_text(content, encoding="utf-8")
    return md


def test_relative_markdown_links_point_to_pdf_anchor(tmp_path):
    content_root = tmp_path / "content"
    chapter = content_root / "chapters" / "chapter-01.md"
    chapter.parent.mkdir(parents=True)
    chapter.write_text("# Kapitel 1\n", encoding="utf-8")

    index = content_root / "index.md"
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(
        """
[Kapitel 1](./chapters/chapter-01.md)
[Detailabschnitt](./chapters/chapter-01.md#teil-1)
![Symbol](./chapters/chapter-01.md)
""".strip(),
        encoding="utf-8",
    )

    out = preprocess_md.process(str(index), paper_format="a4")

    assert "](#md-chapters-chapter-01)" in out
    assert "](#teil-1)" in out
    assert "![Symbol](./chapters/chapter-01.md)" in out
    assert '<a id="md-index"></a>' in out


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
    assert (
        '![Beispiel Caption](.gitbook/assets/example.png){fig-alt="Sample Alt"}' in out
    )


def test_table_wrapped_portrait(artifact_dir):
    md = _wide_table(artifact_dir, cols=15)
    out = preprocess_md.process(str(md), paper_format="a4")
    assert_geometry(out, expected_w=420, expected_h=297)


def test_table_wrapped_landscape_enabled(artifact_dir):
    md = _wide_table(artifact_dir, cols=11)
    out = preprocess_md.process(str(md), paper_format="a4")
    assert_geometry(out, expected_w=297, expected_h=210)


def test_table_width_uses_usable_text_area() -> None:
    a4_landscape = preprocess_md.get_valid_paper_measurements("a4-landscape")
    required_width = preprocess_md.available_text_width_mm(a4_landscape) + 1

    info = preprocess_md.paper_for_table_width(
        required_width,
        base_paper=preprocess_md.get_valid_paper_measurements("a4"),
    )

    assert info.size_mm == (420, 297)


def test_table_with_long_cells_uses_content_width(artifact_dir):
    md = _wide_content_table(artifact_dir)
    out = preprocess_md.process(str(md), paper_format="a4")

    m = GEOM_RE.search(out)
    assert m, "Expected long-cell table to switch geometry"
    assert int(m["w"]) > 297


def test_table_strategy_scores_cjk_long_sequences(artifact_dir):
    md = _cjk_content_table(artifact_dir)
    out = preprocess_md.process(
        str(md),
        paper_format="a4",
        table_strategy={"max_cell_lines": 2, "max_header_lines": 2},
    )

    assert_geometry(out, expected_w=420, expected_h=297)


def test_table_strategy_adds_script_break_hints(artifact_dir):
    md = _cjk_content_table(artifact_dir)
    out = preprocess_md.process(str(md), paper_format="a4")

    assert r"\allowbreak{}" in out
    assert "生命\\allowbreak{}共同" in out


def test_table_strategy_override_comment_forces_paper(artifact_dir):
    md = artifact_dir / "override-table.md"
    md.write_text(
        "\n".join(
            [
                "#### Override table",
                "",
                '<!-- gbw-table paper=a2-landscape reason="reviewed special table" -->',
                "| A | B |",
                "|---|---|",
                "| 1 | 2 |",
            ]
        ),
        encoding="utf-8",
    )

    out = preprocess_md.process(str(md), paper_format="a4")

    assert_geometry(out, expected_w=594, expected_h=420)


def test_table_strategy_custom_candidate_and_report(artifact_dir):
    md = _wide_content_table(artifact_dir)
    report_path = artifact_dir / "table-layout.jsonl"
    if report_path.exists():
        report_path.unlink()
    out = preprocess_md.process(
        str(md),
        paper_format="a4",
        table_strategy={
            "report_path": str(report_path),
            "candidates": [
                "a4",
                "a4-landscape",
                {
                    "name": "customer-wide",
                    "standard": False,
                    "size_mm": [700, 420],
                    "margins_mm": [15, 15, 15, 15],
                },
            ],
        },
    )

    assert "paperwidth=700mm" in out
    report = json.loads(report_path.read_text(encoding="utf-8").splitlines()[-1])
    assert report["selected_paper"] == "customer-wide"
    assert report["evaluations"]


def test_table_strategy_uses_wrapping_latex_columns(artifact_dir):
    md = _english_wide_decision_table(artifact_dir)
    out = preprocess_md.process(str(md), paper_format="a4")

    assert_geometry(out, expected_w=594, expected_h=420)
    assert r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{" in out
    assert "lllllllll" not in out


def test_svg_skips_size_probe(monkeypatch, tmp_path):
    svg = tmp_path / "img.svg"
    svg.write_text("<svg width='10' height='10'></svg>", encoding="utf-8")

    md = tmp_path / "note.md"
    md.write_text(f"![Alt]({svg.name})\n", encoding="utf-8")

    calls: list[Path] = []

    def fake_get_image_width(path: Path) -> int:
        calls.append(path)
        return 0

    monkeypatch.setattr(preprocess_md, "get_image_width", fake_get_image_width)

    out = preprocess_md.process(str(md), paper_format="a4")

    assert "img.svg" in out
    assert calls and calls[0].name == "img.svg"


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
