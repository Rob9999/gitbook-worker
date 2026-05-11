"""Collect editorial Markdown, PDF, and table-layout quality metrics."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import unquote

import yaml
from pypdf import PdfReader

from gitbook_worker import __version__
from gitbook_worker.core.application.pdf_toc import extract_pdf_toc
from gitbook_worker.tools.exit_codes import add_exit_code_help, handle_exit_code_help
from gitbook_worker.tools.logging_config import get_logger
from gitbook_worker.tools.publishing.gitbook_style import get_summary_layout
from gitbook_worker.tools.quality.ai_references import (
    load_inline_reference_tasks,
    load_reference_tasks,
)
from gitbook_worker.tools.quality.editorial_common import (
    EDITORIAL_BLOCKED_EXIT_CODE,
    EDITORIAL_HARD_FINDINGS_EXIT_CODE,
    EDITORIAL_INVALID_PROFILE_EXIT_CODE,
    AcceptanceProfile,
    Finding,
    build_report,
    load_acceptance_profile,
    make_finding,
    relative_artifact,
    write_json_report,
)
from gitbook_worker.tools.quality.link_audit import DuplicateHeading, list_todos
from gitbook_worker.tools.testing.pdf_validator import (
    extract_pdf_fonts,
    font_name_matches,
    scan_forbidden_log_patterns,
)
from gitbook_worker.tools.utils.smart_content import load_content_config
from gitbook_worker.tools.validators.frontmatter_checker import (
    check_file as check_frontmatter_file,
)

logger = get_logger(__name__)


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
_TODO_RE = re.compile(
    r"\b(TODO|FIXME|XXX)\b|\bREVIEW\b\s*:|\[REVIEW\]|<!--\s*REVIEW",
    re.IGNORECASE,
)
_TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
_FOOTER_LINE_RE = re.compile(r"^\s*(?:page\s*)?\d+\s*$", re.IGNORECASE)
_SUMMARY_LINK_RE = re.compile(
    r"\(([^)]+?\.(?:md|markdown))(?:#[^)]+)?\)", re.IGNORECASE
)
_PDF_REPORT_MODES = {"jsonl", "file", "true"}


def collect_editorial_metrics(
    *,
    repo_root: Path,
    project: str | None = None,
    profile: AcceptanceProfile | None = None,
    content_config: Path | None = None,
    languages: Sequence[str] | None = None,
    markdown_roots: Sequence[Path] | None = None,
    pdf_paths: Sequence[Path] | None = None,
    table_report_paths: Sequence[Path] | None = None,
    log_paths: Sequence[Path] | None = None,
    discover_table_reports: bool = False,
) -> dict[str, Any]:
    """Collect metrics and return the canonical editorial metrics report."""

    root = repo_root.resolve()
    active_profile = profile or load_acceptance_profile()
    publish_scope = discover_publish_scope(
        root,
        content_config=content_config,
        languages=languages,
        profile=active_profile,
        enabled=markdown_roots is None,
    )
    if markdown_roots is None and publish_scope["markdown_files"]:
        markdown_files = list(publish_scope["markdown_files"])
        markdown_inputs = list(publish_scope["markdown_inputs"])
    else:
        markdown_files, markdown_inputs = discover_markdown_files(
            root,
            content_config=content_config,
            languages=languages,
            markdown_roots=markdown_roots,
            profile=active_profile,
        )
    markdown_metrics, markdown_findings = analyze_markdown_files(
        root, markdown_files, active_profile
    )

    pdf_metrics: list[dict[str, Any]] = []
    pdf_findings: list[Finding] = []
    pdf_inputs = _dedupe_paths([*(pdf_paths or ()), *publish_scope["expected_pdfs"]])
    for pdf_path in pdf_inputs:
        metrics, findings = analyze_pdf(root, pdf_path, active_profile, log_paths or ())
        pdf_metrics.append(metrics)
        pdf_findings.extend(findings)

    table_paths = list(table_report_paths or ())
    if discover_table_reports:
        table_paths.extend(discover_table_layout_reports(root, markdown_inputs))
    table_paths.extend(publish_scope["expected_table_reports"])
    table_paths = _dedupe_paths(table_paths)
    table_artifact_links = _table_report_artifact_links(
        publish_scope["metrics"].get("entries", [])
    )
    table_metrics, table_findings = analyze_table_reports(
        root, table_paths, artifact_links=table_artifact_links
    )

    toc_findings = compare_markdown_pdf_toc(root, markdown_metrics, pdf_metrics)
    metadata_findings = compare_publish_metadata(
        publish_scope["metrics"], markdown_metrics, pdf_metrics
    )
    release_doc_metrics, release_doc_findings = analyze_release_documentation(
        root, active_profile, pdf_metrics
    )
    findings = [
        *publish_scope["findings"],
        *markdown_findings,
        *pdf_findings,
        *toc_findings,
        *table_findings,
        *metadata_findings,
        *release_doc_findings,
    ]
    inputs = {
        "repo_root": ".",
        "content_config": (
            relative_artifact(content_config, root) if content_config else None
        ),
        "languages": list(languages or []),
        "markdown_roots": markdown_inputs,
        "pdfs": [relative_artifact(path, root) for path in pdf_inputs],
        "table_reports": [relative_artifact(path, root) for path in table_paths],
        "logs": [relative_artifact(path, root) for path in log_paths or ()],
        "network": active_profile.network,
    }
    metrics = {
        "publish_scope": publish_scope["metrics"],
        "markdown": markdown_metrics,
        "pdf": pdf_metrics,
        "tables": table_metrics,
        "release_docs": release_doc_metrics,
    }
    return build_report(
        project=project or root.name,
        inputs=inputs,
        metrics=metrics,
        findings=findings,
        profile=active_profile,
    )


def discover_markdown_files(
    repo_root: Path,
    *,
    content_config: Path | None,
    languages: Sequence[str] | None,
    markdown_roots: Sequence[Path] | None,
    profile: AcceptanceProfile,
) -> tuple[list[Path], list[str]]:
    """Discover Markdown files from explicit roots or content.yaml."""

    roots: list[Path] = []
    if markdown_roots:
        roots.extend(_resolve_path(repo_root, root) for root in markdown_roots)
    else:
        try:
            config = load_content_config(
                content_config,
                cwd=repo_root,
                repo_root=repo_root,
                allow_missing=True,
            )
            target_languages = list(languages or config.entries.keys())
            for language_id in target_languages:
                entry = config.get(language_id)
                if not entry.is_local:
                    continue
                if entry.raw and entry.raw.get("build") is False:
                    continue
                language_root = entry.resolve_path(repo_root)
                content_root = language_root / "content"
                roots.append(content_root if content_root.is_dir() else language_root)
        except Exception as exc:  # noqa: BLE001 - metrics report should stay usable
            logger.warning("Could not resolve content config: %s", exc)
            roots.append(repo_root)

    files: list[Path] = []
    seen: set[Path] = set()
    exclude_dirs = set(profile.markdown.exclude_dirs)
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.md")):
            if not path.is_file():
                continue
            rel_parts = path.resolve().relative_to(root.resolve()).parts
            if any(part in exclude_dirs for part in rel_parts):
                continue
            if path.resolve() not in seen:
                seen.add(path.resolve())
                files.append(path)
    return files, [relative_artifact(root, repo_root) for root in roots]


def discover_publish_scope(
    repo_root: Path,
    *,
    content_config: Path | None,
    languages: Sequence[str] | None,
    profile: AcceptanceProfile,
    enabled: bool = True,
) -> dict[str, Any]:
    """Discover publish.yml scope, expected artifacts and scoped Markdown files."""

    metrics: dict[str, Any] = {
        "enabled": enabled,
        "content_entries_total": 0,
        "local_content_entries_total": 0,
        "skipped_content_entries_total": 0,
        "manifests_total": 0,
        "missing_manifests_total": 0,
        "publish_entries_total": 0,
        "build_entries_total": 0,
        "skipped_publish_entries_total": 0,
        "published_markdown_files_total": 0,
        "unpublished_markdown_files_total": 0,
        "orphaned_markdown_files_total": 0,
        "expected_pdfs_total": 0,
        "missing_expected_pdfs_total": 0,
        "expected_table_reports_total": 0,
        "missing_expected_table_reports_total": 0,
        "entries": [],
    }
    findings: list[Finding] = []
    markdown_files: list[Path] = []
    markdown_inputs: list[str] = []
    expected_pdfs: list[Path] = []
    expected_table_reports: list[Path] = []

    if not enabled:
        return {
            "metrics": metrics,
            "findings": findings,
            "markdown_files": markdown_files,
            "markdown_inputs": markdown_inputs,
            "expected_pdfs": expected_pdfs,
            "expected_table_reports": expected_table_reports,
        }

    try:
        config = load_content_config(
            content_config,
            cwd=repo_root,
            repo_root=repo_root,
            allow_missing=True,
        )
    except Exception as exc:  # noqa: BLE001 - metrics should remain readable
        logger.warning("Could not resolve content config for publish scope: %s", exc)
        return {
            "metrics": metrics,
            "findings": findings,
            "markdown_files": markdown_files,
            "markdown_inputs": markdown_inputs,
            "expected_pdfs": expected_pdfs,
            "expected_table_reports": expected_table_reports,
        }

    target_languages = list(languages or config.entries.keys())
    seen_markdown: set[Path] = set()
    for language_id in target_languages:
        try:
            entry = config.get(language_id)
        except KeyError as exc:
            findings.append(
                make_finding(
                    rule_id="publish.content_entry.missing",
                    severity="warn",
                    category="publish.scope",
                    artifact=relative_artifact(
                        config.source_path or repo_root, repo_root
                    ),
                    location=str(language_id),
                    evidence=str(exc),
                    editorial_impact="Angeforderter Content-Scope ist nicht in content.yaml definiert.",
                    healing="--lang korrigieren oder content.yaml ergaenzen.",
                )
            )
            continue
        metrics["content_entries_total"] += 1
        if not entry.is_local:
            metrics["skipped_content_entries_total"] += 1
            continue
        if entry.raw and _as_bool(entry.raw.get("build"), default=True) is False:
            metrics["skipped_content_entries_total"] += 1
            continue

        metrics["local_content_entries_total"] += 1
        language_root = entry.resolve_path(repo_root)
        manifest = language_root / "publish.yml"
        if not manifest.exists():
            metrics["missing_manifests_total"] += 1
            continue
        metrics["manifests_total"] += 1
        try:
            raw_manifest = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError) as exc:
            findings.append(
                make_finding(
                    rule_id="publish.manifest.read_error",
                    severity="blocked",
                    category="publish.scope",
                    artifact=relative_artifact(manifest, repo_root),
                    location="file",
                    evidence=str(exc),
                    editorial_impact="publish.yml kann nicht fuer den Abnahmescope gelesen werden.",
                    healing="YAML-Syntax oder Dateizugriff korrigieren.",
                )
            )
            continue
        publish_entries = raw_manifest.get("publish")
        if not isinstance(publish_entries, list):
            continue

        for index, raw_entry in enumerate(publish_entries, start=1):
            if not isinstance(raw_entry, Mapping):
                continue
            metrics["publish_entries_total"] += 1
            if not _as_bool(raw_entry.get("build"), default=False):
                metrics["skipped_publish_entries_total"] += 1
                continue
            metrics["build_entries_total"] += 1
            entry_metrics, entry_findings = _analyze_publish_entry(
                repo_root,
                manifest,
                raw_manifest,
                index,
                raw_entry,
                profile,
            )
            metrics["entries"].append(entry_metrics)
            findings.extend(entry_findings)
            for key in (
                "published_markdown_files_total",
                "unpublished_markdown_files_total",
                "orphaned_markdown_files_total",
                "expected_pdfs_total",
                "missing_expected_pdfs_total",
                "expected_table_reports_total",
                "missing_expected_table_reports_total",
            ):
                metrics[key] += int(entry_metrics.get(key, 0))
            for markdown_file in entry_metrics.get("published_markdown_files", []):
                path = (repo_root / markdown_file).resolve()
                if path not in seen_markdown:
                    seen_markdown.add(path)
                    markdown_files.append(path)
            source_root = entry_metrics.get("source_root")
            if source_root and source_root not in markdown_inputs:
                markdown_inputs.append(str(source_root))
            if entry_metrics.get("expected_pdf"):
                expected_pdfs.append(
                    (repo_root / entry_metrics["expected_pdf"]).resolve()
                )
            if entry_metrics.get("expected_table_report"):
                expected_table_reports.append(
                    (repo_root / entry_metrics["expected_table_report"]).resolve()
                )

    return {
        "metrics": metrics,
        "findings": findings,
        "markdown_files": markdown_files,
        "markdown_inputs": markdown_inputs,
        "expected_pdfs": _dedupe_paths(expected_pdfs),
        "expected_table_reports": _dedupe_paths(expected_table_reports),
    }


def analyze_markdown_files(
    repo_root: Path,
    markdown_files: Sequence[Path],
    profile: AcceptanceProfile,
) -> tuple[dict[str, Any], list[Finding]]:
    """Collect Markdown structure metrics and frontmatter findings."""

    metrics = {
        "files_total": len(markdown_files),
        "lines_total": 0,
        "words_total": 0,
        "headings_total": 0,
        "headings": [],
        "frontmatter_files": 0,
        "links_total": 0,
        "images_total": 0,
        "tables_total": 0,
        "codeblocks_total": 0,
        "todo_markers_total": 0,
        "approved_targets_total": 0,
        "by_locale": {},
        "metadata": [],
        "duplicate_headings_total": 0,
        "link_audit_todo_entries_total": 0,
        "ai_reference_tasks_total": 0,
        "inline_reference_tasks_total": 0,
        "frontmatter_syntax_issues_total": 0,
    }
    findings: list[Finding] = []
    source_ids: dict[str, Path] = {}
    target_records: list[tuple[Path, Mapping[str, Any], str]] = []
    frontmatter_by_path: dict[Path, Mapping[str, Any]] = {}

    for path in markdown_files:
        rel = relative_artifact(path, repo_root)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            findings.append(
                make_finding(
                    rule_id="markdown.read_error",
                    severity="blocked",
                    category="markdown.io",
                    artifact=rel,
                    location="file",
                    evidence=str(exc),
                    editorial_impact="Markdown-Datei kann nicht geprueft werden.",
                    healing="Dateizugriff pruefen und Metriklauf wiederholen.",
                )
            )
            continue

        lines = text.splitlines()
        metrics["lines_total"] += len(lines)
        metrics["words_total"] += len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))
        metrics["links_total"] += len(_LINK_RE.findall(text))
        metrics["images_total"] += len(_IMAGE_RE.findall(text))
        frontmatter_lines = _frontmatter_line_numbers(lines)
        for line_number, line in enumerate(lines, start=1):
            heading_match = _HEADING_RE.match(line)
            if not heading_match:
                continue
            metrics["headings_total"] += 1
            metrics["headings"].append(
                {
                    "artifact": rel,
                    "line": line_number,
                    "level": len(heading_match.group(1)),
                    "title": heading_match.group(2).strip(),
                }
            )
        metrics["tables_total"] += _count_markdown_tables(lines)
        metrics["codeblocks_total"] += _count_fenced_code_blocks(lines)

        todo_count = 0
        for line_number, line in enumerate(lines, start=1):
            if line_number in frontmatter_lines:
                continue
            if _TODO_RE.search(line):
                todo_count += 1
                findings.append(
                    make_finding(
                        rule_id="markdown.review_marker",
                        severity="warn",
                        category="markdown.editorial",
                        artifact=rel,
                        location=f"line {line_number}",
                        evidence=line,
                        editorial_impact="Offene redaktionelle Notiz vor Freigabe pruefen.",
                        healing="TODO/FIXME/REVIEW klaeren oder bewusst als Restrisiko dokumentieren.",
                    )
                )
            long_token = _find_long_token(line, profile.markdown.long_token_warn_chars)
            if long_token:
                findings.append(
                    make_finding(
                        rule_id="markdown.long_token",
                        severity="warn",
                        category="markdown.layout",
                        artifact=rel,
                        location=f"line {line_number}",
                        evidence=long_token,
                        editorial_impact="Sehr lange Tokens koennen PDF-Umbruch und Tabellenlayout belasten.",
                        healing="Token umbrechen, als Code/URL behandeln oder Tabellenstrategie pruefen.",
                    )
                )
        metrics["todo_markers_total"] += todo_count

        frontmatter, frontmatter_error = _read_frontmatter(text)
        if frontmatter_error:
            findings.append(
                make_finding(
                    rule_id="markdown.frontmatter.invalid_yaml",
                    severity="fail",
                    category="markdown.frontmatter",
                    artifact=rel,
                    location="frontmatter",
                    evidence=frontmatter_error,
                    editorial_impact="Frontmatter ist nicht maschinenlesbar.",
                    healing="YAML-Frontmatter korrigieren.",
                )
            )
            continue
        if frontmatter is None:
            if path.name not in profile.markdown.skip_filenames:
                findings.append(
                    make_finding(
                        rule_id="markdown.frontmatter.missing",
                        severity="warn",
                        category="markdown.frontmatter",
                        artifact=rel,
                        location="frontmatter",
                        evidence="no YAML frontmatter",
                        editorial_impact="Datei kann nicht eindeutig einem redaktionellen Profil zugeordnet werden.",
                        healing="Erforderliche Frontmatter-Felder ergaenzen oder Datei im Profil ausnehmen.",
                    )
                )
            continue

        metrics["frontmatter_files"] += 1
        frontmatter_by_path[path.resolve()] = frontmatter
        locale = str(frontmatter.get(profile.markdown.locale_field) or "").strip()
        metrics["metadata"].append(
            {
                "artifact": rel,
                "title": str(frontmatter.get("title") or "").strip() or None,
                "version": str(frontmatter.get("version") or "").strip() or None,
                "locale": locale or None,
                "content_id": str(
                    frontmatter.get(profile.markdown.identity_key) or ""
                ).strip()
                or None,
            }
        )
        if locale:
            by_locale = metrics["by_locale"]
            by_locale[locale] = int(by_locale.get(locale, 0)) + 1

        findings.extend(_check_frontmatter_rules(repo_root, path, frontmatter, profile))
        role = _frontmatter_role(frontmatter, profile)
        identity = str(frontmatter.get(profile.markdown.identity_key) or "").strip()
        if role == "source" and identity:
            source_ids[identity] = path.resolve()
        if role == "target":
            target_records.append((path.resolve(), frontmatter, identity))
            status = str(frontmatter.get("status") or "").strip()
            if status == "approved":
                metrics["approved_targets_total"] += 1

    findings.extend(
        _check_translation_drift(
            repo_root,
            target_records,
            source_ids,
            frontmatter_by_path,
            profile,
        )
    )
    reused_metrics, reused_findings = _collect_reused_markdown_signals(
        repo_root, markdown_files, profile
    )
    metrics.update(reused_metrics)
    findings.extend(reused_findings)
    return metrics, findings


def _collect_reused_markdown_signals(
    repo_root: Path,
    markdown_files: Sequence[Path],
    profile: AcceptanceProfile,
) -> tuple[dict[str, Any], list[Finding]]:
    """Reuse existing quality modules and convert their signals to findings."""

    findings: list[Finding] = []
    todo_entries = list_todos(markdown_files)
    duplicate_headings = _check_near_duplicate_headings(
        markdown_files, profile.markdown.duplicate_heading_near_window
    )
    frontmatter_issues = []
    for markdown_file in markdown_files:
        try:
            frontmatter_issues.extend(check_frontmatter_file(markdown_file))
        except OSError as exc:
            logger.debug(
                "Frontmatter checker could not read %s: %s", markdown_file, exc
            )

    for duplicate in duplicate_headings:
        rel = relative_artifact(duplicate.file, repo_root)
        findings.append(
            make_finding(
                rule_id="markdown.heading.duplicate_title",
                severity="warn",
                category="markdown.structure",
                artifact=rel,
                location=f"line {duplicate.lineno}",
                evidence=f"title={duplicate.title!r}, first_seen={duplicate.first_seen}",
                editorial_impact="Doppelte Titel erschweren PDF-Outline, Querverweise und Review-Kommunikation.",
                healing="Titel praezisieren oder bewusst gleiche Titel im Dossier begruenden.",
            )
        )

    for issue in frontmatter_issues:
        rel = relative_artifact(issue.path, repo_root)
        findings.append(
            make_finding(
                rule_id="markdown.frontmatter.syntax_checker",
                severity="fail",
                category="markdown.frontmatter",
                artifact=rel,
                location=f"line {issue.line}",
                evidence=issue.message,
                editorial_impact="Der bestehende Frontmatter-Checker meldet ungueltige YAML-Syntax.",
                healing="YAML-Syntax korrigieren; Snippet im Checker-Kontext pruefen.",
            )
        )

    reference_tasks = load_reference_tasks(markdown_files, language="de")
    inline_reference_tasks = load_inline_reference_tasks(
        markdown_files,
        include_markdown_links=False,
        include_frontmatter_dois=True,
    )
    metrics = {
        "duplicate_headings_total": len(duplicate_headings),
        "link_audit_todo_entries_total": len(todo_entries),
        "ai_reference_tasks_total": len(reference_tasks),
        "inline_reference_tasks_total": len(inline_reference_tasks),
        "frontmatter_syntax_issues_total": len(frontmatter_issues),
    }
    if reference_tasks or inline_reference_tasks:
        findings.append(
            make_finding(
                rule_id="references.ai.tasks_detected",
                severity="info",
                category="references.ai",
                artifact="markdown scope",
                location="source extraction",
                evidence=(
                    f"source_tasks={len(reference_tasks)}, "
                    f"inline_tasks={len(inline_reference_tasks)}"
                ),
                editorial_impact="AI-Referenzcheck hat pruefbare Referenzkandidaten erkannt.",
                healing="Bei Release-Abnahme optional ai_references mit Review-Protokoll laufen lassen.",
            )
        )
    return metrics, findings


def _check_near_duplicate_headings(
    markdown_files: Sequence[Path], window: int
) -> list[DuplicateHeading]:
    if window <= 0:
        return []

    duplicates: list[DuplicateHeading] = []
    for markdown_file in markdown_files:
        try:
            lines = markdown_file.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue

        headings: list[tuple[int, str]] = []
        for line_number, line in enumerate(lines, start=1):
            match = _HEADING_RE.match(line)
            if match:
                headings.append((line_number, match.group(2).strip().lower()))

        for index, (line_number, title) in enumerate(headings):
            nearby_headings = headings[max(0, index - window) : index]
            for previous_line_number, previous_title in nearby_headings:
                if title == previous_title:
                    duplicates.append(
                        DuplicateHeading(
                            markdown_file,
                            line_number,
                            title,
                            f"{markdown_file}:{previous_line_number}",
                        )
                    )
                    break
    return duplicates


def analyze_pdf(
    repo_root: Path,
    pdf_path: Path,
    profile: AcceptanceProfile,
    log_paths: Sequence[Path] = (),
) -> tuple[dict[str, Any], list[Finding]]:
    """Collect metrics for one PDF artifact."""

    path = _resolve_path(repo_root, pdf_path)
    rel = relative_artifact(path, repo_root)
    metrics: dict[str, Any] = {
        "path": rel,
        "exists": path.exists(),
        "pages_total": 0,
        "file_size_bytes": path.stat().st_size if path.exists() else 0,
        "creation_date": None,
        "modified_at": _path_mtime_iso(path) if path.exists() else None,
        "metadata_title": None,
        "metadata_language": None,
        "build_worker_version": None,
        "page_sizes": [],
        "orientations": {},
        "low_text_pages_le_15": 0,
        "very_low_text_pages_le_5": 0,
        "empty_text_pages": 0,
        "low_text_reason_hints": [],
        "text_extraction_replacement_signals_total": 0,
        "text_extraction_replacement_signals_by_page": [],
        "toc_entries_total": 0,
        "toc_entries": [],
        "fonts": [],
        "script_samples": {},
    }
    findings: list[Finding] = []
    if not path.exists():
        findings.append(
            make_finding(
                rule_id="pdf.artifact.missing",
                severity="blocked",
                category="pdf.artifact",
                artifact=rel,
                location="file",
                evidence="PDF file does not exist",
                editorial_impact="Abnahme kann ohne erwartetes PDF-Artefakt nicht erfolgen.",
                healing="PDF-Build ausfuehren oder Pfad im Abnahmeprofil korrigieren.",
            )
        )
        return metrics, findings

    try:
        reader = PdfReader(str(path))
    except Exception as exc:  # noqa: BLE001 - pypdf can raise multiple parser errors
        findings.append(
            make_finding(
                rule_id="pdf.read_error",
                severity="blocked",
                category="pdf.io",
                artifact=rel,
                location="file",
                evidence=str(exc),
                editorial_impact="PDF kann nicht gelesen werden.",
                healing="PDF neu erzeugen und Parserfehler pruefen.",
            )
        )
        return metrics, findings

    metrics["pages_total"] = len(reader.pages)
    if reader.metadata:
        metrics["creation_date"] = (
            str(reader.metadata.get("/CreationDate") or "") or None
        )
        metrics["metadata_title"] = str(reader.metadata.get("/Title") or "") or None
        metrics["metadata_language"] = str(reader.metadata.get("/Lang") or "") or None
        metrics["build_worker_version"] = _pdf_worker_version(reader.metadata)
    orientations: Counter[str] = Counter()
    text_all: list[str] = []
    page_texts: dict[int, str] = {}
    page_line_counts: dict[int, int] = {}
    replacement_signals_by_page: list[dict[str, int]] = []
    for page_index, page in enumerate(reader.pages, start=1):
        width_pt = float(page.mediabox.width)
        height_pt = float(page.mediabox.height)
        orientation = "landscape" if width_pt > height_pt else "portrait"
        orientations[orientation] += 1
        metrics["page_sizes"].append(
            {
                "page": page_index,
                "width_pt": round(width_pt, 3),
                "height_pt": round(height_pt, 3),
                "orientation": orientation,
            }
        )
        text = page.extract_text() or ""
        text_all.append(text)
        page_texts[page_index] = text
        line_count = len(_meaningful_text_lines(text))
        page_line_counts[page_index] = line_count
        if line_count <= profile.pdf.low_text_page_threshold:
            metrics["low_text_pages_le_15"] += 1
            metrics["low_text_reason_hints"].append(
                {
                    "page": page_index,
                    "lines": line_count,
                    "reason": _guess_low_text_reason(text),
                }
            )
        if line_count <= profile.pdf.very_low_text_page_threshold:
            metrics["very_low_text_pages_le_5"] += 1
        if line_count == 0:
            metrics["empty_text_pages"] += 1
        replacement_counts = _pdf_text_replacement_signal_counts(text)
        if sum(replacement_counts.values()):
            replacement_signals_by_page.append(
                {
                    "page": page_index,
                    "replacement_character": replacement_counts[
                        "replacement_character"
                    ],
                    "white_square": replacement_counts["white_square"],
                    "total": sum(replacement_counts.values()),
                }
            )

    metrics["orientations"] = dict(orientations)
    replacement_signal_total = sum(
        entry["total"] for entry in replacement_signals_by_page
    )
    metrics["text_extraction_replacement_signals_total"] = replacement_signal_total
    metrics["text_extraction_replacement_signals_by_page"] = replacement_signals_by_page
    document_text = "\n".join(text_all).strip()
    metrics["script_samples"] = _script_counts(document_text)
    if not document_text and metrics["pages_total"]:
        findings.append(
            make_finding(
                rule_id="pdf.text.empty_document",
                severity="fail",
                category="pdf.text",
                artifact=rel,
                location="document",
                evidence="No extractable text in PDF",
                editorial_impact="Textqualitaet und TOC-Abgleich koennen nicht belastbar geprueft werden.",
                healing="PDF-Textlayer, Pandoc-Ausgabe und Font-Encoding pruefen.",
            )
        )
    elif metrics["empty_text_pages"]:
        findings.append(
            make_finding(
                rule_id="pdf.text.empty_pages",
                severity="warn",
                category="pdf.text",
                artifact=rel,
                location="pages",
                evidence=f"{metrics['empty_text_pages']} page(s) without meaningful extracted text",
                editorial_impact="Leere oder bildlastige Seiten muessen redaktionell erklaert sein.",
                healing="Seitenkontext pruefen und ggf. als akzeptiertes Restrisiko dokumentieren.",
            )
        )
    if replacement_signal_total:
        page_hint = ", ".join(
            f"p{entry['page']}={entry['total']}"
            for entry in replacement_signals_by_page[:8]
        )
        if len(replacement_signals_by_page) > 8:
            page_hint += ", ..."
        findings.append(
            make_finding(
                rule_id="pdf.text.extraction_replacement",
                severity="warn",
                category="pdf.text",
                artifact=rel,
                location="text extraction",
                evidence=(
                    f"{replacement_signal_total} text extraction replacement signal(s)"
                    + (f" ({page_hint})" if page_hint else "")
                ),
                editorial_impact=(
                    "PDF-Textlayer, Accessibility oder Copy/Paste koennen beeintraechtigt sein; "
                    "das ist ohne Sichtbefund kein harter Font-/Glyphenfehler."
                ),
                healing=(
                    "Visuelle Stichprobe und Poppler/pypdf-Extraktion vergleichen; "
                    "LaTeX-Logs auf echte Missing-character-Signale pruefen."
                ),
            )
        )

    fonts = _safe_extract_fonts(path, rel, findings)
    metrics["fonts"] = [asdict(font) for font in fonts]
    findings.extend(_check_required_fonts(rel, fonts, profile))
    findings.extend(_check_pdf_page_targets(rel, metrics["pages_total"], profile))
    findings.extend(
        _check_expected_pdf_pages(
            rel,
            metrics["pages_total"],
            page_texts,
            page_line_counts,
            profile,
        )
    )
    findings.extend(_check_pdf_text_overflow(rel, page_texts, profile))
    findings.extend(_check_pdf_script_samples(rel, metrics["script_samples"], fonts))
    toc_entries = _safe_extract_pdf_toc(path, rel, findings)
    metrics["toc_entries"] = [asdict(entry) for entry in toc_entries]
    metrics["toc_entries_total"] = len(toc_entries)
    findings.extend(_check_log_patterns(repo_root, rel, log_paths))
    return metrics, findings


def compare_markdown_pdf_toc(
    repo_root: Path,
    markdown_metrics: Mapping[str, Any],
    pdf_metrics: Sequence[Mapping[str, Any]],
) -> list[Finding]:
    """Compare published Markdown headings with extracted PDF outline entries."""

    findings: list[Finding] = []
    headings = [
        heading
        for heading in markdown_metrics.get("headings", [])
        if isinstance(heading, Mapping) and int(heading.get("level") or 0) <= 2
    ]
    if not headings or not pdf_metrics:
        return findings

    outline_entries: list[Mapping[str, Any]] = []
    for pdf_metric in pdf_metrics:
        outline_entries.extend(
            entry
            for entry in pdf_metric.get("toc_entries", [])
            if isinstance(entry, Mapping)
        )
        if pdf_metric.get("exists") and not pdf_metric.get("toc_entries_total"):
            findings.append(
                make_finding(
                    rule_id="pdf.toc.missing",
                    severity="warn",
                    category="pdf.toc",
                    artifact=str(pdf_metric.get("path") or "<pdf>"),
                    location="outline",
                    evidence=f"PDF outline empty; {len(headings)} Markdown H1/H2 headings in publish scope",
                    editorial_impact="PDF-Navigation kann nicht gegen Markdown-Struktur abgeglichen werden.",
                    healing="Pandoc TOC/Outline-Optionen und PDF-Erzeugung pruefen.",
                )
            )

    if not outline_entries:
        return findings

    outline_by_title = {
        _normalize_heading_title(str(entry.get("title") or "")): entry
        for entry in outline_entries
    }
    heading_by_title = {
        _normalize_heading_title(str(heading.get("title") or "")): heading
        for heading in headings
    }

    for heading in headings[:50]:
        normalized = _normalize_heading_title(str(heading.get("title") or ""))
        if not normalized or normalized in outline_by_title:
            continue
        artifact = str(heading.get("artifact") or "<markdown>")
        findings.append(
            make_finding(
                rule_id="pdf.toc.markdown_heading_missing",
                severity="warn",
                category="pdf.toc",
                artifact=artifact,
                location=f"line {heading.get('line', '?')}",
                evidence=str(heading.get("title") or ""),
                editorial_impact="Publizierte Markdown-Ueberschrift fehlt im PDF-Outline-Abgleich.",
                healing="SUMMARY, Heading-Level und Pandoc TOC-Tiefe pruefen.",
            )
        )

    for entry in outline_entries[:50]:
        normalized = _normalize_heading_title(str(entry.get("title") or ""))
        if not normalized or normalized in heading_by_title:
            continue
        findings.append(
            make_finding(
                rule_id="pdf.toc.outline_without_markdown_heading",
                severity="info",
                category="pdf.toc",
                artifact="pdf outline",
                location=f"page {entry.get('page', '?')}",
                evidence=str(entry.get("title") or ""),
                editorial_impact="PDF-Outline enthaelt einen Titel ohne direkten Markdown-Heading-Treffer.",
                healing="Pruefen, ob der Eintrag aus generierten Sections, Metadaten oder falscher Heading-Struktur stammt.",
            )
        )
    return findings


def compare_publish_metadata(
    publish_metrics: Mapping[str, Any],
    markdown_metrics: Mapping[str, Any],
    pdf_metrics: Sequence[Mapping[str, Any]],
) -> list[Finding]:
    """Plausibilize project metadata across manifest, Markdown, and PDF."""

    findings: list[Finding] = []
    entries = [
        entry
        for entry in publish_metrics.get("entries", [])
        if isinstance(entry, Mapping)
    ]
    markdown_metadata = [
        item
        for item in markdown_metrics.get("metadata", [])
        if isinstance(item, Mapping)
    ]
    markdown_versions = {
        str(item.get("version")) for item in markdown_metadata if item.get("version")
    }
    markdown_locales = {
        str(item.get("locale")) for item in markdown_metadata if item.get("locale")
    }
    pdf_by_artifact = {
        str(metric.get("path")): metric
        for metric in pdf_metrics
        if isinstance(metric, Mapping) and metric.get("path")
    }

    for entry in entries:
        manifest = str(entry.get("manifest") or "publish.yml")
        expected_pdf = str(entry.get("expected_pdf") or "")
        pdf_metric = pdf_by_artifact.get(expected_pdf, {})
        manifest_version = str(entry.get("manifest_version") or "").strip()
        if (
            manifest_version
            and markdown_versions
            and manifest_version not in markdown_versions
        ):
            findings.append(
                make_finding(
                    rule_id="metadata.version_mismatch",
                    severity="warn",
                    category="metadata.consistency",
                    artifact=manifest,
                    location=f"publish[{entry.get('index', '?')}].version",
                    evidence=f"manifest={manifest_version}, markdown={sorted(markdown_versions)}",
                    editorial_impact="Release- und Inhaltsversionen wirken nicht deckungsgleich.",
                    healing="Manifest- und Markdown-Versionen angleichen oder bewusste Abweichung dokumentieren.",
                )
            )

        expected_title = str(
            entry.get("entry_title") or entry.get("manifest_title") or ""
        ).strip()
        pdf_title = str(pdf_metric.get("metadata_title") or "").strip()
        if (
            expected_title
            and pdf_title
            and _normalize_heading_title(expected_title)
            != _normalize_heading_title(pdf_title)
        ):
            findings.append(
                make_finding(
                    rule_id="metadata.title_mismatch",
                    severity="warn",
                    category="metadata.consistency",
                    artifact=expected_pdf or manifest,
                    location="pdf metadata title",
                    evidence=f"manifest={expected_title!r}, pdf={pdf_title!r}",
                    editorial_impact="PDF-Titel und Manifesttitel sind nicht plausibel synchron.",
                    healing="PDF-Metadaten, publish.yml title/name und Buch-Metadaten pruefen.",
                )
            )

        expected_language = str(
            entry.get("entry_language") or entry.get("manifest_language") or ""
        ).strip()
        pdf_language = str(pdf_metric.get("metadata_language") or "").strip()
        known_languages = {lang.lower() for lang in markdown_locales if lang}
        if (
            expected_language
            and known_languages
            and expected_language.lower() not in known_languages
        ):
            findings.append(
                make_finding(
                    rule_id="metadata.language_mismatch",
                    severity="warn",
                    category="metadata.consistency",
                    artifact=manifest,
                    location=f"publish[{entry.get('index', '?')}].language",
                    evidence=f"manifest={expected_language!r}, markdown={sorted(known_languages)}",
                    editorial_impact="Manifest-Sprache passt nicht zum publizierten Markdown-Scope.",
                    healing="publish.yml language/lang oder Markdown-Frontmatter content_lang pruefen.",
                )
            )
        if (
            expected_language
            and pdf_language
            and expected_language.lower() not in pdf_language.lower()
        ):
            findings.append(
                make_finding(
                    rule_id="metadata.pdf_language_mismatch",
                    severity="info",
                    category="metadata.consistency",
                    artifact=expected_pdf or manifest,
                    location="pdf metadata language",
                    evidence=f"manifest={expected_language!r}, pdf={pdf_language!r}",
                    editorial_impact="PDF-Sprachmetadaten weichen vom Manifest ab oder fehlen in anderer Notation.",
                    healing="PDF-Metadaten pruefen; bei fehlendem PDF-Lang ggf. Pandoc-Variablen ergaenzen.",
                )
            )
    return findings


def analyze_release_documentation(
    repo_root: Path,
    profile: AcceptanceProfile,
    pdf_metrics: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], list[Finding]]:
    """Scan release documents for stale worker/page/layout claims."""

    metrics: dict[str, Any] = {
        "enabled": profile.documentation.scan_release_docs,
        "files_total": 0,
        "stale_worker_claims_total": 0,
        "stale_page_claims_total": 0,
        "layout_claims_total": 0,
    }
    findings: list[Finding] = []
    if not profile.documentation.scan_release_docs:
        return metrics, findings

    pdf_pages = {
        Path(str(metric.get("path") or "")).stem.lower(): int(
            metric.get("pages_total") or 0
        )
        for metric in pdf_metrics
        if isinstance(metric, Mapping) and metric.get("path")
    }
    for release_doc in _iter_release_docs(repo_root, profile):
        rel = relative_artifact(release_doc, repo_root)
        metrics["files_total"] += 1
        try:
            lines = release_doc.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            findings.append(
                make_finding(
                    rule_id="release_docs.read_error",
                    severity="warn",
                    category="release_docs.drift",
                    artifact=rel,
                    location="file",
                    evidence=str(exc),
                    editorial_impact="Release-Dokument kann nicht auf Drift geprueft werden.",
                    healing="Dateizugriff pruefen oder Release-Dokument aus dem Scan nehmen.",
                )
            )
            continue
        for line_number, line in enumerate(lines, start=1):
            worker_match = re.search(
                r"(?:gitbook[-_ ]?worker|worker[-_ ]?version)\D+(\d+\.\d+\.\d+)",
                line,
                re.IGNORECASE,
            )
            if worker_match and _version_tuple(worker_match.group(1)) < _version_tuple(
                __version__
            ):
                metrics["stale_worker_claims_total"] += 1
                findings.append(
                    make_finding(
                        rule_id="release_docs.worker_version.stale",
                        severity="warn",
                        category="release_docs.drift",
                        artifact=rel,
                        location=f"line {line_number}",
                        evidence=f"claimed={worker_match.group(1)}, current={__version__}",
                        editorial_impact="Release-Dokument nennt eine aeltere Worker-Version als der aktuelle Lauf.",
                        healing="Release-Dokument aktualisieren oder historischen Bezug klar kennzeichnen.",
                    )
                )

            page_match = re.search(r"(?:pages|seiten)\D+(\d+)", line, re.IGNORECASE)
            if page_match:
                claimed_pages = int(page_match.group(1))
                for stem, actual_pages in pdf_pages.items():
                    if (
                        stem
                        and stem in line.lower()
                        and actual_pages
                        and claimed_pages != actual_pages
                    ):
                        metrics["stale_page_claims_total"] += 1
                        findings.append(
                            make_finding(
                                rule_id="release_docs.page_count.stale",
                                severity="warn",
                                category="release_docs.drift",
                                artifact=rel,
                                location=f"line {line_number}",
                                evidence=f"{stem}: claimed={claimed_pages}, actual={actual_pages}",
                                editorial_impact="Release-Dokument nennt eine alte Seitenzahl fuer ein aktuelles PDF.",
                                healing="Seitenzahl im Release-Dokument aktualisieren oder als historisch markieren.",
                            )
                        )
            if re.search(r"layout\s*(?:findings|befunde|issues)", line, re.IGNORECASE):
                metrics["layout_claims_total"] += 1
    return metrics, findings


def _iter_release_docs(repo_root: Path, profile: AcceptanceProfile) -> Iterable[Path]:
    seen: set[Path] = set()
    for raw_dir in profile.documentation.release_doc_dirs:
        directory = _resolve_path(repo_root, Path(raw_dir))
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.md")):
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield path


def _version_tuple(value: str) -> tuple[int, int, int]:
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", str(value))
    if not match:
        return (0, 0, 0)
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def discover_table_layout_reports(
    repo_root: Path, markdown_inputs: Sequence[str]
) -> list[Path]:
    """Find table layout JSONL reports near known content roots."""

    roots = [repo_root / raw for raw in markdown_inputs if raw and raw != "."] or [
        repo_root
    ]
    reports: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        for path in root.rglob("*.table-layout.jsonl"):
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                reports.append(path)
    return reports


def analyze_table_reports(
    repo_root: Path,
    table_report_paths: Sequence[Path],
    *,
    artifact_links: Mapping[str, str] | None = None,
) -> tuple[dict[str, Any], list[Finding]]:
    """Aggregate table strategy JSONL reports."""

    metrics: dict[str, Any] = {
        "reports_total": len(table_report_paths),
        "decisions_total": 0,
        "selected_paper_counts": {},
        "method_counts": {},
        "problem_decisions_total": 0,
        "fallback_decisions_total": 0,
        "override_decisions_total": 0,
        "rejected_candidate_decisions_total": 0,
        "rejected_candidates_total": 0,
        "artifact_links": {},
    }
    findings: list[Finding] = []
    selected_counts: Counter[str] = Counter()
    method_counts: Counter[str] = Counter()
    problem_methods = {
        "lowest-score-fallback",
        "override",
        "disabled",
        "oversize-preserve-column-heuristic",
    }

    for report_path in table_report_paths:
        path = _resolve_path(repo_root, report_path)
        rel = relative_artifact(path, repo_root)
        linked_pdf = _linked_pdf_for_table_report(rel, artifact_links or {})
        if linked_pdf:
            metrics["artifact_links"][rel] = linked_pdf
        if not path.exists():
            findings.append(
                make_finding(
                    rule_id="tables.report.missing",
                    severity="warn",
                    category="tables.report",
                    artifact=rel,
                    location="file",
                    evidence="table layout report not found",
                    editorial_impact="Tabellenstrategie kann fuer dieses Artefakt nicht aggregiert werden.",
                    healing="Build mit table_paper_strategy.report=jsonl wiederholen oder Reportpfad korrigieren.",
                )
            )
            continue
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                findings.append(
                    make_finding(
                        rule_id="tables.report.invalid_jsonl",
                        severity="warn",
                        category="tables.report",
                        artifact=rel,
                        location=f"line {line_number}",
                        evidence=str(exc),
                        editorial_impact="Tabellenreport ist teilweise nicht lesbar.",
                        healing="Report neu erzeugen oder defekte JSONL-Zeile entfernen.",
                    )
                )
                continue
            metrics["decisions_total"] += 1
            selected = str(record.get("selected_paper") or "<unknown>")
            method = str(record.get("method") or "<unknown>")
            rejected_count, rejected_summary = _table_rejected_candidate_summary(
                record.get("evaluations")
            )
            selected_summary = _table_selected_candidate_summary(record, selected)
            context = _table_decision_context(record, line_number)
            selected_counts[selected] += 1
            method_counts[method] += 1
            if method in {
                "lowest-score-fallback",
                "oversize-preserve-column-heuristic",
            }:
                metrics["fallback_decisions_total"] += 1
            if method == "override":
                metrics["override_decisions_total"] += 1
            if rejected_count:
                metrics["rejected_candidate_decisions_total"] += 1
                metrics["rejected_candidates_total"] += rejected_count
            if method in problem_methods:
                metrics["problem_decisions_total"] += 1
                findings.append(
                    make_finding(
                        rule_id=f"tables.strategy.{method}",
                        severity="warn" if method != "override" else "info",
                        category="tables.strategy",
                        artifact=rel,
                        location=context,
                        evidence=_table_strategy_evidence(
                            method=method,
                            selected=selected,
                            linked_pdf=linked_pdf,
                            selected_summary=selected_summary,
                            rejected_summary=rejected_summary,
                            override=record.get("override"),
                        ),
                        editorial_impact="Tabellenlayout enthaelt eine bewusste oder riskante Strategieentscheidung.",
                        healing="Auswahl im Dossier redaktionell pruefen und ggf. Override begruenden.",
                    )
                )
            elif rejected_count:
                metrics["problem_decisions_total"] += 1
                findings.append(
                    make_finding(
                        rule_id="tables.strategy.rejected_candidates",
                        severity="info",
                        category="tables.strategy",
                        artifact=rel,
                        location=context,
                        evidence=_table_strategy_evidence(
                            method=method,
                            selected=selected,
                            linked_pdf=linked_pdf,
                            selected_summary=selected_summary,
                            rejected_summary=rejected_summary,
                            override=record.get("override"),
                        ),
                        editorial_impact="Mindestens ein Papierkandidat wurde verworfen; die finale Auswahl ist nachvollziehbar zu pruefen.",
                        healing="Bei knappen Tabellen die Kandidatenbewertung gegen Markdown-Quelle und PDF-Seite pruefen.",
                    )
                )

    metrics["selected_paper_counts"] = dict(selected_counts)
    metrics["method_counts"] = dict(method_counts)
    return metrics, findings


def _table_decision_context(record: Mapping[str, Any], line_number: int) -> str:
    parts = [f"line {line_number}"]
    source = _first_text(
        record, "source_path", "source", "markdown_path", "file", "path"
    )
    if source:
        parts.append(source)
    table_index = (
        record.get("table_index") if "table_index" in record else record.get("table")
    )
    if table_index is not None:
        parts.append(f"table {table_index}")
    heading = _first_text(record, "heading", "nearest_heading", "context_heading")
    if heading:
        parts.append(f"heading {heading}")
    return "; ".join(parts)


def _table_rejected_candidate_summary(evaluations: Any) -> tuple[int, str]:
    if not isinstance(evaluations, Sequence) or isinstance(evaluations, (str, bytes)):
        return 0, ""

    rejected: list[Mapping[str, Any]] = [
        evaluation
        for evaluation in evaluations
        if isinstance(evaluation, Mapping) and evaluation.get("acceptable") is False
    ]
    if not rejected:
        return 0, ""

    details = [_table_candidate_summary(evaluation) for evaluation in rejected[:3]]
    if len(rejected) > 3:
        details.append(f"+{len(rejected) - 3} more")
    return len(rejected), f"rejected_candidates={len(rejected)} ({'; '.join(details)})"


def _table_selected_candidate_summary(
    record: Mapping[str, Any], selected_paper: str
) -> str:
    evaluations = record.get("evaluations")
    if not isinstance(evaluations, Sequence) or isinstance(evaluations, (str, bytes)):
        return ""
    for evaluation in evaluations:
        if not isinstance(evaluation, Mapping):
            continue
        if str(evaluation.get("paper") or "") == selected_paper:
            return f"selected_candidate=({_table_candidate_summary(evaluation)})"
    return ""


def _table_candidate_summary(evaluation: Mapping[str, Any]) -> str:
    paper = str(evaluation.get("paper") or "<paper>")
    parts = [paper]
    for key in (
        "score",
        "overflow_mm",
        "unbreakable_overflow_mm",
        "max_cell_lines",
        "average_row_lines",
    ):
        value = evaluation.get(key)
        if value is not None:
            parts.append(f"{key}={value}")
    reasons = evaluation.get("reasons")
    if isinstance(reasons, Sequence) and not isinstance(reasons, (str, bytes)):
        reason_text = ",".join(str(reason) for reason in reasons[:3])
        if reason_text:
            parts.append(f"reasons={reason_text}")
    return ", ".join(parts)


def _table_strategy_evidence(
    *,
    method: str,
    selected: str,
    linked_pdf: str | None,
    selected_summary: str,
    rejected_summary: str,
    override: Any,
) -> str:
    parts = [f"method={method}", f"selected_paper={selected}"]
    if linked_pdf:
        parts.append(f"pdf={linked_pdf}")
    if selected_summary:
        parts.append(selected_summary)
    if rejected_summary:
        parts.append(rejected_summary)
    if isinstance(override, Mapping):
        reason = override.get("reason")
        paper = override.get("paper")
        if paper:
            parts.append(f"override_paper={paper}")
        if reason:
            parts.append(f"override_reason={reason}")
    return "; ".join(parts)


def _first_text(record: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = record.get(key)
        if value is not None:
            text = str(value).strip()
            if text:
                return text
    return ""


def _table_report_artifact_links(entries: Sequence[Any]) -> dict[str, str]:
    links: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        report = str(entry.get("expected_table_report") or "").strip()
        pdf = str(entry.get("expected_pdf") or "").strip()
        if report and pdf:
            links[report.replace("\\", "/").lower().lstrip("./")] = pdf
    return links


def _linked_pdf_for_table_report(
    report_artifact: str, artifact_links: Mapping[str, str]
) -> str | None:
    normalized = report_artifact.replace("\\", "/").lower().lstrip("./")
    name = Path(normalized).name
    for raw_key, linked_pdf in artifact_links.items():
        key = str(raw_key).replace("\\", "/").lower().lstrip("./")
        if key == normalized or key == name or key.endswith(f"/{name}"):
            return linked_pdf
    return None


def build_arg_parser() -> argparse.ArgumentParser:
    """Build CLI parser for editorial metrics."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--project", help="Project name for the report")
    parser.add_argument("--content-config", type=Path, help="Path to content.yaml")
    parser.add_argument(
        "--lang",
        action="append",
        dest="languages",
        help="Language/content id to scan; repeatable",
    )
    parser.add_argument(
        "--markdown-root",
        action="append",
        type=Path,
        default=None,
        help="Markdown root to scan; repeatable",
    )
    parser.add_argument(
        "--pdf",
        action="append",
        type=Path,
        default=None,
        help="PDF artifact to inspect; repeatable",
    )
    parser.add_argument(
        "--table-report",
        action="append",
        type=Path,
        default=None,
        help="Table layout JSONL report; repeatable",
    )
    parser.add_argument(
        "--discover-table-reports",
        action="store_true",
        help="Discover *.table-layout.jsonl below Markdown roots",
    )
    parser.add_argument(
        "--log",
        action="append",
        type=Path,
        default=None,
        help="Build log file or directory to scan; repeatable",
    )
    parser.add_argument(
        "--profile", default="local-preview", help="Editorial profile name"
    )
    parser.add_argument(
        "--profile-config", type=Path, help="YAML file containing editorial profiles"
    )
    parser.add_argument("-o", "--output", type=Path, help="Destination JSON report")
    parser.add_argument("--csv-output", type=Path, help="Optional findings CSV report")
    parser.add_argument(
        "--sarif-output", type=Path, help="Optional SARIF findings report"
    )
    parser.add_argument(
        "--stdout-json", action="store_true", help="Print report JSON to stdout"
    )
    parser.add_argument(
        "--console-summary",
        action="store_true",
        help="Print one compact status line for humans/CI logs",
    )
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Return a failing exit code for fail/blocked findings",
    )
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Treat warnings as failing when --fail-on-findings is set",
    )
    add_exit_code_help(parser)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the editorial metrics CLI."""

    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        handle_exit_code_help(args, component="editorial")
    except SystemExit as exc:
        return int(exc.code or 0)

    root = args.root.resolve()
    try:
        profile = load_acceptance_profile(args.profile_config, args.profile)
    except ValueError as exc:
        logger.error("Invalid editorial profile: %s", exc)
        return EDITORIAL_INVALID_PROFILE_EXIT_CODE

    report = collect_editorial_metrics(
        repo_root=root,
        project=args.project,
        profile=profile,
        content_config=args.content_config,
        languages=args.languages,
        markdown_roots=args.markdown_root,
        pdf_paths=args.pdf,
        table_report_paths=args.table_report,
        log_paths=args.log,
        discover_table_reports=args.discover_table_reports,
    )
    output = args.output or root / "logs" / "quality" / "editorial-metrics.json"
    write_json_report(report, output)
    if args.csv_output:
        write_findings_csv(report, args.csv_output)
    if args.sarif_output:
        write_findings_sarif(report, args.sarif_output)
    logger.info("Editorial metrics report written to %s", output)
    if args.stdout_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.console_summary:
        print(format_console_summary(report))
    summary = report["summary"]
    logger.info(
        "Editorial metrics status=%s findings=%s",
        summary["status"],
        summary["finding_counts"],
    )
    if args.fail_on_findings:
        counts = summary["finding_counts"]
        if counts.get("blocked", 0):
            return EDITORIAL_BLOCKED_EXIT_CODE
        if counts.get("fail", 0) or (args.fail_on_warnings and counts.get("warn", 0)):
            return EDITORIAL_HARD_FINDINGS_EXIT_CODE
    return 0


def write_findings_csv(report: Mapping[str, Any], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "id",
        "severity",
        "category",
        "rule_id",
        "artifact",
        "location",
        "evidence",
        "editorial_impact",
        "healing",
    ]
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for finding in report.get("findings", []):
            if not isinstance(finding, Mapping):
                continue
            writer.writerow({field: finding.get(field, "") for field in fields})


def write_findings_sarif(report: Mapping[str, Any], destination: Path) -> None:
    """Write findings as SARIF 2.1.0 for code scanning integrations."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    findings = [
        finding
        for finding in report.get("findings", [])
        if isinstance(finding, Mapping)
    ]
    rules: dict[str, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []
    for finding in findings:
        rule_id = str(finding.get("rule_id") or "editorial.finding")
        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "name": rule_id,
                "shortDescription": {"text": rule_id},
                "help": {"text": str(finding.get("healing") or "Review finding.")},
                "properties": {"category": str(finding.get("category") or "")},
            }
        result: dict[str, Any] = {
            "ruleId": rule_id,
            "level": _sarif_level(finding.get("severity")),
            "message": {"text": _sarif_message(finding)},
            "partialFingerprints": {
                "gitbookWorkerFindingId": str(finding.get("id") or "")
            },
        }
        location = _sarif_location(finding)
        if location:
            result["locations"] = [location]
        results.append(result)
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "gitbook-worker editorial_metrics",
                        "semanticVersion": __version__,
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }
    destination.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _sarif_level(severity: object) -> str:
    severity_text = str(severity or "")
    if severity_text in {"blocked", "fail"}:
        return "error"
    if severity_text == "warn":
        return "warning"
    return "note"


def _sarif_message(finding: Mapping[str, Any]) -> str:
    parts = [
        str(finding.get("evidence") or "").strip(),
        str(finding.get("editorial_impact") or "").strip(),
        str(finding.get("healing") or "").strip(),
    ]
    return " | ".join(part for part in parts if part) or str(
        finding.get("rule_id") or "Editorial finding"
    )


def _sarif_location(finding: Mapping[str, Any]) -> dict[str, Any] | None:
    artifact = str(finding.get("artifact") or "").strip()
    if not artifact:
        return None
    physical_location: dict[str, Any] = {
        "artifactLocation": {"uri": artifact.replace("\\", "/")}
    }
    line = _sarif_line_number(finding.get("location"))
    if line is not None:
        physical_location["region"] = {"startLine": line}
    return {"physicalLocation": physical_location}


def _sarif_line_number(location: object) -> int | None:
    match = re.search(r"\bline\s+(\d+)\b", str(location or ""), re.IGNORECASE)
    if not match:
        return None
    line = int(match.group(1))
    return line if line > 0 else None


def format_console_summary(report: Mapping[str, Any]) -> str:
    summary = (
        report.get("summary") if isinstance(report.get("summary"), Mapping) else {}
    )
    counts = (
        summary.get("finding_counts")
        if isinstance(summary.get("finding_counts"), Mapping)
        else {}
    )
    return (
        "editorial_metrics "
        f"status={summary.get('status', '<unknown>')} "
        f"blocked={counts.get('blocked', 0)} "
        f"fail={counts.get('fail', 0)} "
        f"warn={counts.get('warn', 0)} "
        f"info={counts.get('info', 0)}"
    )


def _analyze_publish_entry(
    repo_root: Path,
    manifest: Path,
    manifest_data: Mapping[str, Any],
    index: int,
    entry: Mapping[str, Any],
    profile: AcceptanceProfile,
) -> tuple[dict[str, Any], list[Finding]]:
    findings: list[Finding] = []
    manifest_dir = manifest.parent
    raw_path = str(entry.get("path") or "").strip()
    source = _resolve_from_base(manifest_dir, raw_path or ".")
    rel_source = relative_artifact(source, repo_root)
    out_name = str(entry.get("out") or "").strip()
    out_dir = _resolve_from_base(manifest_dir, str(entry.get("out_dir") or "publish"))
    out_format = str(
        entry.get("out_format")
        or entry.get("target_format")
        or entry.get("format")
        or "pdf"
    ).lower()
    use_summary = _as_bool(entry.get("use_summary")) or _as_bool(
        entry.get("use_book_json")
    )
    source_type = str(entry.get("source_type") or entry.get("type") or "").lower()
    if source_type not in {"file", "folder"}:
        source_type = "folder" if source.is_dir() else "file"

    metrics: dict[str, Any] = {
        "manifest": relative_artifact(manifest, repo_root),
        "index": index,
        "manifest_version": str(manifest_data.get("version") or "").strip() or None,
        "manifest_title": _manifest_title(manifest_data),
        "manifest_language": _manifest_language(manifest_data),
        "entry_title": str(entry.get("title") or entry.get("name") or "").strip()
        or None,
        "entry_language": str(entry.get("language") or entry.get("lang") or "").strip()
        or None,
        "source_root": rel_source,
        "source_type": source_type,
        "use_summary": use_summary,
        "summary_appendices_last": _as_bool(entry.get("summary_appendices_last")),
        "out_format": out_format,
        "out_dir": relative_artifact(out_dir, repo_root),
        "out": out_name,
        "published_markdown_files": [],
        "published_markdown_files_total": 0,
        "unpublished_markdown_files_total": 0,
        "orphaned_markdown_files_total": 0,
        "expected_pdfs_total": 0,
        "missing_expected_pdfs_total": 0,
        "expected_table_reports_total": 0,
        "missing_expected_table_reports_total": 0,
        "expected_pdf": None,
        "expected_table_report": None,
    }

    if not source.exists():
        findings.append(
            make_finding(
                rule_id="publish.source.missing",
                severity="blocked",
                category="publish.scope",
                artifact=relative_artifact(manifest, repo_root),
                location=f"publish[{index}].path",
                evidence=f"path={raw_path!r}",
                editorial_impact="Publikationsscope verweist auf fehlende Markdown-Quelle.",
                healing="publish.yml path korrigieren oder Quelle ergaenzen.",
            )
        )
        return metrics, findings

    if source_type == "file":
        published_files = (
            [source] if source.suffix.lower() in {".md", ".markdown"} else []
        )
        all_markdown_files = published_files
        orphaned_files: list[Path] = []
        missing_summary_refs: list[str] = []
    else:
        all_markdown_files = _discover_markdown_under_source(source, profile)
        published_files, missing_summary_refs = _published_files_from_summary(
            source, use_summary
        )
        if not published_files:
            published_files = all_markdown_files
        published_set = {path.resolve() for path in published_files}
        orphaned_files = [
            path
            for path in all_markdown_files
            if path.resolve() not in published_set
            and path.name not in profile.markdown.skip_filenames
        ]

    metrics["published_markdown_files"] = [
        relative_artifact(path, repo_root) for path in published_files
    ]
    metrics["published_markdown_files_total"] = len(published_files)
    metrics["unpublished_markdown_files_total"] = len(orphaned_files)
    metrics["orphaned_markdown_files_total"] = len(orphaned_files) if use_summary else 0

    for target in missing_summary_refs[:20]:
        findings.append(
            make_finding(
                rule_id="publish.summary.missing_target",
                severity="warn",
                category="publish.scope",
                artifact=rel_source,
                location="SUMMARY.md",
                evidence=target,
                editorial_impact="SUMMARY verweist auf eine fehlende Markdown-Datei.",
                healing="SUMMARY-Link korrigieren oder Datei wiederherstellen.",
            )
        )

    if use_summary:
        for orphaned in orphaned_files[:20]:
            findings.append(
                make_finding(
                    rule_id="publish.summary.orphaned_markdown",
                    severity="warn",
                    category="publish.scope",
                    artifact=relative_artifact(orphaned, repo_root),
                    location="SUMMARY.md",
                    evidence="Markdown file is not referenced by publish SUMMARY",
                    editorial_impact="Datei liegt im Publikationsbaum, wird aber voraussichtlich nicht ins PDF uebernommen.",
                    healing="Datei in SUMMARY aufnehmen, bewusst ausschliessen oder aus dem Scope verschieben.",
                )
            )

    if use_summary and _as_bool(entry.get("summary_appendices_last")):
        findings.extend(_check_summary_appendices_last(repo_root, published_files))

    if out_format == "pdf" and out_name:
        expected_pdf = (out_dir / out_name).resolve()
        metrics["expected_pdf"] = relative_artifact(expected_pdf, repo_root)
        metrics["expected_pdfs_total"] = 1
        if not expected_pdf.exists():
            metrics["missing_expected_pdfs_total"] = 1
            findings.append(
                make_finding(
                    rule_id="publish.pdf.missing_artifact",
                    severity="blocked",
                    category="publish.artifact",
                    artifact=relative_artifact(expected_pdf, repo_root),
                    location=f"publish[{index}].out",
                    evidence=f"build=true expected {out_name!r}",
                    editorial_impact="Build-true Publish-Eintrag hat kein erzeugtes PDF-Artefakt.",
                    healing="PDF-Build ausfuehren oder publish.yml build/out/out_dir korrigieren.",
                )
            )

        table_report = _expected_table_report(entry, out_dir, out_name)
        if table_report:
            metrics["expected_table_report"] = relative_artifact(
                table_report, repo_root
            )
            metrics["expected_table_reports_total"] = 1
            if not table_report.exists():
                metrics["missing_expected_table_reports_total"] = 1
                findings.append(
                    make_finding(
                        rule_id="publish.tables.missing_report",
                        severity="warn",
                        category="tables.report",
                        artifact=relative_artifact(table_report, repo_root),
                        location=f"publish[{index}].pdf_options.table_paper_strategy",
                        evidence="table strategy report configured but not found",
                        editorial_impact="Tabellenstrategie kann fuer das Publish-Artefakt nicht vollstaendig bewertet werden.",
                        healing="Build mit table_paper_strategy.report=jsonl wiederholen oder Reportpfad korrigieren.",
                    )
                )

    return metrics, findings


def _discover_markdown_under_source(
    source: Path, profile: AcceptanceProfile
) -> list[Path]:
    exclude_dirs = set(profile.markdown.exclude_dirs)
    files: list[Path] = []
    for path in sorted(source.rglob("*.md")):
        if not path.is_file():
            continue
        try:
            rel_parts = path.resolve().relative_to(source.resolve()).parts
        except ValueError:
            continue
        if any(part in exclude_dirs for part in rel_parts):
            continue
        files.append(path)
    return files


def _check_summary_appendices_last(
    repo_root: Path, published_files: Sequence[Path]
) -> list[Finding]:
    findings: list[Finding] = []
    appendix_seen = False
    first_appendix: Path | None = None
    for path in published_files:
        if _is_appendix_path(path):
            appendix_seen = True
            if first_appendix is None:
                first_appendix = path
            continue
        if appendix_seen:
            findings.append(
                make_finding(
                    rule_id="publish.summary.appendix_order",
                    severity="warn",
                    category="publish.scope",
                    artifact=relative_artifact(path, repo_root),
                    location="SUMMARY.md order",
                    evidence=(
                        "summary_appendices_last=true but non-appendix follows "
                        f"{relative_artifact(first_appendix or path, repo_root)}"
                    ),
                    editorial_impact="Kapitel erscheinen nach Anhaengen, obwohl summary_appendices_last aktiv ist.",
                    healing="SUMMARY-Reihenfolge oder publish.yml summary_appendices_last pruefen.",
                )
            )
            break
    return findings


def _is_appendix_path(path: Path) -> bool:
    lowered = path.as_posix().lower()
    return any(
        marker in lowered
        for marker in ("appendix", "appendices", "anhang", "anhaenge", "anhänge")
    )


def _manifest_title(manifest_data: Mapping[str, Any]) -> str | None:
    project = manifest_data.get("project")
    candidates = [manifest_data.get("title"), manifest_data.get("name")]
    if isinstance(project, Mapping):
        candidates.extend([project.get("title"), project.get("name")])
    for candidate in candidates:
        text = str(candidate or "").strip()
        if text:
            return text
    return None


def _manifest_language(manifest_data: Mapping[str, Any]) -> str | None:
    project = manifest_data.get("project")
    candidates = [manifest_data.get("language"), manifest_data.get("lang")]
    if isinstance(project, Mapping):
        candidates.extend([project.get("language"), project.get("lang")])
    for candidate in candidates:
        text = str(candidate or "").strip()
        if text:
            return text
    return None


def _published_files_from_summary(
    source: Path, use_summary: bool
) -> tuple[list[Path], list[str]]:
    if not use_summary:
        return [], []
    try:
        summary_layout = get_summary_layout(source)
    except Exception as exc:  # noqa: BLE001 - fallback is handled by caller
        logger.debug("Could not resolve SUMMARY layout for %s: %s", source, exc)
        return [], []
    if not summary_layout.summary_path.exists():
        return [], []
    files: list[Path] = []
    missing: list[str] = []
    seen: set[Path] = set()
    for line in summary_layout.summary_path.read_text(encoding="utf-8").splitlines():
        for raw_target in _SUMMARY_LINK_RE.findall(line):
            target = unquote(raw_target.split("#", 1)[0].strip())
            if target.startswith(("http://", "https://")):
                continue
            candidate = (summary_layout.root_dir / target).resolve()
            if candidate.exists():
                if candidate not in seen:
                    seen.add(candidate)
                    files.append(candidate)
            else:
                missing.append(target)
    return files, missing


def _expected_table_report(
    entry: Mapping[str, Any], out_dir: Path, out_name: str
) -> Path | None:
    pdf_options = entry.get("pdf_options")
    if not isinstance(pdf_options, Mapping):
        return None
    table_strategy = pdf_options.get("table_paper_strategy") or pdf_options.get(
        "table-paper-strategy"
    )
    if not isinstance(table_strategy, Mapping):
        return None
    report_path = table_strategy.get("report_path") or table_strategy.get("report-file")
    if report_path:
        candidate = Path(str(report_path))
        return candidate if candidate.is_absolute() else (out_dir / candidate).resolve()
    report_mode = str(table_strategy.get("report") or "").strip().lower()
    if report_mode in _PDF_REPORT_MODES:
        stem = Path(out_name).stem or "table-layout"
        return (out_dir / f"{stem}.table-layout.jsonl").resolve()
    return None


def _resolve_from_base(base: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    return (
        candidate.resolve() if candidate.is_absolute() else (base / candidate).resolve()
    )


def _dedupe_paths(paths: Iterable[Path]) -> list[Path]:
    result: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            result.append(path)
    return result


def _as_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _path_mtime_iso(path: Path) -> str | None:
    try:
        return (
            datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
            .replace(microsecond=0)
            .isoformat()
        )
    except OSError:
        return None


def _guess_low_text_reason(text: str) -> str:
    lowered = text.lower()
    meaningful = _meaningful_text_lines(text)
    if not meaningful:
        return "empty"
    if "|" in text or "table" in lowered or "tabelle" in lowered:
        return "table"
    if "http://" in lowered or "https://" in lowered or "doi" in lowered:
        return "references-or-url"
    if any(marker in lowered for marker in ("figure", "abbildung", "caption")):
        return "image-or-caption"
    if len(meaningful) <= 3 and any(line.startswith("#") for line in meaningful):
        return "chapter-start"
    return "unknown"


def _check_pdf_page_targets(
    artifact: str, pages_total: int, profile: AcceptanceProfile
) -> list[Finding]:
    target = _pdf_target_for_artifact(artifact, profile.pdf.pdf_targets)
    if not target:
        return []
    findings: list[Finding] = []
    min_pages = target.get("target_pages_min")
    max_pages = target.get("target_pages_max")
    warn_pages_max = target.get("warn_pages_max")
    if min_pages is not None and pages_total < min_pages:
        findings.append(
            make_finding(
                rule_id="pdf.pages.below_target",
                severity="fail",
                category="pdf.pages",
                artifact=artifact,
                location="document",
                evidence=f"pages_total={pages_total}, target_pages_min={min_pages}",
                editorial_impact="PDF liegt unter dem projektspezifischen Seitenzahl-Zielkorridor.",
                healing="Build-Input, fehlende Kapitel oder Zielkorridor pruefen.",
            )
        )
    if max_pages is not None and pages_total > max_pages:
        findings.append(
            make_finding(
                rule_id="pdf.pages.above_target",
                severity="fail",
                category="pdf.pages",
                artifact=artifact,
                location="document",
                evidence=f"pages_total={pages_total}, target_pages_max={max_pages}",
                editorial_impact="PDF ueberschreitet den projektspezifischen Seitenzahl-Zielkorridor.",
                healing="Layout, Tabellenstrategie oder Zielkorridor redaktionell pruefen.",
            )
        )
    elif warn_pages_max is not None and pages_total > warn_pages_max:
        findings.append(
            make_finding(
                rule_id="pdf.pages.above_warning_target",
                severity="warn",
                category="pdf.pages",
                artifact=artifact,
                location="document",
                evidence=f"pages_total={pages_total}, warn_pages_max={warn_pages_max}",
                editorial_impact="PDF liegt oberhalb des weichen Seitenzahl-Warnkorridors.",
                healing="Seitenwachstum im Dossier begruenden oder Layout optimieren.",
            )
        )
    return findings


def _check_expected_pdf_pages(
    artifact: str,
    pages_total: int,
    page_texts: Mapping[int, str],
    page_line_counts: Mapping[int, int],
    profile: AcceptanceProfile,
) -> list[Finding]:
    rules = _pdf_expected_pages_for_artifact(artifact, profile.pdf.expected_pages)
    findings: list[Finding] = []
    for rule in rules:
        page = _int_value(rule.get("page"))
        if page is None:
            continue
        label = str(rule.get("label") or f"page {page}")
        if page < 1 or page > pages_total:
            findings.append(
                make_finding(
                    rule_id="pdf.sample_page.missing",
                    severity="fail",
                    category="pdf.sample_page",
                    artifact=artifact,
                    location=f"page {page}",
                    evidence=f"expected sample page {label!r}; pages_total={pages_total}",
                    editorial_impact="Eine erwartete Sample-Seite fehlt im PDF-Artefakt.",
                    healing="Build-Input, SUMMARY oder Sample-Regel pruefen.",
                    page=page,
                )
            )
            continue
        min_lines = _int_value(rule.get("min_text_lines"))
        actual_lines = int(page_line_counts.get(page, 0))
        if min_lines is not None and actual_lines < min_lines:
            findings.append(
                make_finding(
                    rule_id="pdf.sample_page.low_text",
                    severity="warn",
                    category="pdf.sample_page",
                    artifact=artifact,
                    location=f"page {page}",
                    evidence=f"{label}: lines={actual_lines}, min_text_lines={min_lines}",
                    editorial_impact="Eine erwartete Sample-Seite enthaelt weniger extrahierbaren Text als erwartet.",
                    healing="PDF-Textlayer, Sample-Erwartung oder Seiteninhalt pruefen.",
                    page=page,
                )
            )
        must_contain = str(rule.get("must_contain") or "").strip()
        if must_contain and must_contain not in page_texts.get(page, ""):
            findings.append(
                make_finding(
                    rule_id="pdf.sample_page.missing_text",
                    severity="fail",
                    category="pdf.sample_page",
                    artifact=artifact,
                    location=f"page {page}",
                    evidence=f"{label}: missing {must_contain!r}",
                    editorial_impact="Eine erwartete Sample-Seite enthaelt nicht den geforderten Textanker.",
                    healing="Sample-Regel oder PDF-Inhalt pruefen.",
                    page=page,
                )
            )
    return findings


def _check_pdf_text_overflow(
    artifact: str,
    page_texts: Mapping[int, str],
    profile: AcceptanceProfile,
) -> list[Finding]:
    findings: list[Finding] = []
    token_threshold = profile.pdf.overflow_token_warn_chars
    for page, text in page_texts.items():
        for token in re.findall(r"https?://\S+|doi:\S+|10\.\d{4,9}/\S+|\S+", text):
            cleaned = token.strip().strip(".,;:)]}")
            if len(cleaned) < token_threshold:
                continue
            overflow_pt = round((len(cleaned) - token_threshold + 1) * 2.1, 3)
            if overflow_pt < profile.pdf.overflow_warn_pt:
                continue
            overflow_mm = round(overflow_pt * 0.352778, 3)
            severity = "fail" if overflow_pt >= profile.pdf.overflow_fail_pt else "warn"
            cause = (
                "url-or-doi" if _looks_like_reference_token(cleaned) else "long-token"
            )
            findings.append(
                make_finding(
                    rule_id="pdf.layout.text_overflow",
                    severity=severity,
                    category="pdf.layout",
                    artifact=artifact,
                    location=f"page {page}",
                    evidence=(
                        f"type=text-overflow, overflow_pt={overflow_pt}, "
                        f"overflow_mm={overflow_mm}, cause={cause}, text={cleaned[:120]}"
                    ),
                    editorial_impact="Ein langer extrahierter Token kann auf BBox-/Overflow-Risiko im PDF hindeuten.",
                    healing="URL/DOI umbrechen, als Fussnote setzen oder Profil-Schwelle bewusst als Restrisiko dokumentieren.",
                    page=page,
                )
            )
            break
    return findings


def _check_pdf_script_samples(
    artifact: str, script_counts: Mapping[str, int], fonts: Sequence[Any]
) -> list[Finding]:
    active = {name: count for name, count in script_counts.items() if count}
    if not active:
        return []
    font_names = " ".join(str(getattr(font, "name", "")) for font in fonts).lower()
    has_cjk_font = any(
        marker in font_names for marker in ("cjk", "noto", "sourcehan", "ipa")
    )
    severity = "info" if has_cjk_font else "warn"
    return [
        make_finding(
            rule_id="pdf.text.script_sample",
            severity=severity,
            category="pdf.text",
            artifact=artifact,
            location="document",
            evidence=", ".join(
                f"{key}={value}" for key, value in sorted(active.items())
            ),
            editorial_impact="PDF enthaelt CJK/Hangul/Kana-Zeichen und braucht sichtbare Schriftabdeckung.",
            healing="Eingebettete CJK-Fonts und Stichprobenseiten pruefen; fehlende Fonts in fonts.yml konfigurieren.",
        )
    ]


def _pdf_target_for_artifact(
    artifact: str, targets: Mapping[str, Mapping[str, Any]]
) -> Mapping[str, Any] | None:
    normalized_artifact = artifact.replace("\\", "/").lower().lstrip("./")
    artifact_name = Path(normalized_artifact).name
    for raw_key, target in targets.items():
        key = str(raw_key).replace("\\", "/").lower().lstrip("./")
        if (
            key == normalized_artifact
            or key == artifact_name
            or key.endswith(f"/{artifact_name}")
        ):
            return target
    return None


def _pdf_expected_pages_for_artifact(
    artifact: str, expected_pages: Mapping[str, Sequence[Mapping[str, Any]]]
) -> Sequence[Mapping[str, Any]]:
    normalized_artifact = artifact.replace("\\", "/").lower().lstrip("./")
    artifact_name = Path(normalized_artifact).name
    for raw_key, rules in expected_pages.items():
        key = str(raw_key).replace("\\", "/").lower().lstrip("./")
        if (
            key == normalized_artifact
            or key == artifact_name
            or key.endswith(f"/{artifact_name}")
        ):
            return rules
    return ()


def _int_value(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _looks_like_reference_token(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith(("http://", "https://", "doi:")) or lowered.startswith(
        "10."
    )


def _script_counts(text: str) -> dict[str, int]:
    counts = {"cjk": 0, "hangul": 0, "kana": 0}
    for char in text:
        codepoint = ord(char)
        if 0x4E00 <= codepoint <= 0x9FFF:
            counts["cjk"] += 1
        elif 0xAC00 <= codepoint <= 0xD7AF:
            counts["hangul"] += 1
        elif 0x3040 <= codepoint <= 0x30FF:
            counts["kana"] += 1
    return counts


def _pdf_worker_version(metadata: Mapping[str, Any]) -> str | None:
    for key in (
        "/GitBookWorkerVersion",
        "/GitBook-Worker-Version",
        "/GitBookWorker",
        "/Producer",
        "/Creator",
    ):
        value = str(metadata.get(key) or "")
        match = re.search(
            r"gitbook[-_ ]?worker\D+(\d+\.\d+\.\d+)", value, re.IGNORECASE
        )
        if match:
            return match.group(1)
    return None


def _safe_extract_pdf_toc(path: Path, rel: str, findings: list[Finding]) -> list[Any]:
    try:
        return extract_pdf_toc(path, logger=logger)
    except Exception as exc:  # noqa: BLE001 - TOC extraction is diagnostic only
        findings.append(
            make_finding(
                rule_id="pdf.toc.extract_error",
                severity="warn",
                category="pdf.toc",
                artifact=rel,
                location="outline",
                evidence=str(exc),
                editorial_impact="PDF-Outline konnte nicht extrahiert werden.",
                healing="PDF-Parser und Artefakt pruefen; bei Bedarf TOC-Abgleich manuell dokumentieren.",
            )
        )
        return []


def _normalize_heading_title(value: str) -> str:
    text = re.sub(r"\s+", " ", value).strip().lower()
    text = re.sub(
        r"^(chapter|appendix|anhang|kapitel)\s+[\w.-]+\s*[–—:-]?\s*", "", text
    )
    text = re.sub(r"^[\d.ivxlcdm]+[.)]\s*", "", text)
    return re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip()


def _check_frontmatter_rules(
    repo_root: Path,
    path: Path,
    frontmatter: Mapping[str, Any],
    profile: AcceptanceProfile,
) -> list[Finding]:
    findings: list[Finding] = []
    rel = relative_artifact(path, repo_root)
    for key in profile.markdown.forbidden_frontmatter_keys:
        if key in frontmatter:
            findings.append(
                make_finding(
                    rule_id="markdown.frontmatter.forbidden_key",
                    severity="fail",
                    category="markdown.frontmatter",
                    artifact=rel,
                    location=f"frontmatter.{key}",
                    evidence=f"forbidden key {key!r} present",
                    editorial_impact="Verbotene Frontmatter-Keys koennen Pandoc/Babel- oder Fontfallback-Verhalten stoeren.",
                    healing=f"Key {key!r} entfernen und gewuenschtes Verhalten ueber publish.yml steuern.",
                )
            )

    role = _frontmatter_role(frontmatter, profile)
    if role is None:
        return findings
    required = profile.markdown.required_frontmatter_by_role.get(role, ())
    for key in required:
        value = frontmatter.get(key)
        if value is None or str(value).strip() == "":
            findings.append(
                make_finding(
                    rule_id="markdown.frontmatter.required_missing",
                    severity="fail" if role == "target" else "warn",
                    category="markdown.frontmatter",
                    artifact=rel,
                    location=f"frontmatter.{key}",
                    evidence=f"required {role} field {key!r} missing",
                    editorial_impact="Pflichtmetadaten fehlen fuer redaktionelle Zuordnung und Uebersetzungsabgleich.",
                    healing=f"Frontmatter-Feld {key!r} ergaenzen oder Profilregel anpassen.",
                )
            )
    if role == "target":
        status = str(frontmatter.get("status") or "").strip()
        if status and status not in profile.markdown.allowed_translation_status:
            findings.append(
                make_finding(
                    rule_id="markdown.translation.status_invalid",
                    severity="fail",
                    category="markdown.translation",
                    artifact=rel,
                    location="frontmatter.status",
                    evidence=f"status={status!r}",
                    editorial_impact="Uebersetzungsstatus ist nicht Teil des freigegebenen Workflows.",
                    healing="Status auf erlaubten Wert setzen oder Profil bewusst erweitern.",
                )
            )
    return findings


def _check_translation_drift(
    repo_root: Path,
    target_records: Sequence[tuple[Path, Mapping[str, Any], str]],
    source_ids: Mapping[str, Path],
    frontmatter_by_path: Mapping[Path, Mapping[str, Any]],
    profile: AcceptanceProfile,
) -> list[Finding]:
    findings: list[Finding] = []
    for target_path, frontmatter, identity in target_records:
        rel = relative_artifact(target_path, repo_root)
        raw_source = str(
            frontmatter.get(profile.markdown.source_link_field) or ""
        ).strip()
        if raw_source:
            source_path = (repo_root / raw_source).resolve()
            if not source_path.exists():
                findings.append(
                    make_finding(
                        rule_id="markdown.translation.source_missing",
                        severity="fail",
                        category="markdown.translation",
                        artifact=rel,
                        location=f"frontmatter.{profile.markdown.source_link_field}",
                        evidence=f"source={raw_source!r}",
                        editorial_impact="Target-Datei verweist auf eine fehlende Source-Datei.",
                        healing="Repo-relativen Source-Pfad korrigieren oder Source-Datei ergaenzen.",
                    )
                )
            else:
                source_frontmatter = frontmatter_by_path.get(source_path)
                if source_frontmatter is not None:
                    source_identity = str(
                        source_frontmatter.get(profile.markdown.identity_key) or ""
                    ).strip()
                    if identity and source_identity and identity != source_identity:
                        findings.append(
                            make_finding(
                                rule_id="markdown.translation.content_id_mismatch",
                                severity="fail",
                                category="markdown.translation",
                                artifact=rel,
                                location="frontmatter.content_id",
                                evidence=f"target={identity!r}, source={source_identity!r}",
                                editorial_impact="Source und Target sind nicht eindeutig dieselbe Inhaltseinheit.",
                                healing="content_id zwischen Source und Target angleichen.",
                            )
                        )
        if identity and source_ids and identity not in source_ids:
            findings.append(
                make_finding(
                    rule_id="markdown.translation.source_identity_missing",
                    severity="warn",
                    category="markdown.translation",
                    artifact=rel,
                    location="frontmatter.content_id",
                    evidence=f"target content_id={identity!r} has no matching source content_id",
                    editorial_impact="Uebersetzungsbezug ist ueber content_id nicht nachvollziehbar.",
                    healing="Source-content_id pruefen oder Target-content_id korrigieren.",
                )
            )
    return findings


def _read_frontmatter(text: str) -> tuple[Mapping[str, Any] | None, str | None]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, None
    block_lines: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            try:
                loaded = yaml.safe_load("\n".join(block_lines) or "{}") or {}
            except yaml.YAMLError as exc:
                return None, str(exc).strip()
            if not isinstance(loaded, Mapping):
                return None, "frontmatter must be a mapping"
            return loaded, None
        block_lines.append(line)
    return None, "unterminated frontmatter"


def _frontmatter_role(
    frontmatter: Mapping[str, Any], profile: AcceptanceProfile
) -> str | None:
    locale = str(frontmatter.get(profile.markdown.locale_field) or "").strip()
    if profile.markdown.source_locale and locale == profile.markdown.source_locale:
        return "source"
    if locale in profile.markdown.target_locales:
        return "target"
    return None


def _count_markdown_tables(lines: Sequence[str]) -> int:
    return sum(1 for line in lines if _TABLE_SEPARATOR_RE.match(line))


def _count_fenced_code_blocks(lines: Sequence[str]) -> int:
    count = 0
    in_fence = False
    fence_marker = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
                count += 1
            elif marker == fence_marker:
                in_fence = False
    return count


def _find_long_token(line: str, threshold: int) -> str | None:
    for token in re.findall(r"\S+", line):
        if len(token) >= threshold and not _is_breakable_url_token(token):
            return token
    return None


def _is_breakable_url_token(token: str) -> bool:
    if "http://" in token or "https://" in token:
        return True
    stripped = token.strip("<>()[]{}.,;:\"'")
    if stripped.startswith(("http://", "https://")):
        return True
    if token.startswith(("[http://", "[https://")) and "](" in token:
        return True
    return False


def _frontmatter_line_numbers(lines: Sequence[str]) -> set[int]:
    if not lines or lines[0].strip() != "---":
        return set()
    for index, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            return set(range(1, index + 1))
    return set()


def _meaningful_text_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not _FOOTER_LINE_RE.match(line.strip())
    ]


def _pdf_text_replacement_signal_counts(text: str) -> Counter[str]:
    return Counter(
        {
            "replacement_character": text.count("�"),
            "white_square": text.count("□"),
        }
    )


def _safe_extract_fonts(path: Path, rel: str, findings: list[Finding]) -> list[Any]:
    try:
        return extract_pdf_fonts(path)
    except Exception as exc:  # noqa: BLE001 - font extraction is diagnostic only
        findings.append(
            make_finding(
                rule_id="pdf.fonts.extract_error",
                severity="warn",
                category="pdf.fonts",
                artifact=rel,
                location="fonts",
                evidence=str(exc),
                editorial_impact="PDF-Fontsignale konnten nicht vollstaendig erhoben werden.",
                healing="Poppler/pypdf-Umgebung pruefen oder PDF neu erzeugen.",
            )
        )
        return []


def _check_required_fonts(
    artifact: str, fonts: Sequence[Any], profile: AcceptanceProfile
) -> list[Finding]:
    findings: list[Finding] = []
    for expected in profile.pdf.required_fonts:
        match = next(
            (font for font in fonts if font_name_matches(expected, font.name)), None
        )
        if match is None:
            findings.append(
                make_finding(
                    rule_id="pdf.fonts.required_missing",
                    severity="fail",
                    category="pdf.fonts",
                    artifact=artifact,
                    location="fonts",
                    evidence=f"required font {expected!r} not found",
                    editorial_impact="Erwarteter Projektfont ist nicht im PDF nachweisbar.",
                    healing="Fontprofil, Pandoc-Variablen und PDF-Embedding pruefen.",
                )
            )
        elif not match.embedded:
            findings.append(
                make_finding(
                    rule_id="pdf.fonts.required_unembedded",
                    severity="fail",
                    category="pdf.fonts",
                    artifact=artifact,
                    location="fonts",
                    evidence=f"font {expected!r} matched {match.name!r} but is not embedded",
                    editorial_impact="PDF ist moeglicherweise nicht reproduzierbar darstellbar.",
                    healing="Font-Embedding im LaTeX/Pandoc-Lauf erzwingen.",
                )
            )
    return findings


def _check_log_patterns(
    repo_root: Path, artifact: str, log_paths: Sequence[Path]
) -> list[Finding]:
    findings: list[Finding] = []
    matches = scan_forbidden_log_patterns(log_paths) if log_paths else []
    for match in matches[:20]:
        findings.append(
            make_finding(
                rule_id="pdf.logs.forbidden_pattern",
                severity="warn",
                category="pdf.fonts",
                artifact=artifact,
                location=f"{relative_artifact(match.path, repo_root)}:{match.line_number}",
                evidence=match.line,
                editorial_impact="Build-Log enthaelt Missing-Glyph- oder .notdef-Signale.",
                healing="Logstelle pruefen und Fontfallback/Unicode-Abdeckung korrigieren.",
            )
        )
    return findings


def _resolve_path(repo_root: Path, path: Path) -> Path:
    return path if path.is_absolute() else (repo_root / path).resolve()


if __name__ == "__main__":
    raise SystemExit(main())
