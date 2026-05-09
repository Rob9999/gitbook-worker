from __future__ import annotations

import json
import textwrap
from pathlib import Path

from pypdf import PdfWriter

from gitbook_worker.tools.quality import editorial_acceptance
from gitbook_worker.tools.quality.editorial_common import (
    EDITORIAL_HARD_FINDINGS_EXIT_CODE,
    AcceptanceProfile,
    MarkdownProfile,
    PdfProfile,
    load_acceptance_profile,
    stable_finding_id,
)
from gitbook_worker.tools.quality.editorial_metrics import (
    analyze_pdf,
    analyze_table_reports,
    collect_editorial_metrics,
)


def _write_markdown(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")


def _multilingual_profile() -> AcceptanceProfile:
    return AcceptanceProfile(
        name="test-multilingual",
        markdown=MarkdownProfile(
            source_locale="ja",
            target_locales=("pl",),
            forbidden_frontmatter_keys=("lang",),
            required_frontmatter_by_role={
                "source": ("content_id", "content_lang"),
                "target": ("content_id", "content_lang", "source", "status"),
            },
        ),
        pdf=PdfProfile(),
    )


def test_stable_finding_id_is_deterministic() -> None:
    first = stable_finding_id("rule", "a/b.md", "line 3", "Some Evidence")
    second = stable_finding_id("rule", "a/b.md", "line 3", "some   evidence")

    assert first == second
    assert first.startswith("rule:")


def test_markdown_metrics_detect_generic_target_frontmatter_rules(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source" / "chapter.md"
    target = tmp_path / "target-pl" / "chapter.md"
    _write_markdown(
        source,
        """
        ---
        content_id: ch-1
        content_lang: ja
        ---
        # Source
        """,
    )
    _write_markdown(
        target,
        """
        ---
        content_id: ch-1
        content_lang: pl
        lang: pl
        ---
        # Target
        TODO: review this translation
        """,
    )

    report = collect_editorial_metrics(
        repo_root=tmp_path,
        profile=_multilingual_profile(),
        markdown_roots=(tmp_path,),
    )

    rule_ids = {finding["rule_id"] for finding in report["findings"]}
    assert "markdown.frontmatter.required_missing" in rule_ids
    assert "markdown.frontmatter.forbidden_key" in rule_ids
    assert "markdown.review_marker" in rule_ids
    assert report["metrics"]["markdown"]["by_locale"] == {"ja": 1, "pl": 1}


def test_markdown_metrics_detect_translation_content_id_mismatch(
    tmp_path: Path,
) -> None:
    _write_markdown(
        tmp_path / "source" / "chapter.md",
        """
        ---
        content_id: ch-source
        content_lang: ja
        ---
        # Source
        """,
    )
    _write_markdown(
        tmp_path / "target-pl" / "chapter.md",
        """
        ---
        content_id: ch-target
        content_lang: pl
        source: source/chapter.md
        status: approved
        ---
        # Target
        """,
    )

    report = collect_editorial_metrics(
        repo_root=tmp_path,
        profile=_multilingual_profile(),
        markdown_roots=(tmp_path,),
    )

    rule_ids = {finding["rule_id"] for finding in report["findings"]}
    assert "markdown.translation.content_id_mismatch" in rule_ids
    assert report["metrics"]["markdown"]["approved_targets_total"] == 1


def test_pdf_metrics_detect_empty_text_layer(tmp_path: Path) -> None:
    pdf = tmp_path / "blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=200)
    with pdf.open("wb") as handle:
        writer.write(handle)

    metrics, findings = analyze_pdf(tmp_path, pdf, _multilingual_profile())

    assert metrics["pages_total"] == 1
    assert metrics["orientations"] == {"landscape": 1}
    assert metrics["empty_text_pages"] == 1
    assert any(finding.rule_id == "pdf.text.empty_document" for finding in findings)


def test_table_report_aggregation_flags_fallbacks(tmp_path: Path) -> None:
    report_path = tmp_path / "book.table-layout.jsonl"
    report_path.write_text(
        json.dumps(
            {
                "selected_paper": "a3-landscape",
                "method": "lowest-score-fallback",
                "columns": 9,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    metrics, findings = analyze_table_reports(tmp_path, (report_path,))

    assert metrics["decisions_total"] == 1
    assert metrics["method_counts"] == {"lowest-score-fallback": 1}
    assert findings[0].rule_id == "tables.strategy.lowest-score-fallback"


def test_acceptance_writes_dossier_and_returns_failure(tmp_path: Path) -> None:
    metrics_report = tmp_path / "metrics.json"
    metrics_report.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "generated_at": "2026-05-09T00:00:00+00:00",
                "project": "sample",
                "summary": {"status": "failed"},
                "findings": [
                    {
                        "id": "rule:123",
                        "severity": "fail",
                        "category": "markdown.frontmatter",
                        "rule_id": "markdown.frontmatter.required_missing",
                        "artifact": "target-pl/chapter.md",
                        "location": "frontmatter.source",
                        "evidence": "missing source",
                        "editorial_impact": "Translation cannot be audited.",
                        "healing": "Add source.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    dossier = tmp_path / "dossier.md"

    exit_code = editorial_acceptance.main(
        [str(metrics_report), "--output", str(dossier)]
    )

    assert exit_code == EDITORIAL_HARD_FINDINGS_EXIT_CODE
    text = dossier.read_text(encoding="utf-8")
    assert "Editorial Acceptance Dossier" in text
    assert "Human Decision" in text
    assert "missing source" in text


def test_builtin_multilingual_profile_loads() -> None:
    profile = load_acceptance_profile(profile_name="multilingual-release-candidate")

    assert profile.markdown.source_locale == "ja"
    assert profile.markdown.target_locales == ("pl", "hr", "no")
    assert "ProjectCJK-Regular" in profile.pdf.required_fonts
