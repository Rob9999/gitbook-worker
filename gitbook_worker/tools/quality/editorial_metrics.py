"""Collect editorial Markdown, PDF, and table-layout quality metrics."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml
from pypdf import PdfReader

from gitbook_worker.tools.exit_codes import add_exit_code_help, handle_exit_code_help
from gitbook_worker.tools.logging_config import get_logger
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
from gitbook_worker.tools.testing.pdf_validator import (
    extract_pdf_fonts,
    font_name_matches,
    scan_forbidden_log_patterns,
)
from gitbook_worker.tools.utils.smart_content import load_content_config

logger = get_logger(__name__)


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
_TODO_RE = re.compile(r"\b(TODO|FIXME|REVIEW|XXX)\b", re.IGNORECASE)
_TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
_FOOTER_LINE_RE = re.compile(r"^\s*(?:page\s*)?\d+\s*$", re.IGNORECASE)


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
    for pdf_path in pdf_paths or ():
        metrics, findings = analyze_pdf(root, pdf_path, active_profile, log_paths or ())
        pdf_metrics.append(metrics)
        pdf_findings.extend(findings)

    table_paths = list(table_report_paths or ())
    if discover_table_reports:
        table_paths.extend(discover_table_layout_reports(root, markdown_inputs))
    table_metrics, table_findings = analyze_table_reports(root, table_paths)

    findings = [*markdown_findings, *pdf_findings, *table_findings]
    inputs = {
        "repo_root": ".",
        "content_config": (
            relative_artifact(content_config, root) if content_config else None
        ),
        "languages": list(languages or []),
        "markdown_roots": markdown_inputs,
        "pdfs": [relative_artifact(path, root) for path in pdf_paths or ()],
        "table_reports": [relative_artifact(path, root) for path in table_paths],
        "logs": [relative_artifact(path, root) for path in log_paths or ()],
        "network": active_profile.network,
    }
    metrics = {
        "markdown": markdown_metrics,
        "pdf": pdf_metrics,
        "tables": table_metrics,
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
        "frontmatter_files": 0,
        "links_total": 0,
        "images_total": 0,
        "tables_total": 0,
        "codeblocks_total": 0,
        "todo_markers_total": 0,
        "approved_targets_total": 0,
        "by_locale": {},
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
        metrics["headings_total"] += sum(1 for line in lines if _HEADING_RE.match(line))
        metrics["tables_total"] += _count_markdown_tables(lines)
        metrics["codeblocks_total"] += _count_fenced_code_blocks(lines)

        todo_count = 0
        for line_number, line in enumerate(lines, start=1):
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
    return metrics, findings


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
        "page_sizes": [],
        "orientations": {},
        "low_text_pages_le_15": 0,
        "very_low_text_pages_le_5": 0,
        "empty_text_pages": 0,
        "fonts": [],
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
    orientations: Counter[str] = Counter()
    text_all: list[str] = []
    replacement_hits = 0
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
        line_count = len(_meaningful_text_lines(text))
        if line_count <= profile.pdf.low_text_page_threshold:
            metrics["low_text_pages_le_15"] += 1
        if line_count <= profile.pdf.very_low_text_page_threshold:
            metrics["very_low_text_pages_le_5"] += 1
        if line_count == 0:
            metrics["empty_text_pages"] += 1
        replacement_hits += text.count("□") + text.count("�")

    metrics["orientations"] = dict(orientations)
    document_text = "\n".join(text_all).strip()
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
    if replacement_hits:
        findings.append(
            make_finding(
                rule_id="pdf.text.replacement_glyph",
                severity="fail",
                category="pdf.fonts",
                artifact=rel,
                location="text extraction",
                evidence=f"{replacement_hits} replacement glyph signal(s)",
                editorial_impact="Moegliche fehlende Glyphen oder Fontfallback-Probleme im PDF.",
                healing="Fontkonfiguration und LaTeX-Logs pruefen.",
            )
        )

    fonts = _safe_extract_fonts(path, rel, findings)
    metrics["fonts"] = [asdict(font) for font in fonts]
    findings.extend(_check_required_fonts(rel, fonts, profile))
    findings.extend(_check_log_patterns(repo_root, rel, log_paths))
    return metrics, findings


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
    repo_root: Path, table_report_paths: Sequence[Path]
) -> tuple[dict[str, Any], list[Finding]]:
    """Aggregate table strategy JSONL reports."""

    metrics: dict[str, Any] = {
        "reports_total": len(table_report_paths),
        "decisions_total": 0,
        "selected_paper_counts": {},
        "method_counts": {},
        "problem_decisions_total": 0,
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
            selected_counts[selected] += 1
            method_counts[method] += 1
            if method in problem_methods:
                metrics["problem_decisions_total"] += 1
                findings.append(
                    make_finding(
                        rule_id=f"tables.strategy.{method}",
                        severity="warn" if method != "override" else "info",
                        category="tables.strategy",
                        artifact=rel,
                        location=f"line {line_number}",
                        evidence=f"method={method}, selected_paper={selected}",
                        editorial_impact="Tabellenlayout enthaelt eine bewusste oder riskante Strategieentscheidung.",
                        healing="Auswahl im Dossier redaktionell pruefen und ggf. Override begruenden.",
                    )
                )

    metrics["selected_paper_counts"] = dict(selected_counts)
    metrics["method_counts"] = dict(method_counts)
    return metrics, findings


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
    parser.add_argument(
        "--stdout-json", action="store_true", help="Print report JSON to stdout"
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
    logger.info("Editorial metrics report written to %s", output)
    if args.stdout_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
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
        if len(token) >= threshold:
            return token
    return None


def _meaningful_text_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not _FOOTER_LINE_RE.match(line.strip())
    ]


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
