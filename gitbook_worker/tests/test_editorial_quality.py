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
    _check_pdf_script_samples,
    _check_pdf_text_overflow,
    analyze_pdf,
    analyze_table_reports,
    collect_editorial_metrics,
    format_console_summary,
    main as editorial_metrics_main,
    write_findings_csv,
    write_findings_sarif,
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


def test_markdown_metrics_reuses_existing_quality_signals(tmp_path: Path) -> None:
    _write_markdown(
        tmp_path / "source" / "chapter-a.md",
        """
        ---
        content_id: ch-a
        content_lang: ja
        doi: 10.1234/example
        ---
        # Shared Title
        TODO: verify this citation trail.
        """,
    )
    _write_markdown(
        tmp_path / "source" / "chapter-b.md",
        """
        ---
        content_id: ch-b
        content_lang: ja
        ---
        # Shared Title
        """,
    )

    report = collect_editorial_metrics(
        repo_root=tmp_path,
        profile=_multilingual_profile(),
        markdown_roots=(tmp_path,),
    )

    markdown_metrics = report["metrics"]["markdown"]
    rule_ids = {finding["rule_id"] for finding in report["findings"]}
    assert markdown_metrics["duplicate_headings_total"] == 1
    assert markdown_metrics["link_audit_todo_entries_total"] == 1
    assert markdown_metrics["inline_reference_tasks_total"] >= 1
    assert "markdown.heading.duplicate_title" in rule_ids
    assert "references.ai.tasks_detected" in rule_ids


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


def test_pdf_expected_page_rules_and_overflow_signals(tmp_path: Path) -> None:
    pdf = tmp_path / "blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=200)
    writer.add_metadata({"/Title": "Blank Sample"})
    with pdf.open("wb") as handle:
        writer.write(handle)
    profile = AcceptanceProfile(
        name="sample-pages",
        pdf=PdfProfile(
            expected_pages={
                "blank.pdf": (
                    {
                        "page": 1,
                        "label": "sample anchor",
                        "min_text_lines": 1,
                        "must_contain": "Sample Anchor",
                    },
                )
            },
            overflow_warn_pt=0.1,
            overflow_fail_pt=12.0,
            overflow_token_warn_chars=20,
        ),
    )

    metrics, findings = analyze_pdf(tmp_path, pdf, profile)
    overflow_findings = _check_pdf_text_overflow(
        "blank.pdf",
        {1: "https://example.test/" + "x" * 80},
        profile,
    )
    script_findings = _check_pdf_script_samples(
        "blank.pdf", {"cjk": 1, "hangul": 1, "kana": 0}, ()
    )

    assert metrics["metadata_title"] == "Blank Sample"
    assert any(finding.rule_id == "pdf.sample_page.low_text" for finding in findings)
    assert any(
        finding.rule_id == "pdf.sample_page.missing_text" for finding in findings
    )
    assert overflow_findings[0].rule_id == "pdf.layout.text_overflow"
    assert overflow_findings[0].severity == "fail"
    assert "overflow_mm=" in overflow_findings[0].evidence
    assert script_findings[0].rule_id == "pdf.text.script_sample"


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
        textwrap.dedent("""
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
            """).lstrip(),
        encoding="utf-8",
    )
    (tmp_path / "content.yaml").write_text(
        textwrap.dedent("""
            version: 1.0.0
            default: sample
            contents:
              - id: sample
                type: local
                uri: sample/
            """).lstrip(),
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


def test_publish_metadata_summary_order_and_release_docs_drift(
    tmp_path: Path,
) -> None:
    language_root = tmp_path / "sample"
    _write_markdown(
        language_root / "content" / "SUMMARY.md",
        """
        # Summary

        * [Appendix](appendix-a.md)
        * [Chapter](chapter.md)
        """,
    )
    _write_markdown(
        language_root / "content" / "appendix-a.md",
        """
        ---
        content_id: appendix-a
        content_lang: de
        version: 1.0.0
        ---
        # Appendix A
        """,
    )
    _write_markdown(
        language_root / "content" / "chapter.md",
        """
        ---
        content_id: chapter
        content_lang: de
        version: 1.0.0
        ---
        # Chapter
        """,
    )
    publish_dir = language_root / "publish"
    publish_dir.mkdir(parents=True)
    pdf = publish_dir / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=200)
    writer.add_metadata({"/Title": "PDF Title"})
    with pdf.open("wb") as handle:
        writer.write(handle)
    (language_root / "book.json").write_text(
        json.dumps({"root": "content/", "structure": {"summary": "SUMMARY.md"}}),
        encoding="utf-8",
    )
    (language_root / "publish.yml").write_text(
        textwrap.dedent("""
            version: 2.0.0
            title: Manifest Title
            language: en
            publish:
              - path: ./
                out_format: pdf
                out_dir: ./publish
                out: sample.pdf
                source_type: folder
                use_summary: true
                use_book_json: true
                build: true
                summary_appendices_last: true
            """).lstrip(),
        encoding="utf-8",
    )
    (tmp_path / "content.yaml").write_text(
        textwrap.dedent("""
            version: 1.0.0
            default: sample
            contents:
              - id: sample
                type: local
                uri: sample/
            """).lstrip(),
        encoding="utf-8",
    )
    _write_markdown(
        tmp_path / "docs" / "releases" / "v0.md",
        """
        # Release v0

        GitBook Worker 0.0.0
        sample pages: 99
        Layout findings: old
        """,
    )

    report = collect_editorial_metrics(
        repo_root=tmp_path,
        content_config=tmp_path / "content.yaml",
        languages=("sample",),
        profile=AcceptanceProfile(name="metadata-test"),
    )

    rule_ids = {finding["rule_id"] for finding in report["findings"]}
    assert "publish.summary.appendix_order" in rule_ids
    assert "metadata.version_mismatch" in rule_ids
    assert "metadata.title_mismatch" in rule_ids
    assert "metadata.language_mismatch" in rule_ids
    assert "release_docs.worker_version.stale" in rule_ids
    assert "release_docs.page_count.stale" in rule_ids
    assert report["metrics"]["release_docs"]["layout_claims_total"] == 1


def test_table_report_aggregation_flags_fallbacks(tmp_path: Path) -> None:
    report_path = tmp_path / "book.table-layout.jsonl"
    report_path.write_text(
        "\n".join(
            json.dumps(record)
            for record in (
                {
                    "source_path": "content/chapter.md",
                    "table_index": 2,
                    "heading": "Risk Matrix",
                    "selected_paper": "a3-landscape",
                    "method": "lowest-score-fallback",
                    "columns": 9,
                    "evaluations": [
                        {
                            "paper": "a4-portrait",
                            "acceptable": False,
                            "score": 32.5,
                            "unbreakable_overflow_mm": 18.2,
                            "max_cell_lines": 17,
                            "reasons": ["long-token"],
                        },
                        {
                            "paper": "a3-landscape",
                            "acceptable": False,
                            "score": 12.0,
                            "overflow_mm": 4.5,
                            "average_row_lines": 6.2,
                            "reasons": ["dense-table"],
                        },
                    ],
                },
                {
                    "source_path": "content/chapter.md",
                    "table_index": 3,
                    "heading": "Risk Matrix",
                    "selected_paper": "a4-landscape",
                    "method": "override",
                    "override": {
                        "paper": "a4-landscape",
                        "reason": "Editorial review keeps the table on one page.",
                    },
                },
                {
                    "source_path": "content/appendix.md",
                    "table_index": 1,
                    "heading": "Appendix Scores",
                    "selected_paper": "a4-landscape",
                    "method": "editorial-best-fit",
                    "evaluations": [
                        {
                            "paper": "a4-portrait",
                            "acceptable": False,
                            "score": 21.0,
                            "overflow_mm": 9.5,
                            "reasons": ["narrow-columns"],
                        },
                        {
                            "paper": "a4-landscape",
                            "acceptable": True,
                            "score": 3.0,
                            "max_cell_lines": 5,
                            "average_row_lines": 2.4,
                        },
                    ],
                },
            )
        )
        + "\n",
        encoding="utf-8",
    )

    metrics, findings = analyze_table_reports(tmp_path, (report_path,))

    assert metrics["decisions_total"] == 3
    assert metrics["method_counts"] == {
        "lowest-score-fallback": 1,
        "override": 1,
        "editorial-best-fit": 1,
    }
    assert metrics["problem_decisions_total"] == 3
    assert metrics["fallback_decisions_total"] == 1
    assert metrics["override_decisions_total"] == 1
    assert metrics["rejected_candidate_decisions_total"] == 2
    assert metrics["rejected_candidates_total"] == 3
    assert findings[0].rule_id == "tables.strategy.lowest-score-fallback"
    assert "content/chapter.md" in findings[0].location
    assert "table 2" in findings[0].location
    assert "rejected_candidates=2" in findings[0].evidence
    assert "override_reason" in findings[1].evidence
    assert findings[2].rule_id == "tables.strategy.rejected_candidates"
    assert findings[2].severity == "info"


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


def test_acceptance_passes_clean_sample() -> None:
    dossier, summary = editorial_acceptance.build_acceptance_dossier(
        [
            {
                "schema_version": "1.0.0",
                "generated_at": "2026-05-09T00:00:00+00:00",
                "project": "clean-sample",
                "worker_version": __version__,
                "summary": {"status": "passed"},
                "findings": [],
            }
        ],
        profile=AcceptanceProfile(name="clean-sample"),
    )

    assert summary["status"] == "passed"
    assert "No findings recorded." in dossier
    assert "Human Decision" in dossier


def test_editorial_quality_clis_expose_exit_code_help(capsys) -> None:
    assert editorial_metrics_main(["--help-exit-codes"]) == 0
    metrics_help = capsys.readouterr().out
    assert "45" in metrics_help
    assert "48" in metrics_help

    assert editorial_acceptance.main(["--help-exit-codes"]) == 0
    acceptance_help = capsys.readouterr().out
    assert "45" in acceptance_help
    assert "48" in acceptance_help


def test_metrics_writes_optional_csv_and_console_summary(tmp_path: Path) -> None:
    report = {
        "summary": {
            "status": "passed_with_warnings",
            "finding_counts": {"blocked": 0, "fail": 0, "warn": 1, "info": 0},
        },
        "findings": [
            {
                "id": "rule:1",
                "severity": "warn",
                "category": "markdown",
                "rule_id": "markdown.review_marker",
                "artifact": "chapter.md",
                "location": "line 1",
                "evidence": "TODO",
                "editorial_impact": "Review needed.",
                "healing": "Resolve note.",
            }
        ],
    }
    csv_path = tmp_path / "findings.csv"

    write_findings_csv(report, csv_path)

    assert "markdown.review_marker" in csv_path.read_text(encoding="utf-8")
    assert format_console_summary(report) == (
        "editorial_metrics status=passed_with_warnings blocked=0 fail=0 warn=1 info=0"
    )


def test_metrics_writes_sarif_with_source_locations(tmp_path: Path) -> None:
    report = {
        "findings": [
            {
                "id": "rule:1",
                "severity": "fail",
                "category": "markdown",
                "rule_id": "markdown.review_marker",
                "artifact": "content/chapter.md",
                "location": "line 12",
                "evidence": "TODO",
                "editorial_impact": "Review needed.",
                "healing": "Resolve note.",
            }
        ]
    }
    sarif_path = tmp_path / "findings.sarif"

    write_findings_sarif(report, sarif_path)

    sarif = json.loads(sarif_path.read_text(encoding="utf-8"))
    result = sarif["runs"][0]["results"][0]
    assert sarif["version"] == "2.1.0"
    assert result["level"] == "error"
    assert result["locations"][0]["physicalLocation"]["region"] == {"startLine": 12}


def test_acceptance_writes_html_trends_and_snapshot_index(tmp_path: Path) -> None:
    metrics_report = tmp_path / "metrics.json"
    metrics_report.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "generated_at": "2026-05-09T00:00:00+00:00",
                "project": "sample",
                "worker_version": __version__,
                "inputs": {"languages": ["en"]},
                "summary": {"status": "failed"},
                "metrics": {
                    "pdf": [
                        {
                            "path": "publish/sample.pdf",
                            "pages_total": 3,
                            "file_size_bytes": 42,
                            "modified_at": "2026-05-09T00:00:00+00:00",
                        }
                    ]
                },
                "findings": [
                    {
                        "id": "pdf:1",
                        "severity": "fail",
                        "category": "pdf.text",
                        "rule_id": "pdf.text.empty_page",
                        "artifact": "publish/sample.pdf",
                        "location": "page 2",
                        "evidence": "empty text layer",
                        "editorial_impact": "Search and copy are unreliable.",
                        "healing": "Rebuild PDF with text layer.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    dossier = tmp_path / "acceptance.md"
    html_report = tmp_path / "acceptance.html"
    trends = tmp_path / "trends.jsonl"
    snapshots = tmp_path / "snapshots"

    exit_code = editorial_acceptance.main(
        [
            str(metrics_report),
            "--output",
            str(dossier),
            "--html-output",
            str(html_report),
            "--trend-output",
            str(trends),
            "--snapshot-dir",
            str(snapshots),
            "--snapshot-renderer",
            "none",
        ]
    )

    assert exit_code == EDITORIAL_HARD_FINDINGS_EXIT_CODE
    assert "Editorial Acceptance" in html_report.read_text(encoding="utf-8")
    trend_record = json.loads(trends.read_text(encoding="utf-8"))
    assert trend_record["status"] == "failed"
    assert trend_record["pages_total"] == 3
    snapshot_index = (snapshots / "index.html").read_text(encoding="utf-8")
    assert "publish/sample.pdf page 2" in snapshot_index


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


def test_builtin_local_release_and_customer_handover_profiles_load() -> None:
    local = load_acceptance_profile(profile_name="local")
    release = load_acceptance_profile(profile_name="release")
    handover = load_acceptance_profile(profile_name="customer-handover")

    assert local.fail_on_warnings is False
    assert release.documentation.fail_on_stale_worker_version is True
    assert handover.fail_on_warnings is True
