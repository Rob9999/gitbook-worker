"""Document type parsing and summary helpers for SUMMARY.md generation.

This module stays side-effect free beyond filesystem reads, so it can be
reused in both CLI and tests. It parses Markdown front matter, infers missing
values, and produces structured records for summary generation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import yaml

# Core catalog of supported document types
DOC_TYPES = {
    "cover",
    "preface",
    "chapter",
    "part",
    "epilog",
    "appendix",
    "chapter-appendix",
    "list-of-tables",
    "list-of-figures",
    "list-of-abbreviations",
    "list-of-symbols",
    "list-of-equations",
    "list-of-algorithms",
    "list-of-listings",
    "glossary",
    "legal-notice",
    "bibliography",
    "index",
    "attributions",
    "errata",
    "release-notes",
    "colophon",
    "placeholder",
    "template",
    "example",
    "dedication",
    "translators-note",
}


@dataclass
class DocumentTypeConfig:
    section_order: List[str]
    section_titles: Dict[str, str]
    section_titles_by_locale: Dict[str, Dict[str, str]]
    show_in_summary: Dict[str, bool]
    auto_number_chapters: bool
    auto_number_appendices: bool
    auto_number_parts: bool
    chapter_appendix_indent: bool
    chapter_appendix_prefix: str
    default_order_weight: int


@dataclass
class DocumentRecord:
    path: Path
    doc_type: str
    title: str
    order: Optional[int] = None
    chapter_number: Optional[List[int]] = None
    part_number: Optional[List[int]] = None
    appendix_id: Optional[str] = None
    chapter_ref: Optional[str] = None
    parent_chapter: Optional[List[int]] = None
    is_appendix_child: bool = False
    extra: Dict[str, object] = field(default_factory=dict)

    @property
    def display_title(self) -> str:
        return self.title or self.path.stem.replace("-", " ").strip()


_FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(md_path: Path) -> tuple[dict, str]:
    text = md_path.read_text(encoding="utf-8")
    match = _FRONTMATTER_PATTERN.match(text)
    frontmatter: dict = {}
    body = text
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1)) or {}
        except Exception:
            frontmatter = {}
        body = text[match.end() :]
    return frontmatter, body


def _first_heading(body: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def _parse_number_parts(value: object) -> Optional[List[int]]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return [int(value)]
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        parts = []
        for chunk in cleaned.replace("-", ".").split("."):
            if not chunk:
                continue
            try:
                parts.append(int(chunk))
            except ValueError:
                return None
        return parts or None
    return None


def _infer_doc_type(path: Path) -> Optional[str]:
    name = path.name.lower()
    stem = path.stem.lower()
    parent = path.parent.name.lower()
    if name in {"index.md", "readme.md"}:
        return "cover"
    if stem == "preface" or "vorwort" in stem:
        return "preface"
    if parent == "chapters" or stem.startswith("chapter-"):
        return "chapter"
    if (
        parent == "appendices"
        or stem.startswith("appendix-")
        or stem.startswith("anhang-")
    ):
        return "appendix"
    if stem in {"list-of-tables", "tabellenverzeichnis"}:
        return "list-of-tables"
    if stem in {"list-of-figures", "abbildungsverzeichnis"}:
        return "list-of-figures"
    if stem in {"glossary", "glossar"}:
        return "glossary"
    if stem in {"references", "bibliography", "literatur"}:
        return "bibliography"
    if stem.startswith("index"):
        return "index"
    if stem.startswith("attribution") or "danksag" in stem:
        return "attributions"
    if "colophon" in stem or "impressum" in stem:
        return "colophon"
    return None


def load_document_type_config(raw_manifest: dict) -> Optional[DocumentTypeConfig]:
    publish_entries = (
        raw_manifest.get("publish") if isinstance(raw_manifest, dict) else None
    )
    if not publish_entries or not isinstance(publish_entries, list):
        return None
    # Use first publish entry for now
    entry = publish_entries[0] or {}
    if not entry.get("use_document_types"):
        return None
    cfg = entry.get("document_type_config") or {}
    return DocumentTypeConfig(
        section_order=cfg.get("section_order", []),
        section_titles=cfg.get("section_titles", {}),
        section_titles_by_locale=cfg.get("section_titles_by_locale", {}),
        show_in_summary=cfg.get("show_in_summary", {}),
        auto_number_chapters=bool(cfg.get("auto_number_chapters", True)),
        auto_number_appendices=bool(cfg.get("auto_number_appendices", True)),
        auto_number_parts=bool(cfg.get("auto_number_parts", True)),
        chapter_appendix_indent=bool(cfg.get("chapter_appendix_indent", True)),
        chapter_appendix_prefix=cfg.get(
            "chapter_appendix_prefix", "Appendix {chapter}.{id}"
        ),
        default_order_weight=int(cfg.get("default_order_weight", 100)),
    )


def collect_documents(root_dir: Path) -> List[DocumentRecord]:
    records: List[DocumentRecord] = []
    for md_path in root_dir.rglob("*.md"):
        if md_path.name.lower() in {"summary.md", "summary"}:
            continue
        frontmatter, body = _parse_frontmatter(md_path)
        doc_type = (
            frontmatter.get("doc_type") if isinstance(frontmatter, dict) else None
        )
        if doc_type not in DOC_TYPES:
            doc_type = _infer_doc_type(md_path)
        if not doc_type:
            continue
        title = frontmatter.get("title") if isinstance(frontmatter, dict) else None
        if not title:
            title = _first_heading(body) or md_path.stem.replace("-", " ")
        order_value = (
            frontmatter.get("order") if isinstance(frontmatter, dict) else None
        )
        order = int(order_value) if isinstance(order_value, int) else None
        chapter_number = _parse_number_parts(
            frontmatter.get("chapter_number") if isinstance(frontmatter, dict) else None
        )
        parent_chapter = _parse_number_parts(
            frontmatter.get("parent_chapter") if isinstance(frontmatter, dict) else None
        )
        part_number = _parse_number_parts(
            frontmatter.get("part_number") if isinstance(frontmatter, dict) else None
        )
        appendix_id = (
            frontmatter.get("appendix_id") if isinstance(frontmatter, dict) else None
        )
        chapter_ref = (
            frontmatter.get("chapter_ref") if isinstance(frontmatter, dict) else None
        )
        record = DocumentRecord(
            path=md_path.relative_to(root_dir),
            doc_type=doc_type,
            title=title,
            order=order,
            chapter_number=chapter_number,
            part_number=part_number,
            appendix_id=appendix_id,
            chapter_ref=str(chapter_ref) if chapter_ref is not None else None,
            parent_chapter=parent_chapter,
            extra=frontmatter if isinstance(frontmatter, dict) else {},
        )
        records.append(record)
    return records


def _weight(record: DocumentRecord, default_weight: int) -> int:
    return record.order if record.order is not None else default_weight


def _format_chapter_title(record: DocumentRecord, index: int) -> str:
    base = record.display_title
    if record.chapter_number:
        number_str = ".".join(str(n) for n in record.chapter_number)
        return f"Chapter {number_str} – {base}"
    return f"Chapter {index} – {base}"


def _format_appendix_title(record: DocumentRecord, index: int) -> str:
    base = record.display_title
    appendix_id = record.appendix_id or chr(ord("A") + index - 1)
    if not base.lower().startswith("appendix") and not base.lower().startswith(
        "anhang"
    ):
        return f"Appendix {appendix_id} – {base}"
    return base


def build_doc_type_summary(
    records: Iterable[DocumentRecord],
    config: DocumentTypeConfig,
    *,
    locale: Optional[str] = None,
) -> List[str]:
    section_lines: List[str] = ["# Summary", ""]

    by_type: Dict[str, List[DocumentRecord]] = {}
    for record in records:
        by_type.setdefault(record.doc_type, []).append(record)

    # helper sorters
    def sort_chapters(items: List[DocumentRecord]) -> List[DocumentRecord]:
        return sorted(
            items,
            key=lambda r: (
                r.part_number or [0],
                r.chapter_number or [config.default_order_weight],
                _weight(r, config.default_order_weight),
                r.display_title.lower(),
            ),
        )

    def sort_appendices(items: List[DocumentRecord]) -> List[DocumentRecord]:
        return sorted(
            items,
            key=lambda r: (
                r.appendix_id or "",
                _weight(r, config.default_order_weight),
                r.display_title.lower(),
            ),
        )

    locale_titles = config.section_titles_by_locale.get(locale or "", {})

    for section in config.section_order:
        docs: List[DocumentRecord] = []
        if section == "chapters":
            docs = sort_chapters(by_type.get("chapter", []))
        elif section == "appendices":
            docs = sort_appendices(by_type.get("appendix", []))
        else:
            primary = by_type.get(section.rstrip("s"), [])
            secondary = (
                by_type.get(section, []) if section.rstrip("s") != section else []
            )
            docs = sorted(
                primary + secondary,
                key=lambda r: (
                    _weight(r, config.default_order_weight),
                    r.display_title.lower(),
                ),
            )

        if not docs:
            continue

        section_title = (
            locale_titles.get(section) or config.section_titles.get(section) or section
        )
        section_lines.append(f"## {section_title}")
        section_lines.append("")

        if section == "chapters":
            part_groups: Dict[str, List[DocumentRecord]] = {}
            for rec in docs:
                key = (
                    ".".join(str(n) for n in rec.part_number) if rec.part_number else ""
                )
                part_groups.setdefault(key, []).append(rec)

            for part_key, part_docs in sorted(part_groups.items()):
                if part_key and config.auto_number_parts:
                    section_lines.append(f"* Part {part_key}")
                for idx, rec in enumerate(part_docs, start=1):
                    title = (
                        _format_chapter_title(rec, idx)
                        if config.auto_number_chapters
                        else rec.display_title
                    )
                    section_lines.append(f"* [{title}]({rec.path.as_posix()})")
                    # nest chapter appendices beneath
                    for child in sort_appendices(by_type.get("chapter-appendix", [])):
                        if child.chapter_ref and rec.chapter_number:
                            if child.chapter_ref == ".".join(
                                str(n) for n in rec.chapter_number
                            ):
                                prefix = config.chapter_appendix_prefix.format(
                                    chapter=child.chapter_ref,
                                    id=child.appendix_id or "A",
                                )
                                line_title = (
                                    f"{prefix} – {child.display_title}"
                                    if config.chapter_appendix_indent
                                    else child.display_title
                                )
                                indent = "  " if config.chapter_appendix_indent else ""
                                section_lines.append(
                                    f"{indent}* [{line_title}]({child.path.as_posix()})"
                                )
                section_lines.append("")
            if section_lines and section_lines[-1] == "":
                section_lines.pop()
                section_lines.append("")
        elif section == "appendices":
            for idx, rec in enumerate(docs, start=1):
                title = (
                    _format_appendix_title(rec, idx)
                    if config.auto_number_appendices
                    else rec.display_title
                )
                section_lines.append(f"* [{title}]({rec.path.as_posix()})")
            section_lines.append("")
        else:
            for rec in docs:
                if (
                    section in config.show_in_summary
                    and not config.show_in_summary.get(section, True)
                ):
                    continue
                section_lines.append(f"* [{rec.display_title}]({rec.path.as_posix()})")
            section_lines.append("")

    # trim trailing blank line
    while section_lines and not section_lines[-1].strip():
        section_lines.pop()
    section_lines.append("")
    return section_lines
