from __future__ import annotations

import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfWriter

from gitbook_worker import __version__
from gitbook_worker.tools.quality import editorial_acceptance
from gitbook_worker.tools.quality.editorial_common import (
    EDITORIAL_HARD_FINDINGS_EXIT_CODE,
    AcceptanceProfile,
    DocumentationProfile,
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
    assert metrics["low_text_reason_hints"] == [
        {"page": 1, "lines": 0, "reason": "empty"}
    ]
    assert any(finding.rule_id == "pdf.text.empty_document" for finding in findings)


def test_pdf_targets_flag_page_count_outside_corridor(tmp_path: Path) -> None:
    pdf = tmp_path / "blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=200)
    with pdf.open("wb") as handle:
        writer.write(handle)
    profile = AcceptanceProfile(
        name="page-target-test",
        pdf=PdfProfile(
            pdf_targets={"blank.pdf": {"target_pages_min": 2, "target_pages_max": 4}}
        ),
    )

    _, findings = analyze_pdf(tmp_path, pdf, profile)

    assert any(finding.rule_id == "pdf.pages.below_target" for finding in findings)


def test_publish_scope_uses_summary_and_blocks_missing_pdf(tmp_path: Path) -> None:
    language_root = tmp_path / "sample"
    _write_markdown(
        language_root / "content" / "SUMMARY.md",
        """
        # Summary

        * [Chapter](chapter.md)
        """,
    )
    _write_markdown(language_root / "content" / "chapter.md", "# Chapter\n")
    _write_markdown(language_root / "content" / "orphan.md", "# Orphan\n")
    (language_root / "book.json").write_text(
        json.dumps(
            {
                "root": "content/",
                "structure": {"summary": "SUMMARY.md"},
            }
        ),
        encoding="utf-8",
    )
    (language_root / "publish.yml").write_text(
        textwrap.dedent(
            """
            version: 0.1.3
            publish:
              - path: ./
                out_format: pdf
                out_dir: ./publish
                out: sample.pdf
                source_type: folder
                use_summary: true
                use_book_json: true
                build: true
                pdf_options:
                  table_paper_strategy:
                    report: jsonl
            """
        ).lstrip(),
        encoding="utf-8",
    )
    (tmp_path / "content.yaml").write_text(
        textwrap.dedent(
            """
            version: 1.0.0
            default: sample
            contents:
              - id: sample
                type: local
                uri: sample/
            """
        ).lstrip(),
        encoding="utf-8",
    )

    report = collect_editorial_metrics(
        repo_root=tmp_path,
        content_config=tmp_path / "content.yaml",
        languages=("sample",),
        profile=AcceptanceProfile(name="publish-scope-test"),
    )

    publish_metrics = report["metrics"]["publish_scope"]
    rule_ids = {finding["rule_id"] for finding in report["findings"]}
    assert publish_metrics["build_entries_total"] == 1
    assert publish_metrics["published_markdown_files_total"] == 1
    assert publish_metrics["orphaned_markdown_files_total"] == 1
    assert publish_metrics["missing_expected_pdfs_total"] == 1
    assert "publish.pdf.missing_artifact" in rule_ids
    assert "publish.summary.orphaned_markdown" in rule_ids


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


def test_acceptance_derives_stale_report_findings(tmp_path: Path) -> None:
    old_report_time = "2026-05-09T10:00:00+00:00"
    newer_artifact_time = "2026-05-09T10:30:00+00:00"
    dossier, summary = editorial_acceptance.build_acceptance_dossier(
        [
            {
                "schema_version": "1.0.0",
                "generated_at": old_report_time,
                "project": "sample",
                "worker_version": "0.0.0",
                "metrics": {
                    "pdf": [
                        {
                            "path": "publish/sample.pdf",
                            "pages_total": 10,
                            "file_size_bytes": 100,
                            "creation_date": None,
                            "modified_at": newer_artifact_time,
                        }
                    ]
                },
                "findings": [],
            }
        ],
        profile=AcceptanceProfile(
            name="stale-test",
            documentation=DocumentationProfile(
                fail_on_stale_worker_version=True,
                fail_on_stale_page_count=True,
            ),
        ),
    )

    assert summary["status"] == "failed"
    assert "report.worker_version.stale" in dossier
    assert "report.artifact.stale" in dossier
    assert "PDF Artifacts" in dossier


def test_acceptance_compares_baseline_and_marks_residual_risks() -> None:
    baseline_report = {
        "findings": [
            {
                "id": "existing-id",
                "severity": "warn",
                "rule_id": "markdown.long_token",
                "artifact": "chapter.md",
                "location": "line 3",
                "evidence": "same evidence",
            },
            {
                "id": "changed-old-id",
                "severity": "warn",
                "rule_id": "pdf.toc.missing",
                "artifact": "book.pdf",
                "location": "outline",
                "evidence": "old evidence",
            },
            {
                "id": "resolved-id",
                "severity": "warn",
                "rule_id": "markdown.review_marker",
                "artifact": "old.md",
                "location": "line 1",
                "evidence": "resolved",
            },
        ]
    }
    current_report = {
        "schema_version": "1.0.0",
        "generated_at": "2026-05-09T00:00:00+00:00",
        "project": "sample",
        "worker_version": __version__,
        "findings": [
            {
                "id": "existing-id",
                "severity": "warn",
                "category": "markdown.layout",
                "rule_id": "markdown.long_token",
                "artifact": "chapter.md",
                "location": "line 3",
                "evidence": "same evidence",
                "editorial_impact": "Layout risk.",
                "healing": "Wrap token.",
            },
            {
                "id": "changed-new-id",
                "severity": "warn",
                "category": "pdf.toc",
                "rule_id": "pdf.toc.missing",
                "artifact": "book.pdf",
                "location": "outline",
                "evidence": "new evidence",
                "editorial_impact": "Navigation risk.",
                "healing": "Regenerate TOC.",
            },
            {
                "id": "new-id",
                "severity": "warn",
                "category": "tables.strategy",
                "rule_id": "tables.strategy.lowest-score-fallback",
                "artifact": "book.table-layout.jsonl",
                "location": "line 1",
                "evidence": "fallback",
                "editorial_impact": "Layout trade-off.",
                "healing": "Review table.",
            },
        ],
    }
    accepted_findings = [
        {
            "finding_id": "new-id",
            "reason": "Known table trade-off for release candidate.",
            "role": "editor",
            "date": "2026-05-09",
            "expires": "2099-01-01",
            "release": "v2.9.0",
        },
        {
            "finding_id": "existing-id",
            "reason": "Old acceptance must be renewed.",
            "role": "editor",
            "date": "2026-01-01",
            "expires": "2000-01-01",
        },
        {
            "finding_id": "unused-id",
            "reason": "No longer present.",
            "role": "editor",
            "date": "2026-05-09",
            "expires": "2099-01-01",
        },
    ]

    dossier, summary = editorial_acceptance.build_acceptance_dossier(
        [current_report],
        profile=AcceptanceProfile(name="baseline-test"),
        baseline_report=baseline_report,
        accepted_findings=accepted_findings,
    )

    assert summary["baseline"]["new"] == 1
    assert summary["baseline"]["existing"] == 1
    assert summary["baseline"]["changed"] == 1
    assert summary["baseline"]["resolved"] == 1
    assert summary["accepted_findings"]["matched"] == 2
    assert summary["accepted_findings"]["active"] == 1
    assert summary["accepted_findings"]["expired"] == 1
    assert summary["accepted_findings"]["unused"] == 1
    assert summary["status"] == "failed"
    assert "Baseline Comparison" in dossier
    assert "Accepted Residual Risks" in dossier
    assert "Baseline: `changed`" in dossier
    assert "acceptance.residual_risk.expired" in dossier


def test_builtin_multilingual_profile_loads() -> None:
    profile = load_acceptance_profile(profile_name="multilingual-release-candidate")

    assert profile.markdown.source_locale == "ja"
    assert profile.markdown.target_locales == ("pl", "hr", "no")
    assert "ProjectCJK-Regular" in profile.pdf.required_fonts
