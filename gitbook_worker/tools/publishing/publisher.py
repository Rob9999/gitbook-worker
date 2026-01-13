#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selective Publisher

DESIGN PRINCIPLE: Font License Compliance
==========================================
This publisher enforces strict font configuration to ensure license compliance and attribution:
- ALL fonts must be explicitly configured in fonts.yml (single source of truth)
- NO hardcoded font fallbacks allowed (violates license tracking)
- NO automatic system font discovery (prevents attribution)
- Font selection uses only fonts.yml entries to maintain reproducible builds

This guarantees we can always fulfill attribution requirements and license obligations
for every font used in published documents.

Core Operations:
- Reads publish.yml|yaml from repository root
- Identifies entries with build: true -> get_publish_list()
- Prepares environment (PyYAML, optional Pandoc/LaTeX & configured fonts) -> prepare_publishing()
- Builds PDFs for 'file' and 'folder' types -> build_pdf()
- Resets build flags after successful build -> main()

Usage Examples:
  python gitbook_worker/tools/publishing/publisher.py
  python gitbook_worker/tools/publishing/publisher.py --manifest publish.yml --use-summary
  python gitbook_worker/tools/publishing/publisher.py --no-apt --only-prepare

See argparse configuration below for all options.
"""

from __future__ import annotations

import argparse
import hashlib
import contextlib
import json
import os
import pathlib
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections import OrderedDict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union
from collections.abc import Mapping
from functools import lru_cache
from urllib.parse import urlparse

from gitbook_worker.core.application.svg_to_pdf import ensure_svg_pdf

from gitbook_worker.tools.logging_config import get_logger
from gitbook_worker.tools.utils.asset_copy import copy_assets_to_temp
from gitbook_worker.tools.utils.language_context import (
    build_language_env,
    resolve_language_context,
)
from gitbook_worker.tools.utils.smart_manifest import (
    DEFAULT_FILENAMES,
    SmartManifestError,
    detect_repo_root,
    resolve_manifest,
)

from gitbook_worker.tools.publishing.font_config import get_font_config
from gitbook_worker.tools.publishing.smart_font_stack import (
    SmartFontError,
    prepare_runtime_font_loader,
)
from gitbook_worker.tools.publishing.markdown_combiner import (
    add_geometry_package,
    combine_markdown,
    normalize_md,
)
from gitbook_worker.tools.publishing.preprocess_md import process
from gitbook_worker.tools.publishing.gitbook_style import (
    DEFAULT_MANUAL_MARKER,
    SummaryContext,
    ensure_clean_summary,
    get_summary_layout,
)
from gitbook_worker.tools.publishing.emoji_report import emoji_report

# ------------------------------- Utils ------------------------------------- #

logger = get_logger(__name__)


_BANNED_FONT_PATTERNS: Tuple[str, ...] = (
    "notosanscjk",
    "notoserifcjk",
    "notosansjp",
    "notoserifjp",
    "notosanskr",
    "notoserifkr",
    "notosanssc",
    "notoserifsc",
    "notosanstc",
    "notoseriftc",
    "notosanshk",
    "notoserifhk",
    "sourcehansans",
    "sourcehanserif",
)

_SVG_DIR_CACHE: set[str] = set()
_SVG_CONVERSION_WARNED = False
_SVG_PDF_ENV_FLAG = "GITBOOK_SVG_PDF_AVAILABLE"


def _purge_disallowed_fonts(
    patterns: Sequence[str] = _BANNED_FONT_PATTERNS,
) -> List[Path]:
    """Remove fonts that violate repository licensing constraints.

    The ERDA publication intentionally avoids bundling Google's Noto CJK fonts
    because they are not available under CC-BY 4.0. When the local publishing
    pipeline installs LaTeX tooling via ``apt``, some distributions try to pull
    in those fonts as optional extras. This helper deletes the unwanted files so
    the build relies on the custom ERDA CC-BY CJK fallback instead.
    """

    removed: List[Path] = []
    lowered = tuple(pattern.lower() for pattern in patterns if pattern)
    if not lowered:
        return removed

    font_roots = (
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
        Path.home() / ".local" / "share" / "fonts",
    )

    for root in font_roots:
        if not root.exists():
            continue
        try:
            candidates = list(root.rglob("*"))
        except OSError as exc:  # pragma: no cover - best effort cleanup
            logger.debug("Font-Suche in %s übersprungen: %s", root, exc)
            continue
        for candidate in candidates:
            if not candidate.is_file():
                continue
            if candidate.suffix.lower() not in {".ttf", ".otf"}:
                continue
            name = candidate.name.lower()
            if not any(pattern in name for pattern in lowered):
                continue
            try:
                candidate.unlink()
            except OSError as exc:  # pragma: no cover - best effort cleanup
                logger.warning(
                    "Konnte unerlaubte Schrift %s nicht entfernen: %s",
                    candidate,
                    exc,
                )
            else:
                removed.append(candidate)

    if removed:
        logger.info(
            "Entfernte %d nicht CC-BY-konforme Noto/Source Han Schriftdateien.",
            len(removed),
        )
    return removed


_TRUE_VALUES = {"1", "true", "yes", "on", "y"}

_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?$"
)
_MANIFEST_VERSION_MIN = (0, 1, 0)
_MANIFEST_VERSION_CURRENT = (0, 1, 0)


# Helper function to resolve paths relative to this module's directory
def _resolve_module_path(relative_path: str) -> str:
    """Resolve a path relative to the publisher module directory.

    This makes the package portable and independent of repository structure.
    lua/ and texmf/ directories are part of the tools.publishing package.

    Args:
        relative_path: Path relative to publisher.py directory (e.g., 'lua/filter.lua')

    Returns:
        Absolute path as string
    """
    module_dir = Path(__file__).resolve().parent
    return str((module_dir / relative_path).resolve())


_DEFAULT_LUA_FILTERS: List[str] = [
    _resolve_module_path("lua/image-path-resolver.lua"),
    _resolve_module_path("lua/emoji-span.lua"),
    _resolve_module_path("lua/latex-emoji.lua"),
]
_DEFAULT_HEADER_PATH = _resolve_module_path("texmf/tex/latex/local/deeptex.sty")
_DEFAULT_METADATA: Dict[str, List[str]] = {
    "color": ["true"],
}


class ProjectMetadataError(RuntimeError):
    """Raised when required project metadata is missing."""


@dataclass(frozen=True)
class ProjectMetadata:
    """Container for project-level metadata used across builds."""

    name: str
    authors: tuple[str, ...]
    license: str | None
    date: str | None = None
    policy: str = "fail"
    warnings: tuple[str, ...] = ()

    def as_pandoc_metadata(
        self, *, title_override: Optional[str] = None
    ) -> Dict[str, Sequence[str] | str]:
        metadata: Dict[str, Sequence[str] | str] = {}
        if title_override:
            metadata["title"] = [title_override]
        if self.authors:
            metadata["author"] = list(self.authors)
        if self.license:
            metadata["rights"] = [self.license]
        if self.date:
            metadata["date"] = [self.date]
        return metadata


def _get_default_variables() -> Dict[str, str]:
    """Get default Pandoc variables with font names from configuration.

    Returns:
        Dictionary of default Pandoc variables
    """
    try:
        font_config = get_font_config()
        default_fonts = font_config.get_default_fonts()
        # Get fallback font names for mainfontfallback
        cjk_font_name = font_config.get_font_name("CJK")
        indic_font_name = font_config.get_font_name("INDIC")
        ethiopic_font_name = font_config.get_font_name("ETHIOPIC")
    except Exception as e:
        logger.warning(
            "Konnte Font-Konfiguration nicht laden: %s. Verwende Fallback-Fonts.", e
        )
        default_fonts = {
            "serif": "DejaVu Serif",
            "sans": "DejaVu Sans",
            "mono": "DejaVu Sans Mono",
        }
        cjk_font_name = None

    variables = {
        "mainfont": default_fonts["serif"],
        "sansfont": default_fonts["sans"],
        "monofont": default_fonts["mono"],
        "geometry": "margin=1in",
        "longtable": "true",
        "max-list-depth": "9",
    }

    # Add CC BY fallback chain if available
    fallback_chain = [
        name for name in [cjk_font_name, indic_font_name, ethiopic_font_name] if name
    ]
    if fallback_chain:
        variables["mainfontfallback"] = "; ".join(
            f"{name}:mode=harf" for name in fallback_chain
        )

    return variables


# Initialize default variables from configuration
_DEFAULT_VARIABLES: Dict[str, str] = _get_default_variables()

_DEFAULT_EXTRA_ARGS: Tuple[str, ...] = ()

EMOJI_RANGES = (
    "1F300-1F5FF, 1F600-1F64F, 1F680-1F6FF, 1F700-1F77F, 1F780-1F7FF, "
    "1F800-1F8FF, 1F900-1F9FF, 1FA00-1FA6F, 1FA70-1FAFF, "
    "2600-26FF, 2700-27BF, 2300-23FF, 2B50, 2B06, 2934-2935, 25A0-25FF"
)


@dataclass(frozen=True)
class EmojiOptions:
    """Runtime configuration for emoji handling in Pandoc runs."""

    color: bool = True
    report: bool = False
    report_dir: Optional[Path] = None
    bxcoloremoji: Optional[bool] = None


@dataclass(frozen=True)
class FontSpec:
    """Describe a custom font provided via the publish manifest."""

    name: Optional[str]
    path: Optional[Path]
    url: Optional[str]


_ADDITIONAL_FONT_DIRS: List[Path] = []


def _user_font_directories() -> List[Path]:
    """Return OS-specific font directories where we place/register fonts."""

    dirs: List[Path] = []
    if sys.platform == "win32":
        local_appdata = Path(os.environ.get("LOCALAPPDATA", ""))
        if not local_appdata:
            local_appdata = Path.home() / "AppData" / "Local"
        dirs.append(local_appdata / "Microsoft" / "Windows" / "Fonts")
    elif sys.platform == "darwin":
        dirs.append(Path.home() / "Library" / "Fonts")
    else:
        dirs.append(Path.home() / ".local" / "share" / "fonts")

    # Always include the POSIX-style fonts dir as a fallback (used in CI containers)
    fallback = Path.home() / ".local" / "share" / "fonts"
    if fallback not in dirs:
        dirs.append(fallback)

    return dirs


def _configure_osfontdir(additional_dirs: Optional[Sequence[Path]] = None) -> None:
    """Ensure OSFONTDIR contains repo/local font directories for LuaLaTeX.

    On Windows a temporary ``fonts.conf`` is generated so fontconfig picks up
    repo fonts (including those declared only in ``fonts.yml`` like ERDA CJK).
    """

    new_dirs: List[str] = []
    entries = list(_user_font_directories())
    repo_root = _resolve_repo_root()
    entries.append(repo_root / ".github" / "fonts")
    entries.append(repo_root / "fonts-storage")
    if additional_dirs:
        entries.extend(additional_dirs)

    for directory in entries + _ADDITIONAL_FONT_DIRS:
        if not directory:
            continue
        try:
            resolved = Path(directory).resolve()
        except (OSError, RuntimeError):
            resolved = Path(directory)
        if resolved.exists():
            new_dirs.append(str(resolved))

    if not new_dirs:
        return

    separator = os.pathsep
    existing = os.environ.get("OSFONTDIR", "")
    merged: List[str] = []
    if existing:
        merged.extend([entry for entry in existing.split(separator) if entry])

    for path_str in new_dirs:
        if path_str not in merged:
            merged.append(path_str)

    os.environ["OSFONTDIR"] = separator.join(merged)
    logger.info("ℹ OSFONTDIR aktualisiert (%d Pfade)", len(merged))
    logger.debug("OSFONTDIR Inhalte: %s", os.environ["OSFONTDIR"])

    # On Windows, generate a dynamic fontconfig file that mirrors OSFONTDIR
    # so fc-list/luaotfload can discover fonts stored in the repo (e.g., ERDA CJK).
    if sys.platform == "win32":
        try:
            cache_dir = Path.home() / ".cache" / "erda-publisher" / "fontconfig"
            cache_dir.mkdir(parents=True, exist_ok=True)
            conf_path = cache_dir / "fonts.conf"

            dir_entries = []
            for path_str in merged:
                escaped = (
                    path_str.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                dir_entries.append(f"  <dir>{escaped}</dir>")

            conf_contents = "\n".join(
                [
                    '<?xml version="1.0"?>',
                    '<!DOCTYPE fontconfig SYSTEM "fonts.dtd">',
                    "<fontconfig>",
                    *dir_entries,
                    "  <rescan><int>30</int></rescan>",
                    "</fontconfig>",
                    "",
                ]
            )

            conf_path.write_text(conf_contents, encoding="utf-8")
            os.environ["FONTCONFIG_FILE"] = str(conf_path)
            logger.info("✓ FONTCONFIG_FILE set to %s (dynamic)", conf_path)
        except Exception as exc:
            logger.warning(
                "⚠ Konnte dynamische FONTCONFIG_FILE nicht schreiben: %s", exc
            )
            fallback_conf = repo_root / "fonts-storage" / "fonts.conf"
            if fallback_conf.exists():
                os.environ["FONTCONFIG_FILE"] = str(fallback_conf.resolve())
                logger.info("✓ FONTCONFIG_FILE fallback to %s", fallback_conf)


def _configure_texmf_cache(manifest_path: Optional[Path]) -> None:
    """Place TeX/luaotfload caches in a repo-local directory (optionally per language).

    This keeps font caches reproducible and avoids polluting global user caches.

    NOTE: LUAOTFLOAD_CACHE is intentionally NOT set to repo-local directory because
    luaotfload-tool --update does not respect this variable and updates the system
    cache instead. This causes a mismatch where CLI tools see fonts but LuaTeX runtime
    cannot find them. We only set TEXMFVAR/TEXMFCONFIG for TeX itself.
    """

    repo_root = _resolve_repo_root()
    lang_hint = None
    if manifest_path:
        try:
            lang_hint = manifest_path.parent.name
        except Exception:
            lang_hint = None

    cache_root = repo_root / ".texmf-cache"
    if lang_hint:
        cache_root = cache_root / lang_hint

    texmf_var = cache_root / "texmf-var"
    texmf_config = cache_root / "texmf-config"

    for path in (texmf_var, texmf_config):
        path.mkdir(parents=True, exist_ok=True)

    # Keep TeX/luaotfload caches local for reproducibility (TEXMFVAR is the
    # canonical base; TEXMFCACHE is used by TeX but NOT for luaotfload font database).
    os.environ["TEXMFVAR"] = str(texmf_var)
    os.environ["TEXMFCONFIG"] = str(texmf_config)
    # TEXMFCACHE removed - luaotfload needs system cache to find fonts
    # os.environ["TEXMFCACHE"] = str(texmf_var / "luatex-cache")
    # LUAOTFLOAD_CACHE removed - let luaotfload use system cache so CLI and runtime agree

    logger.info("ℹ TEXMFVAR gesetzt: %s", texmf_var)
    logger.info("ℹ TEXMFCONFIG gesetzt: %s", texmf_config)
    logger.info("ℹ TEXMFCACHE: using system default (not overridden)")
    logger.info("ℹ LUAOTFLOAD_CACHE: using system default (not overridden)")


def _resolve_repo_root() -> Path:
    """Return the repository root for the current checkout."""

    current = Path(__file__).resolve()
    parents = list(current.parents)
    for candidate in parents:
        if (candidate / ".git").is_dir():
            return candidate
        if (candidate / "publish.yml").exists() or (
            candidate / "publish.yaml"
        ).exists():
            return candidate
        if (candidate / "book.json").exists():
            return candidate
    return parents[-1]


def _as_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in _TRUE_VALUES
    return default


def _run(
    cmd: List[str],
    check: bool = True,
    env: Optional[Dict[str, str]] = None,
    **kwargs: Any,
) -> subprocess.CompletedProcess:
    run_kwargs: Dict[str, Any] = {
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",  # Replace problematic bytes instead of crashing
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
    }

    if env:
        run_kwargs["env"] = {**os.environ, **env}

    # Allow callers to override defaults (e.g. timeout, capture_output)
    if "capture_output" in kwargs:
        # capture_output=True conflicts with explicit stdout/stderr pipes
        if kwargs.get("capture_output"):
            run_kwargs.pop("stdout", None)
            run_kwargs.pop("stderr", None)
        # Merge after the cleanup so caller-provided pipes win if set
    run_kwargs.update(kwargs)

    logger.info("Run Command → %s", " ".join(cmd))
    cp = subprocess.run(cmd, **run_kwargs)
    if cp.stdout:
        logger.info(cp.stdout)
    if cp.stderr:
        logger.error(cp.stderr)
    if check and cp.returncode != 0:
        # Include stdout/stderr in the exception so error handlers can access them
        raise subprocess.CalledProcessError(
            cp.returncode, cmd, output=cp.stdout, stderr=cp.stderr
        )
    return cp


def _escape_latex(value: str) -> str:
    """Escape common LaTeX special characters in a string used in -V title=...

    This is a conservative escape for values injected into LaTeX via Pandoc
    variables (e.g. title). We escape the characters that commonly break
    LaTeX alignment or maths: & % $ # _ { } and backslash. We keep the
    result simple (use standard TeX escapes) so Pandoc forwards a safe value
    into the PDF engine.
    """
    if not value:
        return value

    # Replace backslash first
    esc = value.replace("\\", "\\textbackslash{}")

    # Escape LaTeX special characters
    # NOTE: Use regular strings (not raw strings r"...") to ensure single backslash
    # in output. r"\\&" would produce \\& (double backslash), but we need \& (single).
    replacements = {
        "&": "\\&",
        "%": "\\%",
        "$": "\\$",
        "#": "\\#",
        "_": "\\_",
        "{": "\\{",
        "}": "\\}",
    }

    for k, v in replacements.items():
        esc = esc.replace(k, v)

    return esc


def _which(name: str) -> Optional[str]:
    return shutil.which(name)


def _is_debian_like() -> bool:
    return pathlib.Path("/etc/debian_version").exists()


def _clear_lualatex_caches() -> None:
    """Clear LuaLaTeX font caches to force reload of updated fonts.

    LuaLaTeX caches fonts separately from fontconfig, so updating fonts
    via fc-cache alone is insufficient. This function removes the LuaTeX
    font cache directories to ensure the PDF engine picks up font changes.
    """
    cache_locations = [
        Path.home() / ".texlive2023" / "texmf-var" / "luatex-cache",
        Path.home() / ".texlive2024" / "texmf-var" / "luatex-cache",
        Path.home() / ".texlive2025" / "texmf-var" / "luatex-cache",
        Path("/var/lib/texmf/luatex-cache"),
    ]

    cleared_count = 0
    for cache_dir in cache_locations:
        if not cache_dir.exists():
            continue
        try:
            shutil.rmtree(cache_dir, ignore_errors=True)
            logger.info("✓ LuaLaTeX Cache gelöscht: %s", cache_dir)
            cleared_count += 1
        except Exception as exc:
            logger.warning(
                "⚠ Konnte LuaLaTeX Cache nicht löschen (%s): %s", cache_dir, exc
            )

    if cleared_count > 0:
        logger.info("ℹ %d LuaLaTeX Cache-Verzeichnisse gelöscht", cleared_count)
    else:
        logger.debug("ℹ Keine LuaLaTeX Cache-Verzeichnisse gefunden")


def _check_fontconfig_has_font(font_name: str) -> bool:
    """Check if fontconfig cache knows about this font.

    Args:
        font_name: Font family name (e.g., "Twemoji Mozilla")

    Returns:
        True if font is in fontconfig cache, False otherwise
    """
    fc_list = _which("fc-list")
    if not fc_list:
        logger.debug("fc-list nicht verfügbar - kann fontconfig nicht prüfen")
        return False

    try:
        result = _run(
            [fc_list, ":", "family", "--format", "%{family}\n"],
            capture_output=True,
            text=True,
            check=False,
        )
        target = _normalize_font_name(font_name)
        for line in (result.stdout or "").splitlines():
            if target in _normalize_font_name(line):
                return True
        return False
    except Exception as exc:
        logger.debug("fc-list check fehlgeschlagen: %s", exc)
        return False


def _check_luaotfload_has_font(font_name: str) -> bool:
    """Check if LuaTeX font database knows about this font.

    Args:
        font_name: Font family name (e.g., "Twemoji Mozilla")

    Returns:
        True if font is in LuaTeX cache, False otherwise
    """
    tool = _which("luaotfload-tool") or _which("luaotfload-tool.exe")
    if not tool:
        logger.debug("luaotfload-tool nicht verfügbar - kann LuaTeX cache nicht prüfen")
        return False

    try:
        result = _run(
            [tool, "--find", font_name],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        # Returns font path if found, empty if not
        return bool(result.stdout.strip())
    except Exception as exc:
        logger.debug("luaotfload-tool check fehlgeschlagen: %s", exc)
        return False


def _fonts_need_cache_update() -> bool:
    """Check if any configured font is missing from font caches.

    Returns:
        True if font caches need updating, False if all fonts are cached
    """
    try:
        logger.info("ℹ Prüfe Schriftarten in Font-Caches...")
        font_config = get_font_config()

        # Check critical fonts that must be in cache for PDF generation
        critical_fonts = ["EMOJI", "CJK", "SERIF", "SANS", "MONO"]

        for key in critical_fonts:
            try:
                font = font_config.get_font(key)
                if not font:
                    continue

                # Check fontconfig cache
                if not _check_fontconfig_has_font(font.name):
                    logger.info(
                        "🔍 Font '%s' nicht in fontconfig cache - Update erforderlich",
                        font.name,
                    )
                    return True

                # Check LuaTeX cache (critical for PDF generation)
                if not _check_luaotfload_has_font(font.name):
                    logger.info(
                        "🔍 Font '%s' nicht in LuaTeX cache - Update erforderlich",
                        font.name,
                    )
                    return True
            except Exception as exc:
                logger.debug("Fehler beim Prüfen von Font %s: %s", key, exc)
                continue

        logger.info("✓ Alle konfigurierten Fonts in Caches - Update nicht nötig")
        return False
    except Exception as exc:
        logger.warning("Cache-Check fehlgeschlagen (%s) - führe Update durch", exc)
        return True


def _update_luaotfload_database() -> None:
    """Refresh luaotfload font database so LuaLaTeX sees new fonts."""

    tool = _which("luaotfload-tool") or _which("luaotfload-tool.exe")
    if not tool:
        logger.debug("luaotfload-tool nicht gefunden – überspringe Update")
        return

    logger.info("🔄 Aktualisiere luaotfload Font-Datenbank ...")
    try:
        _run([tool, "--update", "--quiet"], check=False)
    except Exception as exc:  # pragma: no cover - best effort only
        logger.warning("luaotfload-tool --update fehlgeschlagen: %s", exc)


def _ensure_dir(path: str) -> None:
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def _coerce_sequence(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        raise TypeError("Mappings können nicht als Sequenz interpretiert werden.")
    try:
        return [str(item) for item in value]
    except TypeError:
        return [str(value)]


def _merge_sequence(base: Sequence[str], override: Any) -> Tuple[str, ...]:
    values = list(base)
    if override is None:
        return tuple(values)
    if isinstance(override, Mapping):
        if "replace" in override:
            return tuple(_coerce_sequence(override.get("replace")))
        if "prepend" in override:
            values = _coerce_sequence(override.get("prepend")) + values
        if "append" in override:
            values.extend(_coerce_sequence(override.get("append")))
        if "remove" in override:
            removals = set(_coerce_sequence(override.get("remove")))
            values = [item for item in values if item not in removals]
        return tuple(values)
    return tuple(_coerce_sequence(override))


def _merge_metadata(
    base: Dict[str, Sequence[str]], override: Any
) -> Dict[str, Tuple[str, ...]]:
    result: Dict[str, Tuple[str, ...]] = {
        key: tuple(values) for key, values in base.items()
    }
    if not override:
        return result
    if not isinstance(override, Mapping):
        logger.warning("Pandoc-Metadaten-Override muss ein Mapping sein.")
        return result
    replace_block = override.get("replace")
    if isinstance(replace_block, Mapping):
        result = {
            str(key): tuple(_coerce_sequence(value))
            for key, value in replace_block.items()
        }
    for key, value in override.items():
        if key == "replace":
            continue
        if value is None:
            result.pop(str(key), None)
            continue
        if isinstance(value, Mapping):
            try:
                result[str(key)] = _merge_sequence(result.get(str(key), tuple()), value)
            except TypeError as exc:
                logger.warning(
                    "Pandoc-Metadaten-Override für %s konnte nicht angewendet werden: %s",
                    key,
                    exc,
                )
            continue
        try:
            result[str(key)] = tuple(_coerce_sequence(value))
        except TypeError as exc:
            logger.warning(
                "Pandoc-Metadaten-Override für %s konnte nicht geparst werden: %s",
                key,
                exc,
            )
    return result


def _merge_variables(base: Dict[str, str], override: Any) -> Dict[str, str]:
    result = dict(base)
    if not override:
        return result
    if not isinstance(override, Mapping):
        logger.warning("Pandoc-Variablen-Override muss ein Mapping sein.")
        return result
    replace_block = override.get("replace")
    if isinstance(replace_block, Mapping):
        result = {str(key): str(value) for key, value in replace_block.items()}
    for key, value in override.items():
        if key == "replace":
            continue
        if value is None:
            result.pop(str(key), None)
        else:
            if isinstance(value, Mapping):
                logger.warning(
                    "Verschachtelte Variablen-Overrides für %s werden nicht unterstützt.",
                    key,
                )
                continue
            result[str(key)] = str(value)
    return result


def _normalize_font_name(value: str) -> str:
    """Return a normalised version of ``value`` for fuzzy font matching."""

    return re.sub(r"[^a-z0-9]", "", value.lower())


def _font_available(name: str) -> bool:
    """Return ``True`` if fontconfig or local assets can resolve ``name``.

    Checks in order:
    1. fontconfig (fc-list)
    2. fonts.yml configured paths
    3. legacy font directories
    """

    normalized = _normalize_font_name(name)

    # 1. Try fontconfig first
    fc_list = _which("fc-list")
    if fc_list:
        try:
            result = subprocess.run(
                [fc_list, name],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except OSError:
            result = None
        else:
            if result and result.stdout:
                for line in result.stdout.splitlines():
                    if normalized in _normalize_font_name(line):
                        return True

    # 2. Fallback: Check fonts.yml configured paths
    try:
        from gitbook_worker.tools.publishing.font_storage import get_font_config

        font_config = get_font_config()
        # Try to find font entry by name - iterate ALL configured fonts
        for font_key in font_config.fonts.keys():
            try:
                font_entry = font_config.get_font(font_key)
                if font_entry and font_entry.name == name:
                    # Check if any configured path exists
                    for path_str in font_entry.paths:
                        path = Path(path_str)
                        if not path.is_absolute():
                            # Resolve relative paths from repo root
                            repo_root = _resolve_repo_root()
                            path = repo_root / path
                        if path.exists() and path.is_file():
                            logger.debug(
                                "✓ Font '%s' found in fonts.yml path: %s",
                                name,
                                path,
                            )
                            return True
            except Exception:
                # Ignore errors for individual font entries
                continue
    except Exception as exc:
        logger.debug("fonts.yml fallback check failed: %s", exc)

    repo_root = _resolve_repo_root()
    font_dirs = [
        repo_root / ".github" / "gitbook_worker" / "tools" / "publishing" / "fonts",
        repo_root / ".github" / "tools" / "publishing" / "fonts",
        repo_root / ".github" / "fonts",
        Path.home() / ".local" / "share" / "fonts",
    ]
    font_dirs.extend(_ADDITIONAL_FONT_DIRS)
    try:
        for base_dir in font_dirs:
            if not base_dir.exists():
                continue
            for extension in ("*.ttf", "*.otf"):
                for font_file in base_dir.rglob(extension):
                    stem = _normalize_font_name(font_file.stem)
                    if stem and (normalized in stem or stem in normalized):
                        return True
    except OSError:
        pass
    return False


@lru_cache(maxsize=1)
def _locate_bxcoloremoji() -> Optional[str]:
    """Return the path to ``bxcoloremoji.sty`` if kpsewhich can resolve it."""

    kpsewhich = shutil.which("kpsewhich")
    if not kpsewhich:
        logger.warning(
            "⚠ kpsewhich nicht gefunden – automatische bxcoloremoji-Erkennung deaktiviert."
        )
        return None

    try:
        result = subprocess.run(
            [kpsewhich, "bxcoloremoji.sty"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError as exc:
        logger.warning("⚠ kpsewhich-Aufruf für bxcoloremoji fehlgeschlagen: %s", exc)
        return None

    lines = [
        line.strip() for line in (result.stdout or "").splitlines() if line.strip()
    ]
    if result.returncode != 0 or not lines:
        if result.stderr:
            logger.debug("kpsewhich stderr: %s", result.stderr.strip())
        logger.info(
            "ℹ bxcoloremoji.sty konnte nicht gefunden werden (rc=%s).",
            result.returncode,
        )
        return None

    path = lines[-1]
    logger.info("ℹ bxcoloremoji.sty gefunden: %s", path)
    return path


def _require_bxcoloremoji() -> str:
    """Ensure bxcoloremoji is available and raise a helpful error otherwise."""

    path = _locate_bxcoloremoji()
    if path:
        return path
    message = (
        "bxcoloremoji.sty wurde nicht gefunden. Installiere das TeX-Paket "
        "'bxcoloremoji' (tlmgr install bxcoloremoji) oder deaktiviere --emoji-bxcoloremoji."
    )
    logger.error(message)
    raise RuntimeError(message)


def _decide_bxcoloremoji(options: EmojiOptions) -> bool:
    """Decide whether latex-emoji should activate the bxcoloremoji package."""

    # Allow operators to force-disable bxcoloremoji in troublesome environments
    # (e.g. minimal TeX installs) without changing code. Default remains auto-on
    # when the package is available so tests and full builds keep color emoji.
    env_disable = _as_bool(os.environ.get("ERDA_BXCOLOREMOJI_DISABLE"), False)
    if env_disable and options.bxcoloremoji is None:
        logger.info("ℹ bxcoloremoji disabled via ERDA_BXCOLOREMOJI_DISABLE env var.")
        return False

    if options.bxcoloremoji is True:
        path = _require_bxcoloremoji()
        logger.info("ℹ bxcoloremoji per Konfiguration erzwungen (%s).", path)
        return True

    if options.bxcoloremoji is False:
        logger.info("ℹ bxcoloremoji explizit deaktiviert.")
        return False

    if not options.color:
        logger.info(
            "ℹ bxcoloremoji deaktiviert, da emoji_color=False (kein Bedarf an Farbglyphen)."
        )
        return False

    path = _locate_bxcoloremoji()
    if path:
        logger.info("ℹ bxcoloremoji automatisch aktiviert (%s).", path)
        return True

    logger.warning(
        "⚠ bxcoloremoji nicht verfügbar – verwende Lua-Fallback für Emoji-Fonts."
    )
    return False


def _remember_font_dir(path: Path) -> None:
    """Track additional font directories for discovery fallbacks."""

    global _ADDITIONAL_FONT_DIRS

    try:
        resolved = path.resolve()
    except FileNotFoundError:
        resolved = path
    if resolved in _ADDITIONAL_FONT_DIRS:
        return
    _ADDITIONAL_FONT_DIRS.append(resolved)


def _parse_font_specs(raw: Any, manifest_dir: Optional[Path]) -> List[FontSpec]:
    """Normalise ``fonts`` manifest entries into :class:`FontSpec` objects."""

    if not isinstance(raw, list):
        return []

    specs: List[FontSpec] = []

    for entry in raw:
        name: Optional[str] = None
        path_value: Optional[Path] = None
        url_value: Optional[str] = None

        if isinstance(entry, Mapping):
            raw_name = entry.get("name")
            if isinstance(raw_name, str):
                stripped = raw_name.strip()
                name = stripped or None

            raw_path = entry.get("path")
            if raw_path:
                candidate = Path(str(raw_path))
                if not candidate.is_absolute() and manifest_dir:
                    candidate = (manifest_dir / candidate).resolve()
                path_value = candidate

            raw_url = entry.get("url")
            if isinstance(raw_url, str):
                stripped_url = raw_url.strip()
                url_value = stripped_url or None
        else:
            candidate = Path(str(entry))
            if not candidate.is_absolute() and manifest_dir:
                candidate = (manifest_dir / candidate).resolve()
            path_value = candidate

        if not path_value and not url_value:
            continue

        specs.append(FontSpec(name=name, path=path_value, url=url_value))

    return specs


@lru_cache(maxsize=1)
def _get_pandoc_version() -> Tuple[int, ...]:
    """Return the installed Pandoc version as a tuple or ``()`` if unknown."""
    pandoc = _which("pandoc")
    if not pandoc:
        return ()
    try:
        result = subprocess.run(
            [pandoc, "--version"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError:
        return ()
    if result.returncode != 0 or not result.stdout:
        return ()
    first_line = result.stdout.splitlines()[0]
    match = re.search(r"pandoc\s+([0-9]+(?:\.[0-9]+)*)", first_line)
    if not match:
        return ()
    return tuple(int(part) for part in match.group(1).split("."))


def _needs_harfbuzz(font_name: str) -> bool:
    """Return ``True`` if ``font_name`` requires HarfBuzz rendering."""

    lowered = font_name.lower()
    return "color" in lowered or "segoe ui emoji" in lowered


def _select_emoji_font(prefer_color: bool) -> Tuple[Optional[str], bool]:
    """Select the best available emoji font from font_config.yml.

    Returns a tuple ``(font_name, needs_harfbuzz)`` describing the selected
    font and whether HarfBuzz rendering should be enabled for it.

    Uses font_config.yml EMOJI entry as source of truth (AGENTS.md compliant).
    """

    logger.info(
        "🔍 FONT-STACK: _select_emoji_font() aufgerufen (prefer_color=%s)", prefer_color
    )
    try:
        font_config = get_font_config()
        emoji_font_name = font_config.get_font_name("EMOJI")
        logger.info("🔍 FONT-STACK: fonts.yml EMOJI entry name: %s", emoji_font_name)
        if not emoji_font_name:
            raise RuntimeError("EMOJI font not configured in fonts.yml")

        # Try fontconfig family name first (e.g., "Twemoji Mozilla")
        logger.info("🔍 FONT-STACK: Prüfe Verfügbarkeit von '%s'", emoji_font_name)
        if _font_available(emoji_font_name):
            needs_hb = _needs_harfbuzz(emoji_font_name)
            logger.info(
                "✅ FONT-STACK: Emoji-Font gewählt: '%s' (needs_harfbuzz=%s)",
                emoji_font_name,
                needs_hb,
            )
            return emoji_font_name, needs_hb

        # Fallback: Try "Twemoji Color Font" alias (fonts.yml name field)
        emoji_config = font_config.get_font("EMOJI")
        if emoji_config and emoji_config.name != emoji_font_name:
            logger.info(
                "🔍 FONT-STACK: Primärer Name nicht verfügbar, prüfe Alias: '%s'",
                emoji_config.name,
            )
            if _font_available(emoji_config.name):
                needs_hb = _needs_harfbuzz(emoji_config.name)
                logger.info(
                    "✅ FONT-STACK: Emoji-Font gewählt (alias): '%s' (needs_harfbuzz=%s)",
                    emoji_config.name,
                    needs_hb,
                )
                return emoji_config.name, needs_hb

        # DESIGN DECISION: No hardcoded fallbacks allowed!
        # All fonts must be explicitly configured in fonts.yml to ensure:
        # - License compliance (CC-BY, MIT, etc.)
        # - Attribution requirements can be fulfilled
        # - Reproducible builds across environments
        # Using unconfigured system fonts would violate these principles.
        message = f"❌ Emoji font '{emoji_font_name}' not found – please install configured fonts or update Docker image"
        logger.error(message)
        raise RuntimeError(
            f"Emoji font '{emoji_font_name}' is not available. "
            "No hardcoded fallbacks allowed - all fonts must be configured in fonts.yml for license compliance. "
            "Run 'fc-list | grep -i emoji' inside the container and rebuild the Docker image if necessary."
        )
    except Exception as exc:
        logger.error("Emoji-Font-Auswahl fehlgeschlagen: %s", exc)
        raise


def _lua_escape_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _lua_fallback_block(spec: str) -> Optional[str]:
    """Generate Lua table literal for luaotfload.add_fallback() with full fontspec strings."""
    entries = [chunk.strip() for chunk in re.split(r"[;,]", spec) if chunk.strip()]
    if not entries:
        return None
    # Build table literal with full fontspec strings (including features like :mode=harf)
    escaped_entries = [
        entry.replace("\\", "\\\\").replace('"', '\\"') for entry in entries
    ]
    # Return as Lua table literal: {"Font1:features", "Font2:features", ...}
    return "{" + ", ".join(f'"{e}"' for e in escaped_entries) + "}"


def _normalize_fallback_spec(
    spec: str, *, primary_font: Optional[str], needs_harfbuzz: bool
) -> str:
    logger.info("🔍 FONT-STACK: _normalize_fallback_spec() aufgerufen")
    logger.info("🔍 FONT-STACK:   Input spec: %s", spec)
    logger.info("🔍 FONT-STACK:   Primary font: %s", primary_font)
    logger.info("🔍 FONT-STACK:   Needs HarfBuzz: %s", needs_harfbuzz)
    entries: List[str] = []
    seen: set[str] = set()
    primary_normalized = _normalize_font_name(primary_font) if primary_font else None

    for chunk in re.split(r"[;,]", spec):
        entry = chunk.strip()
        if not entry:
            continue
        base = entry.split(":", 1)[0].strip()
        if not base:
            continue
        if not (_check_luaotfload_has_font(base) or _font_available(base)):
            logger.info(
                "🔍 FONT-STACK: Fallback-Font nicht verfügbar (wird im Lua-Filter herausgefiltert): %s",
                base,
            )
        normalized = _normalize_font_name(base)
        if normalized in seen:
            continue
        if needs_harfbuzz and (normalized == primary_normalized):
            if ":mode=" not in entry.lower():
                entry = f"{entry}:mode=harf"
        entries.append(entry)
        seen.add(normalized)

    # Add SANS font from font_config as final fallback (AGENTS.md compliant)
    try:
        font_config = get_font_config()
        sans_font_name = font_config.get_font_name("SANS", "DejaVu Sans")
        logger.info("🔍 FONT-STACK: Füge SANS-Fallback hinzu: %s", sans_font_name)
        sans_normalized = _normalize_font_name(sans_font_name)
        if sans_normalized not in seen:
            entries.append(f"{sans_font_name}:mode=harf")
            seen.add(sans_normalized)
    except Exception as exc:
        logger.debug("Konnte SANS-Fallback nicht aus font_config laden: %s", exc)
        # Absolute last resort
        if _normalize_font_name("DejaVu Sans") not in seen:
            logger.warning("🔍 FONT-STACK: Verwende DejaVu Sans als letzten Fallback")
            entries.append("DejaVu Sans:mode=harf")

    final_spec = "; ".join(entries)
    logger.info("✅ FONT-STACK: Normalisierte Fallback-Spec: %s", final_spec)
    return final_spec


def _build_font_header(
    *,
    main_font: str,
    sans_font: str,
    mono_font: str,
    emoji_font: Optional[str],
    include_mainfont: bool,
    needs_harfbuzz: bool,
    manual_fallback_spec: Optional[str],
    abort_if_missing_glyph: bool,
    temp_dir: str,
) -> str:
    """Render a Pandoc header snippet configuring fonts and fallbacks."""

    logger.info("📄 FONT-STACK: _build_font_header() aufgerufen (FINAL FONT CHOICES)")
    logger.info("📄 FONT-STACK:   main_font = %s", main_font)
    logger.info("📄 FONT-STACK:   sans_font = %s", sans_font)
    logger.info("📄 FONT-STACK:   mono_font = %s", mono_font)
    logger.info("📄 FONT-STACK:   emoji_font = %s", emoji_font)
    logger.info("📄 FONT-STACK:   needs_harfbuzz = %s", needs_harfbuzz)
    logger.info("📄 FONT-STACK:   manual_fallback_spec = %s", manual_fallback_spec)
    logger.info("📄 FONT-STACK:   include_mainfont = %s", include_mainfont)

    lines = ["\\newcommand{\\fallbackfeature}{}"]

    # Step 1: Collect available fallbacks
    available_fallbacks: List[str] = []
    missing_fallbacks: List[str] = []
    lua_cache_misses: List[str] = []
    if manual_fallback_spec:
        for chunk in re.split(r"[;,]", manual_fallback_spec):
            entry = chunk.strip()
            if not entry:
                continue
            base = entry.split(":", 1)[0].strip()
            if not base:
                continue

            # Only treat a fallback as usable when luaotfload already knows it.
            # This prevents us from emitting TeX headers that later fail at
            # runtime when fonts are merely present on disk but not registered
            # in LuaTeX caches (the current Windows issue).
            if _check_luaotfload_has_font(base):
                available_fallbacks.append(entry)
                continue

            if _font_available(base):
                lua_cache_misses.append(base)
            else:
                missing_fallbacks.append(base)

    if manual_fallback_spec and missing_fallbacks:
        logger.warning(
            "⚠️ FONT-STACK: Fallback-Fonts fehlen und werden übersprungen: %s",
            "; ".join(sorted(set(missing_fallbacks))),
        )

    if manual_fallback_spec and not available_fallbacks:
        cause_parts: List[str] = []
        if lua_cache_misses:
            cause_parts.append(
                "LuaTeX cache fehlt: "
                + "; ".join(sorted(set(lua_cache_misses)))
                + " (luaotfload-tool --update --force)"
            )
        if missing_fallbacks:
            cause_parts.append(
                "nicht gefunden: " + "; ".join(sorted(set(missing_fallbacks)))
            )

        msg = "Keine der konfigurierten Fallback-Fonts ist verfügbar" + (
            ": " + "; ".join(cause_parts) if cause_parts else ""
        )
        logger.error("❌ FONT-STACK: %s", msg)
        raise RuntimeError(msg)

    fallback_block = (
        _lua_fallback_block(";".join(available_fallbacks))
        if available_fallbacks
        else None
    )

    lua_fallback_flag = os.getenv("ERDA_ENABLE_LUA_FALLBACK", "1").lower()
    enable_lua_fallback = bool(fallback_block) and lua_fallback_flag not in {
        "0",
        "false",
        "no",
        "off",
    }

    if enable_lua_fallback and platform.system().lower() == "windows":
        # Historically disabled due to luaotfload issues; we now enable by default to
        # meet the cross-platform requirement (Win/macOS/Linux/Docker). Users can still
        # opt-out via ERDA_ENABLE_LUA_FALLBACK=0/off.
        logger.info(
            "⚠️ FONT-STACK: Lua fallback auf Windows aktiv (deaktivieren mit ERDA_ENABLE_LUA_FALLBACK=0)"
        )

    # Store lua_fallback_code for insertion AFTER font setup
    lua_fallback_code: Optional[str] = None
    if enable_lua_fallback and fallback_block:
        logger.info(f"DEBUG: fallback_block (table literal) = {repr(fallback_block)}")
        # Build inline Lua code WITHOUT \AtBeginDocument wrapper!
        # CRITICAL: Matching working commit 28a21cf5 (Nov 29) - simple direct call
        lua_fallback_code = (
            f"\\directlua{{luaotfload.add_fallback('mainfont', {fallback_block})}}"
        )

    if not enable_lua_fallback and fallback_block:
        logger.info(
            "⚠️ FONT-STACK: Lua fallback deaktiviert (set ERDA_ENABLE_LUA_FALLBACK=0 to disable explicitly)"
        )

    # Detect unresolved glyphs after fallback and optionally abort; skip when
    # lua fallback is disabled (e.g., on Windows) to avoid TeX header churn.
    detector_env = os.getenv("ERDA_ENABLE_MISSING_GLYPH_DETECTOR", "0").lower()
    detector_requested = detector_env not in {"0", "false", "no", "off"}
    enable_missing_detector = enable_lua_fallback and detector_requested

    if enable_missing_detector:
        abort_flag = "true" if abort_if_missing_glyph else "false"
        lines.append(
            "\\AtBeginDocument{"
            "\\directlua{"
            f"texio.write_nl('term and log', '*** GBW: Missing glyph detector initialized (abort={abort_flag})');"
            "gbw_missing_glyphs = gbw_missing_glyphs or {};"
            "local function gbw_font_name(fid)"
            "  local f = font.getfont(fid);"
            "  if not f then return tostring(fid) end;"
            "  return f.fullname or f.psname or f.name or tostring(fid);"
            "end;"
            "local function gbw_note_missing(fid, cp)"
            "  local entry = gbw_missing_glyphs[cp];"
            "  if not entry then entry = {fonts={}}; gbw_missing_glyphs[cp]=entry end;"
            "  entry.fonts[gbw_font_name(fid)] = true;"
            "  texio.write_nl('term and log', '*** GBW: Noted missing glyph U+'..string.format('%04X', cp)..' in font '..gbw_font_name(fid));"
            "end;"
            "local function gbw_check(head)"
            "  for n in node.traverse_id(node.id('glyph'), head) do"
            "    local fid = n.font; local cp = n.char;"
            "    if fid and cp then"
            "      local ok, has = pcall(font.has_glyph, fid, cp);"
            "      if (not ok) or (not has) then gbw_note_missing(fid, cp) end;"
            "    end"
            "  end;"
            "  return head;"
            "end;"
            "local function gbw_report()"
            "  texio.write_nl('term and log', '*** GBW: gbw_report() called');"
            "  if not gbw_missing_glyphs then texio.write_nl('term and log', '*** GBW: gbw_missing_glyphs is nil'); return end;"
            "  local keys = {}; for cp,_ in pairs(gbw_missing_glyphs) do keys[#keys+1]=cp end;"
            "  table.sort(keys);"
            "  texio.write_nl('term and log', '*** GBW: Found '..#keys..' missing glyph codepoints');"
            "  if #keys==0 then return end;"
            "  texio.write_nl('log', 'gbw missing glyph report ('..#keys..' codepoints)');"
            "  local fb = gbw_fallback_stack;"
            "  if type(fb) == 'table' and next(fb) ~= nil then "
            "    local okc, fb_str = pcall(function() return table.concat(fb, '; ') end);"
            "    if okc and fb_str then texio.write_nl('log', '  fallback stack: '..fb_str) end;"
            "  end;"
            "  local summary_lines = {};"
            "  for _,cp in ipairs(keys) do"
            "    local entry = gbw_missing_glyphs[cp];"
            "    local fonts = {}; for name,_ in pairs(entry.fonts or {}) do fonts[#fonts+1]=name end; table.sort(fonts);"
            "    local char_repr = ''; local ok,ch = pcall(function() return unicode.utf8.char(cp) end);"
            "    if ok and ch then char_repr = ' \\\"'..ch..'\\\"' end;"
            "    local line = string.format('  U+%04X%s missing in fonts: %s', cp, char_repr, table.concat(fonts, ', '));"
            "    texio.write_nl('log', line); summary_lines[#summary_lines+1]=line;"
            "  end;"
            f"  if {abort_flag} then"
            "    texio.write_nl('term and log', '*** GBW: Aborting due to missing glyphs');"
            "    io.stderr:write('\\\\n=== GBW MISSING GLYPH ERROR ===\\\\n');"
            "    io.stderr:write('Found '..#keys..' codepoints with missing glyphs after fallback\\\\n');"
            "    if type(fb) == 'table' and next(fb) ~= nil then io.stderr:write('Fallback stack: '..table.concat(fb, '; ')..'\\\\n') end;"
            "    for _,l in ipairs(summary_lines) do io.stderr:write(l..'\\\\n') end;"
            "    io.stderr:write('=================================\\\\n');"
            "    io.stderr:flush();"
            "    tex.error('Missing glyphs after fallback', table.concat(summary_lines, '\\\\n'));"
            "  end;"
            "end;"
            "local lb = luatexbase or require('luatexbase');"
            "if lb and lb.add_to_callback then"
            "  texio.write_nl('term and log', '*** GBW: Registering callbacks');"
            "  lb.add_to_callback('hpack_filter', gbw_check, 'gbw-missing-glyphs-h');"
            "  lb.add_to_callback('pre_linebreak_filter', gbw_check, 'gbw-missing-glyphs-v');"
            "  lb.add_to_callback('finish_pdffile', gbw_report, 'gbw-missing-glyphs-report');"
            "  texio.write_nl('term and log', '*** GBW: Callbacks registered successfully');"
            "else"
            "  texio.write_nl('term and log', 'gbw missing glyph detector: luatexbase unavailable; skipping');"
            "end;"
            "}"
            "}"
        )
    elif not detector_requested:
        logger.info(
            "ℹ️ FONT-STACK: Missing-glyph detector deaktiviert (set ERDA_ENABLE_MISSING_GLYPH_DETECTOR=1 to enable)"
        )
    else:
        logger.info(
            "ℹ️ FONT-STACK: Missing-glyph detector übersprungen (lua fallback disabled)"
        )

    # CRITICAL: Replicate 2bc9e27 working pattern - Lua INSIDE \IfFontExistsTF conditional!
    if emoji_font:
        options: List[str] = []
        if needs_harfbuzz:
            options.append("Renderer=Harfbuzz")
        option_block = f"[{','.join(options)}]" if options else ""

        lines.append(f"\\IfFontExistsTF{{{emoji_font}}}{{")
        lines.append(f"  \\newfontfamily\\EmojiOne{option_block}{{{emoji_font}}}")

        # Register fallback INSIDE the conditional (critical for execution context!)
        if lua_fallback_code:
            lines.append(f"  {lua_fallback_code}")

        lines.append("}{}")

    # Font definitions with inline RawFeature (NO macro!)
    if include_mainfont:
        if fallback_block and emoji_font:
            lines.append(f"\\IfFontExistsTF{{{emoji_font}}}{{")
            lines.append(
                f"  \\setmainfont[RawFeature={{fallback=mainfont}}]{{{main_font}}}"
            )
            lines.append("}{")
            lines.append(f"  \\setmainfont{{{main_font}}}")
            lines.append("}")
        else:
            lines.append(f"\\setmainfont{{{main_font}}}")

    # Sans/Mono with conditional fallback
    sans_options = "[RawFeature={fallback=mainfont}]" if fallback_block else ""
    lines.append(f"\\setsansfont{sans_options}{{{sans_font}}}")
    lines.append(f"\\setmonofont{sans_options}{{{mono_font}}}")

    # Note: SVG files are converted to PDF during asset copying (asset_copy.py)
    # No LaTeX svg package needed since we now use Python-based conversion

    # Note: \panEmoji is now defined by latex-emoji.lua filter, not here
    return "\n".join(lines) + "\n"


def _combine_header_paths(
    default_header: Optional[Any],
    override_header: Optional[Any],
    extra_headers: Sequence[str],
) -> List[str]:
    headers: List[str] = []

    for candidate in (default_header, override_header):
        if not candidate:
            continue
        if isinstance(candidate, (list, tuple, set)):
            headers.extend(str(item) for item in candidate)
        else:
            headers.append(str(candidate))

    headers.extend(extra_headers)
    return headers


def _emit_emoji_report(md_file: str, pdf_out: Path, options: EmojiOptions) -> None:
    if not options.report:
        return

    try:
        counts, table_md = emoji_report(md_file)
    except Exception as exc:  # pragma: no cover - keep build running
        logger.error("Emoji-Analyse fehlgeschlagen: %s", exc)
        return

    timestamp = datetime.now(timezone.utc)
    target_dir = Path(options.report_dir) if options.report_dir else pdf_out.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    report_path = (
        target_dir / f"{pdf_out.stem}_emoji_report_{timestamp:%Y%m%d%H%M%S}.md"
    )

    lines = [
        "# Emoji usage report",
        "",
        f"* Source: {pdf_out.name}",
        f"* Generated: {timestamp.isoformat()}",
        "",
        table_md,
    ]
    if counts:
        lines.append("")
        lines.append("## Counts")
        for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"* {name}: {count}")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("ℹ Emoji-Report geschrieben nach %s", report_path)


def _load_pandoc_overrides() -> Dict[str, Any]:
    inline = os.environ.get("ERDA_PANDOC_DEFAULTS_JSON")
    if inline:
        try:
            data = json.loads(inline)
            if isinstance(data, dict):
                return data
            logger.warning(
                "ERDA_PANDOC_DEFAULTS_JSON muss ein JSON-Objekt liefern, nicht %s.",
                type(data).__name__,
            )
        except json.JSONDecodeError as exc:
            logger.warning("Konnte ERDA_PANDOC_DEFAULTS_JSON nicht parsen: %s", exc)
    path = os.environ.get("ERDA_PANDOC_DEFAULTS_FILE")
    if path:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                return data
            logger.warning(
                "%s muss ein JSON-Objekt enthalten, nicht %s.",
                path,
                type(data).__name__,
            )
        except OSError as exc:
            logger.warning("Konnte %s nicht lesen: %s", path, exc)
        except json.JSONDecodeError as exc:
            logger.warning("Konnte %s nicht parsen: %s", path, exc)
    return {}


@lru_cache(maxsize=1)
def _get_pandoc_defaults() -> Dict[str, Any]:
    overrides = _load_pandoc_overrides()
    defaults: Dict[str, Any] = {
        "lua_filters": tuple(_DEFAULT_LUA_FILTERS),
        "metadata": {key: tuple(values) for key, values in _DEFAULT_METADATA.items()},
        "variables": dict(_DEFAULT_VARIABLES),
        "header_path": _DEFAULT_HEADER_PATH,
        "pdf_engine": "lualatex",
        "extra_args": _DEFAULT_EXTRA_ARGS,
    }
    if not overrides:
        return defaults
    if "lua_filters" in overrides:
        try:
            defaults["lua_filters"] = _merge_sequence(
                defaults["lua_filters"], overrides["lua_filters"]
            )
        except TypeError as exc:
            logger.warning("Pandoc-Filter-Override ungültig: %s", exc)
    if "metadata" in overrides:
        defaults["metadata"] = _merge_metadata(
            defaults["metadata"], overrides["metadata"]
        )
    if "variables" in overrides:
        defaults["variables"] = _merge_variables(
            defaults["variables"], overrides["variables"]
        )
    if "header_path" in overrides:
        header_override = overrides.get("header_path")
        if header_override is None:
            defaults["header_path"] = None
        else:
            defaults["header_path"] = str(header_override)
    if "pdf_engine" in overrides:
        engine_override = overrides.get("pdf_engine")
        defaults["pdf_engine"] = str(engine_override) if engine_override else ""
    if "extra_args" in overrides:
        try:
            defaults["extra_args"] = _merge_sequence(
                defaults["extra_args"], overrides["extra_args"]
            )
        except TypeError as exc:
            logger.warning("Pandoc-Argument-Override ungültig: %s", exc)
    return defaults


def _reset_pandoc_defaults_cache() -> None:
    _get_pandoc_defaults.cache_clear()


def _parse_semver(value: str) -> Tuple[int, int, int]:
    if not isinstance(value, str):
        raise ValueError("Manifest-Version muss ein String sein.")
    candidate = value.strip()
    match = _SEMVER_RE.match(candidate)
    if not match:
        raise ValueError(
            "Manifest-Version muss dem SemVer-Format MAJOR.MINOR.PATCH entsprechen."
        )
    major_s, minor_s, patch_s = match.groups()
    return int(major_s), int(minor_s), int(patch_s)


def _format_semver(parts: Tuple[int, int, int]) -> str:
    return ".".join(str(p) for p in parts)


def _resolve_publish_directory(base_dir: Path, value: Optional[str]) -> Path:
    target = Path(value) if value else Path("publish")
    if not target.is_absolute():
        target = (base_dir / target).resolve()
    return target


def _download(url: str, dest: str) -> None:
    import urllib.request

    logger.info("↓ Download %s -> %s", url, dest)
    pathlib.Path(os.path.dirname(dest)).mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as r, open(dest, "wb") as f:
        f.write(r.read())


# ----------------------------- YAML Helpers -------------------------------- #


def prepareYAML() -> None:
    """Installiert PyYAML, falls nicht vorhanden."""
    try:
        import yaml  # noqa: F401

        return
    except Exception:
        pass
    py = sys.executable or "python"
    _run([py, "-m", "pip", "install", "--upgrade", "pip"], check=False)
    _run([py, "-m", "pip", "install", "pyyaml"])


def find_publish_manifest(explicit: Optional[str] = None) -> str:
    env_root = os.getenv("GITBOOK_CONTENT_ROOT")
    if explicit is None and env_root:
        for name in DEFAULT_FILENAMES:
            candidate = (Path(env_root) / name).resolve()
            if candidate.exists():
                return str(candidate)
    cwd = Path.cwd()
    repo_root = detect_repo_root(cwd)
    try:
        manifest_path = resolve_manifest(
            explicit=explicit, cwd=cwd, repo_root=repo_root
        )
    except SmartManifestError as exc:
        logger.error(str(exc))
        sys.exit(2)
    return str(manifest_path)


def _load_yaml(path: str) -> Dict[str, Any]:
    import yaml

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    version_value = data.get("version")
    if version_value is None:
        logger.error("Manifest-Version fehlt (Schlüssel 'version').")
        sys.exit(3)

    try:
        manifest_version = _parse_semver(str(version_value))
    except ValueError as exc:
        logger.error("Ungültige Manifest-Version '%s': %s", version_value, exc)
        sys.exit(3)

    if manifest_version[0] != _MANIFEST_VERSION_CURRENT[0]:
        logger.error(
            "Manifest-Major-Version %s wird nicht unterstützt (erwartet %d.x.x).",
            version_value,
            _MANIFEST_VERSION_CURRENT[0],
        )
        sys.exit(3)

    if manifest_version < _MANIFEST_VERSION_MIN:
        logger.error(
            "Manifest-Version %s ist zu alt. Minimal unterstützt: %s.",
            version_value,
            _format_semver(_MANIFEST_VERSION_MIN),
        )
        sys.exit(3)

    if manifest_version > _MANIFEST_VERSION_CURRENT:
        logger.warning(
            "Manifest-Version %s ist neuer als die getestete %s – versuche fortzufahren.",
            version_value,
            _format_semver(_MANIFEST_VERSION_CURRENT),
        )

    data["_manifest_version"] = manifest_version

    if "publish" not in data or not isinstance(data["publish"], list):
        logger.error("Ungültiges Manifest – Top-Level 'publish' (Liste) fehlt.")
        sys.exit(3)
    return data


def _save_yaml(path: str, data: Dict[str, Any]) -> None:
    import yaml

    serialisable = {k: v for k, v in data.items() if not str(k).startswith("_")}
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(serialisable, f, sort_keys=False, allow_unicode=True)


def _coerce_str(value: Any) -> str | None:
    if isinstance(value, str):
        text = value.strip()
        return text or None
    return None


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _coerce_date(value: Any) -> str | None:
    """Coerce a date-like value into YYYY-MM-DD.

    Notes:
      - YAML may deserialize YYYY-MM-DD into a datetime.date.
      - We intentionally validate the date format to keep publishing metadata
        stable and predictable.
    """

    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if not _DATE_RE.match(text):
            raise ValueError("expected YYYY-MM-DD")
        # Validate that the date is a real calendar date (e.g. rejects 2024-02-31)
        return datetime.fromisoformat(text).date().isoformat()
    return None


def _coerce_policy(value: Any) -> str:
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"warn", "warning"}:
            return "warn"
        if text == "fail":
            return "fail"
    return "fail"


def _author_label(value: Any) -> str | None:
    if isinstance(value, Mapping):
        name = _coerce_str(value.get("name") or value.get("full_name"))
        if not name:
            return None
        org = _coerce_str(value.get("org") or value.get("organization"))
        email = _coerce_str(value.get("email"))
        if org:
            return f"{name} ({org})"
        if email:
            return f"{name} <{email}>"
        return name
    return _coerce_str(value)


def _extract_authors(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)):
        label = _coerce_str(value)
        return (label,) if label else ()
    if isinstance(value, Mapping):
        label = _author_label(value)
        return (label,) if label else ()
    if isinstance(value, Sequence):
        authors: list[str] = []
        for entry in value:
            label = _author_label(entry)
            if label:
                authors.append(label)
        return tuple(authors)
    return ()


def _load_book_json(
    manifest_dir: Path,
) -> tuple[str | None, tuple[str, ...], str | None, Any]:
    book_path = manifest_dir / "book.json"
    if not book_path.exists():
        return None, (), None, None
    try:
        data = json.loads(book_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - best effort fallback
        logger.debug("book.json konnte nicht gelesen werden: %s", exc)
        return None, (), None, None
    title = _coerce_str(data.get("title"))
    authors = _extract_authors(data.get("author"))
    license_value = _coerce_str(data.get("license"))
    book_date = data.get("date")
    return title, authors, license_value, book_date


def _resolve_repo_hint(
    manifest_path: Path, repository: str | None
) -> tuple[str, str | None]:
    repo_root = detect_repo_root(manifest_path.parent)
    repo_name = repo_root.name or "repository"
    repo_owner: str | None = None
    slug = repository or os.getenv("GITHUB_REPOSITORY")
    if slug and isinstance(slug, str) and "/" in slug:
        repo_owner = slug.split("/", 1)[0] or None
    return repo_name, repo_owner


def _resolve_project_metadata(
    manifest_path: Path,
    *,
    manifest_data: Dict[str, Any] | None = None,
    repository: str | None = None,
) -> ProjectMetadata:
    data = manifest_data or _load_yaml(str(manifest_path))
    project_cfg = (
        data.get("project") if isinstance(data.get("project"), Mapping) else {}
    )
    policy = _coerce_policy(
        project_cfg.get("attribution_policy") if project_cfg else None
    )
    repo_name, repo_owner = _resolve_repo_hint(manifest_path, repository)
    book_title, book_authors, book_license, book_date_raw = _load_book_json(
        manifest_path.parent
    )

    warnings: list[str] = []

    name = _coerce_str(project_cfg.get("name")) if project_cfg else None
    if not name:
        name = book_title
    if not name:
        name = f"<MISSING project.name | using repo '{repo_name}'>"
        warnings.append(
            "project.name fehlt – verwende Repository-Namen als Platzhalter."
        )

    authors = _extract_authors(project_cfg.get("authors") if project_cfg else None)
    if not authors and book_authors:
        authors = book_authors
    if not authors:
        placeholder = "<MISSING project.authors"
        if repo_owner:
            placeholder += f" | using repo owner '{repo_owner}'"
        placeholder += ">"
        authors = (placeholder,)
        warnings.append(
            "project.authors fehlt – verwende Repository-Eigentümer als Platzhalter."
        )

    license_value = _coerce_str(project_cfg.get("license")) if project_cfg else None
    if not license_value:
        license_value = book_license
    if not license_value:
        msg = (
            "project.license fehlt – bitte in publish.yml unter project.license setzen."
        )
        if policy == "fail":
            raise ProjectMetadataError(msg)
        license_value = "<MISSING project.license>"
        warnings.append(msg + " attribution_policy=warn")

    # Document date override handling.
    # Precedence:
    # 1) publish.yml: project.date
    # 2) book.json: date
    # 3) fallback: keep existing derived/frontmatter date behaviour
    date_value: str | None = None
    manifest_date_raw = project_cfg.get("date") if project_cfg else None
    if manifest_date_raw is not None:
        try:
            date_value = _coerce_date(manifest_date_raw)
        except ValueError as exc:
            raise ProjectMetadataError(
                f"project.date ungültig (erwartet YYYY-MM-DD): {exc}"
            ) from exc
        if not date_value:
            raise ProjectMetadataError("project.date ungültig (erwartet YYYY-MM-DD).")
    elif book_date_raw is not None:
        try:
            date_value = _coerce_date(book_date_raw)
        except ValueError as exc:
            raise ProjectMetadataError(
                f"book.json date ungültig (erwartet YYYY-MM-DD): {exc}"
            ) from exc
        if not date_value:
            raise ProjectMetadataError("book.json date ungültig (erwartet YYYY-MM-DD).")

    return ProjectMetadata(
        name=name,
        authors=tuple(authors),
        license=license_value,
        date=date_value,
        policy=policy,
        warnings=tuple(warnings),
    )


def _dedupe_preserve_order(values: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    result: List[str] = []
    for raw in values:
        if not raw:
            continue
        candidate = os.path.normpath(str(raw))
        if candidate in seen:
            continue
        seen.add(candidate)
        result.append(Path(candidate).as_posix())
    return result


def _build_resource_paths(additional: Optional[Iterable[str]] = None) -> List[str]:
    defaults = [".", "assets", ".gitbook/assets", "content/.gitbook/assets"]
    if additional:
        defaults.extend(additional)
    return _dedupe_preserve_order(defaults)


def _mark_svg_pdf_available() -> None:
    os.environ.setdefault(_SVG_PDF_ENV_FLAG, "1")


def _convert_svg_to_pdf(svg_file: Path) -> bool:
    global _SVG_CONVERSION_WARNED

    if not svg_file.exists() or svg_file.suffix.lower() != ".svg":
        return False

    pdf_file = svg_file.with_suffix(".pdf")
    try:
        if pdf_file.exists():
            if pdf_file.stat().st_mtime >= svg_file.stat().st_mtime:
                _mark_svg_pdf_available()
                return True
        pdf_file.parent.mkdir(parents=True, exist_ok=True)

        result = ensure_svg_pdf(
            svg_file,
            pdf_file=pdf_file,
            prefer=("cairosvg", "svglib"),
            logger=logger,
        )
        if result.converted and pdf_file.exists():
            _mark_svg_pdf_available()
            return True

        if not _SVG_CONVERSION_WARNED:
            logger.warning(
                "Keine SVG-Konvertierung verfügbar – bitte cairosvg oder svglib/reportlab installieren."
            )
            _SVG_CONVERSION_WARNED = True
        return False
    except Exception as exc:  # pragma: no cover - best effort logging
        logger.warning("Konnte SVG %s nicht nach PDF konvertieren: %s", svg_file, exc)
        return False


def _prepare_asset_artifacts(path: Path) -> None:
    try:
        resolved = path.resolve()
    except Exception:
        return

    if not resolved.exists():
        return

    if resolved.is_dir():
        key = resolved.as_posix()
        if key in _SVG_DIR_CACHE:
            return
        _SVG_DIR_CACHE.add(key)
        for svg_file in resolved.rglob("*.svg"):
            _convert_svg_to_pdf(svg_file)
    elif resolved.is_file() and resolved.suffix.lower() == ".svg":
        _convert_svg_to_pdf(resolved)


def _resource_paths_for_source(
    md_path: str,
    resource_paths: Optional[Iterable[str]] = None,
) -> List[str]:
    """Resolve stable Pandoc resource paths for images and assets.

    ``pandoc`` resolves images relative to its working directory. When the
    orchestrator runs from the repository root but the Markdown lives in a
    subdirectory, images could be missed unless the source directory is part of
    ``--resource-path``. This helper ensures that the Markdown parent directory
    is always prioritised while keeping the existing defaults and any user
    supplied additions.
    """

    parent_dir = Path(md_path).resolve().parent
    merged = [parent_dir.as_posix()]
    merged.extend(_build_resource_paths(resource_paths))
    return _dedupe_preserve_order(merged)


def _parse_pdf_options(raw: Any) -> Dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {}

    parsed: Dict[str, Any] = {}

    # Abort flag defaults to True unless explicitly disabled
    parsed["abort_if_missing_glyph"] = True

    if "emoji_color" in raw:
        parsed["emoji_color"] = _as_bool(raw.get("emoji_color"))

    if "emoji_bxcoloremoji" in raw:
        parsed["emoji_bxcoloremoji"] = _as_bool(raw.get("emoji_bxcoloremoji"))

    for key in ("main_font", "sans_font", "mono_font"):
        value = raw.get(key)
        if value is None:
            continue
        value_str = str(value).strip()
        if value_str:
            parsed[key] = value_str

    fallback_value = raw.get("mainfont_fallback") or raw.get("main_font_fallback")
    if fallback_value is not None:
        fallback_str = str(fallback_value).strip()
        if fallback_str:
            parsed["mainfont_fallback"] = fallback_str

    if "abort_if_missing_glyph" in raw:
        parsed["abort_if_missing_glyph"] = _as_bool(raw.get("abort_if_missing_glyph"))

    return parsed


def _build_variable_overrides(pdf_options: Mapping[str, Any]) -> Dict[str, str]:
    variables: Dict[str, str] = {}
    mapping = {
        "main_font": "mainfont",
        "sans_font": "sansfont",
        "mono_font": "monofont",
        "mainfont_fallback": "mainfontfallback",
    }
    for option_key, variable_key in mapping.items():
        value = pdf_options.get(option_key)
        if isinstance(value, str) and value.strip():
            variables[variable_key] = value.strip()
    return variables


def _resolve_asset_paths(
    assets: List[Dict[str, Any]], manifest_dir: Path, entry_path: Path
) -> List[Dict[str, Any]]:
    resolved: List[Dict[str, Any]] = assets.copy()
    entry_base = entry_path if entry_path.is_dir() else entry_path.parent

    for asset in resolved:
        if isinstance(asset, dict):
            path_value = asset.get("path")
        else:
            path_value = asset

        if not path_value:
            continue

        candidate = Path(str(path_value))

        if candidate.is_absolute():
            # Note: SVG→PDF conversion now happens in asset_copy.py to avoid content dir pollution
            asset["path"] = str(candidate)
            continue

        # Prefer manifest-relative resolution, fall back to the entry folder.
        manifest_candidate = (manifest_dir / candidate).resolve()
        if manifest_candidate.exists():
            # Note: SVG→PDF conversion now happens in asset_copy.py to avoid content dir pollution
            asset["path"] = str(manifest_candidate)
            continue

        entry_candidate = (entry_base / candidate).resolve()
        if entry_candidate.exists():
            # Note: SVG→PDF conversion now happens in asset_copy.py to avoid content dir pollution
            asset["path"] = str(entry_candidate)
            continue

        # As a last resort keep the manifest-relative absolute path even if it
        # does not exist yet (e.g. generated later in the pipeline).
        asset["path"] = str(manifest_candidate)

    return resolved


# --------------------------- Public API (A) -------------------------------- #


def get_publish_list(manifest_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return all manifest entries that should be built."""

    prepareYAML()
    mpath = find_publish_manifest(manifest_path)
    data = _load_yaml(mpath)
    manifest_version = data.get("_manifest_version")
    if isinstance(manifest_version, tuple):
        logger.info("Manifest-Version: %s", _format_semver(manifest_version))
    res: List[Dict[str, Any]] = []

    for entry in data.get("publish", []):
        if not _as_bool(entry.get("build"), default=False):
            continue

        path = entry.get("path")
        out = entry.get("out")
        if not path or not out:
            logger.warning("Überspringe Manifest-Eintrag ohne path/out: %s", entry)
            continue

        out_dir = entry.get("out_dir")
        use_document_types = _as_bool(entry.get("use_document_types"))

        result: Dict[str, Any] = {
            "path": str(path),
            "out": str(out),
            "out_dir": str(out_dir) if out_dir not in (None, "") else None,
            "out_format": str(entry.get("out_format", "pdf") or "pdf").lower(),
            "source_type": str(entry.get("source_type") or entry.get("type") or "")
            .lower()
            .strip(),
            "source_format": str(entry.get("source_format", "markdown") or "markdown")
            .lower()
            .strip(),
            "use_summary": _as_bool(entry.get("use_summary")),
            "use_book_json": _as_bool(entry.get("use_book_json")),
            "keep_combined": _as_bool(entry.get("keep_combined")),
            "summary_mode": entry.get("summary_mode"),
            "summary_order_manifest": entry.get("summary_order_manifest"),
            "summary_manual_marker": entry.get("summary_manual_marker"),
            "summary_appendices_last": entry.get("summary_appendices_last"),
            "use_document_types": use_document_types,
            "document_manifest": str(mpath) if use_document_types else None,
            "reset_build_flag": _as_bool(entry.get("reset_build_flag")),
        }

        assets_value = entry.get("assets")
        assets: List[Dict[str, Any]] = []
        if isinstance(assets_value, list):
            for raw_asset in assets_value:
                if isinstance(raw_asset, dict):
                    path_value = raw_asset.get("path")
                    if not path_value:
                        continue
                    assets.append(
                        {
                            "path": str(path_value),
                            "type": str(raw_asset.get("type") or "").strip() or None,
                            "copy_to_output": _as_bool(raw_asset.get("copy_to_output")),
                        }
                    )
                elif raw_asset:
                    assets.append(
                        {
                            "path": str(raw_asset),
                            "type": None,
                            "copy_to_output": False,
                        }
                    )
        result["assets"] = assets
        result["pdf_options"] = _parse_pdf_options(entry.get("pdf_options"))
        res.append(result)

    return res


# ---------------------- Environment Prep (B / B.1) ------------------------- #


def prepare_publishing(
    no_apt: bool = False, manifest_path: Optional[str] = None
) -> None:
    """
    Installiert die System- und Python-Abhängigkeiten für den PDF-Build.
    - PyYAML (via prepareYAML)
    - Pandoc + LaTeX (apt-get auf Debian/Ubuntu)
    - OpenMoji Fonts (schwarz + farbig) + fc-cache
    - latex-emoji.lua (Pandoc Lua-Filter) für Legacy-Pipelines
    """
    prepareYAML()  # B.1

    manifest_path_obj = Path(manifest_path).resolve() if manifest_path else None
    _configure_texmf_cache(manifest_path_obj)

    # Pandoc vorhanden?
    have_pandoc = _which("pandoc") is not None
    have_lualatex = _which("lualatex") is not None

    removed_fonts: List[Path] = []
    if not (have_pandoc and have_lualatex):
        if no_apt:
            logger.warning(
                "pandoc/lualatex fehlen, --no-apt gesetzt. Bitte vorinstallieren."
            )
        elif _is_debian_like():
            sudo = _which("sudo")
            prefix = [sudo] if sudo else []
            _run(prefix + ["apt-get", "update"])
            _run(
                prefix
                + [
                    "apt-get",
                    "install",
                    "-y",
                    "--no-install-recommends",
                    "pandoc",
                    "texlive-luatex",
                    "texlive-fonts-recommended",
                    "texlive-latex-extra",
                    "fonts-dejavu-core",
                    "wget",
                ]
            )
        else:
            logger.warning(
                "Nicht-Debian System erkannt – installiere pandoc/LaTeX manuell."
            )

    removed_fonts = _purge_disallowed_fonts()

    # OpenMoji-Font & fc-cache
    manifest_specs: List[FontSpec] = []
    manifest_dir: Optional[Path] = None

    # Fonts are configured centrally in defaults/fonts.yml, BUT we still need to parse
    # manifest font paths to add them to OSFONTDIR and make them discoverable
    if manifest_path:
        manifest_candidate = Path(manifest_path)
        if not manifest_candidate.exists():
            logger.warning(
                "Manifest %s nicht gefunden – überspringe Schriftkonfiguration.",
                manifest_candidate,
            )
        else:
            manifest_dir = manifest_candidate.parent
            try:
                manifest_data = _load_yaml(str(manifest_candidate))
            except SystemExit:
                raise
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning(
                    "Konnte Manifest %s nicht lesen – Fonts auslassen: %s",
                    manifest_candidate,
                    exc,
                )
            else:
                manifest_specs = _parse_font_specs(
                    manifest_data.get("fonts"), manifest_dir
                )
                if manifest_specs:
                    logger.info(
                        "✓ %d Font-Pfade aus Manifest gelesen (werden zu OSFONTDIR hinzugefügt)",
                        len(manifest_specs),
                    )

    # OpenMoji removed per AGENTS.md (license compliance - only Twemoji CC BY 4.0 allowed)
    font_cache_refreshed = False

    def _maybe_refresh_font_cache() -> None:
        nonlocal font_cache_refreshed
        if font_cache_refreshed:
            return
        if _which("fc-cache"):
            # Note: -v (verbose) flag causes fc-cache to hang on Windows TeX Live
            # Use -v only on non-Windows platforms
            cmd = ["fc-cache", "-f"]
            if sys.platform != "win32":
                cmd.append("-v")
            _run(cmd, check=False)
            font_cache_refreshed = True

    if removed_fonts:
        _maybe_refresh_font_cache()

    def _register_font(font_path: Union[Path, str]) -> None:
        """Register a font file in OS-specific user font directories with hash checks."""

        if not font_path:
            return
        try:
            path_obj = Path(font_path)
            if not path_obj.exists():
                return

            for user_font_dir in _user_font_directories():
                user_font_dir.mkdir(parents=True, exist_ok=True)
                target = user_font_dir / path_obj.name

                needs_update = True
                if target.exists():
                    try:
                        source_hash = hashlib.sha256(path_obj.read_bytes()).hexdigest()
                        target_hash = hashlib.sha256(target.read_bytes()).hexdigest()
                        needs_update = source_hash != target_hash

                        if not needs_update:
                            logger.debug("ℹ Font bereits aktuell: %s", target)
                    except Exception as hash_exc:
                        logger.warning(
                            "⚠ Hash-Vergleich fehlgeschlagen für %s: %s",
                            target,
                            hash_exc,
                        )
                        needs_update = True

                if needs_update:
                    if target.exists():
                        target.unlink()
                        logger.info("✓ Alte Font-Version entfernt: %s", target)

                    shutil.copy2(path_obj, target)
                    logger.info("✓ Font aktualisiert: %s → %s", path_obj, target)

                    nonlocal font_cache_refreshed
                    font_cache_refreshed = False
                    _maybe_refresh_font_cache()

                _remember_font_dir(path_obj.parent)
                _remember_font_dir(user_font_dir)

        except Exception as exc:  # pragma: no cover - best effort only
            logger.warning("Konnte Font %s nicht registrieren: %s", font_path, exc)

    def _register_font_tree(path_obj: Path) -> bool:
        if path_obj.is_file():
            _register_font(path_obj)
            return True
        if path_obj.is_dir():
            _remember_font_dir(path_obj)
            found = False
            for pattern in ("*.ttf", "*.otf"):
                for candidate in path_obj.rglob(pattern):
                    _register_font(candidate)
                    found = True
            return found
        return False

    # Twemoji wird im Docker-Image aus dem offiziellen Release-Archiv installiert
    # (siehe tools/docker/Dockerfile). Diese Runtime-Prüfung stellt sicher, dass der
    # Font wirklich verfügbar ist und der Build andernfalls klar fehlschlägt.
    # OpenMoji references removed to ensure license compliance

    manifest_fonts: List[Dict[str, str]] = []
    if manifest_specs:
        logger.info("Wende Manifest-Font-Overrides an (%d Fonts)", len(manifest_specs))
        for spec in manifest_specs:
            font_dict: Dict[str, str] = {}
            if spec.name:
                font_dict["name"] = spec.name
            if spec.path:
                font_dict["path"] = str(spec.path)
            if spec.url:
                font_dict["url"] = spec.url
            if font_dict:
                manifest_fonts.append(font_dict)

    repo_root = _resolve_repo_root()
    repo_font_dir = repo_root / ".github" / "fonts"

    try:
        smart_fonts = prepare_runtime_font_loader(
            manifest_fonts=manifest_fonts or None,
            extra_search_paths=[repo_font_dir],
            repo_root=repo_root,
        )
    except SmartFontError as exc:
        logger.error("❌ Smart Font Stack fehlgeschlagen: %s", exc)
        hint_cmd = [
            sys.executable or "python",
            "-m",
            "gitbook_worker.tools.publishing.fonts_cli",
            "sync",
        ]
        if manifest_path:
            hint_cmd.extend(["--manifest", str(manifest_path)])
        hint_cmd.extend(["--search-path", str(repo_font_dir)])
        logger.error(
            "💡 Bitte Fonts synchronisieren: %s",
            " ".join(shlex.quote(str(part)) for part in hint_cmd),
        )
        logger.error(
            "   (Exit-Code 43 wird für Pipelines weitergereicht, damit Maschinen den Fehler erkennen.)"
        )
        raise SystemExit(43)

    font_config = smart_fonts.loader
    if smart_fonts.downloads:
        logger.info("✓ %d Fonts heruntergeladen", smart_fonts.downloads)
    for resolved_font in smart_fonts.resolved_fonts:
        logger.debug(
            "Smart Font %s → %s",
            resolved_font.name,
            ", ".join(path.as_posix() for path in resolved_font.paths),
        )
        for path in resolved_font.paths:
            _remember_font_dir(path.parent)

    force_font_cache_update = _as_bool(
        os.environ.get("ERDA_FORCE_FONT_CACHE_UPDATE"), False
    )
    if smart_fonts.downloads:
        force_font_cache_update = True
    if sys.platform == "win32":
        force_font_cache_update = True

    if force_font_cache_update:
        logger.info("ℹ Erzwinge Font-Cache-Update (Plattform/Downloads/Flag).")

    # Register CJK font from merged configuration
    erda_font_locations = font_config.get_font_paths("CJK")

    erda_font_found = False
    for erda_font_path in erda_font_locations:
        if os.path.exists(erda_font_path):
            logger.info("✓ ERDA CJK Font gefunden: %s", erda_font_path)
            _register_font(erda_font_path)
            _remember_font_dir(Path(erda_font_path).parent)
            erda_font_found = True
            break

    if not erda_font_found and erda_font_locations:
        logger.warning("⚠ ERDA CJK Font nicht gefunden in: %s", erda_font_locations)

    # Register additional fonts from repo .github/fonts directory
    if repo_font_dir.exists():
        logger.info("✓ Repository-Schriftverzeichnis gefunden: %s", repo_font_dir)
        for pattern in ("*.ttf", "*.otf"):
            for font_path in repo_font_dir.rglob(pattern):
                logger.info("✓ Registriere Repository-Font: %s", font_path)
                _register_font(str(font_path))
        _remember_font_dir(repo_font_dir)
        logger.info("✓ Repository-Font-Verzeichnis hinzugefügt: %s", repo_font_dir)

    # Register legacy manifest fonts (for backward compatibility)
    # TODO: Remove in future major version
    # Downloading fonts shall be only done into the fonts-storage/ managed by Smart Font Stack
    if manifest_specs:
        cache_dir = Path.home() / ".cache" / "erda-publisher" / "fonts"
        for spec in manifest_specs:
            handled = False
            if spec.path:
                try:
                    handled = _register_font_tree(spec.path)
                except Exception as exc:  # pragma: no cover - defensive
                    logger.warning(
                        "Konnte Font-Pfad %s nicht verarbeiten: %s", spec.path, exc
                    )
            if handled:
                continue
            if spec.url:
                parsed = urlparse(spec.url)
                filename = Path(parsed.path).name
                if not filename:
                    logger.warning(
                        "Font-Eintrag %s ohne gültigen Dateinamen in URL %s",
                        spec.name,
                        spec.url,
                    )
                    continue
                cache_dir.mkdir(parents=True, exist_ok=True)
                target = cache_dir / filename
                if not target.exists():
                    try:
                        _download(spec.url, str(target))
                    except Exception as exc:  # pragma: no cover - best effort only
                        logger.warning(
                            "Download für Font %s (%s) fehlgeschlagen: %s",
                            spec.name or filename,
                            spec.url,
                            exc,
                        )
                        continue
                _remember_font_dir(target.parent)
                _register_font(target)

    # Configure OSFONTDIR BEFORE cache checking so fc-list can find fonts-storage/
    logger.info("✓ Konfiguriere OSFONTDIR für Font-Verzeichnisse...")
    _configure_osfontdir([repo_font_dir])

    # Refresh fontconfig cache to pick up fonts-storage/ contents
    # This ensures fc-list can find newly downloaded fonts
    if _which("fc-cache"):
        logger.info("🔄 Refreshing fontconfig cache for OSFONTDIR...")
        cmd = ["fc-cache", "-f"]
        if sys.platform != "win32":
            cmd.append("-v")
        _run(cmd, check=False)

    # latex-emoji.lua Filter
    lua_dir = _resolve_module_path("lua")
    lua_path = os.path.join(lua_dir, "latex-emoji.lua")
    if not os.path.exists(lua_path):
        try:
            logger.info("↓ Lade latex-emoji.lua Pandoc Lua-Filter...")
            _ensure_dir(lua_dir)
            url = "https://gist.githubusercontent.com/zr-tex8r/a5410ad20ab291c390884b960c900537/raw/latex-emoji.lua"
            _download(url, lua_path)
        except Exception as e:
            logger.warning("Konnte latex-emoji.lua nicht laden: %s", e)

    # Smart font cache update: only if fonts are missing or were modified
    # NOTE: This runs AFTER OSFONTDIR is configured and fc-cache refreshed,
    # so fc-list can find fonts in fonts-storage/
    needs_cache_update = _fonts_need_cache_update()
    cache_update_required = force_font_cache_update or needs_cache_update

    if cache_update_required:
        if force_font_cache_update and not needs_cache_update:
            logger.info("🔄 Font-Cache-Update erzwungen (Zuverlässigkeit).")
        else:
            logger.info("🔄 Font caches veraltet - aktualisiere...")

        # Clear LuaLaTeX font caches after font registration
        # This ensures that LuaTeX picks up any font updates
        logger.info("🔄 Clearing LuaLaTeX font caches...")
        _clear_lualatex_caches()
        _update_luaotfload_database()

        # Final font cache refresh after all font operations
        if manifest_specs or removed_fonts or font_cache_refreshed:
            logger.info("🔄 Final fontconfig cache refresh...")
            if _which("fc-cache"):
                # Note: -v (verbose) flag causes fc-cache to hang on Windows TeX Live
                # Use -v only on non-Windows platforms
                cmd = ["fc-cache", "-f"]
                if sys.platform != "win32":
                    cmd.append("-v")
                _run(cmd, check=False)

        logger.info("✓ Font-Cache-Update abgeschlossen")
    else:
        logger.info(
            "✓ Font caches aktuell - überspringe Update (spart ~15-30 Sekunden)"
        )


# --------------------------- PDF Build (C) --------------------------------- #


def _get_book_title(folder: str) -> Optional[str]:
    try:
        # Pfad zum book.json eine Ebene über dem Ordner
        book_json_path = pathlib.Path(folder) / "book.json"
        if not book_json_path.exists():
            return None
        with book_json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("title")
    except Exception:
        return None


def _run_pandoc(
    md_path: str,
    pdf_out: str,
    add_toc: bool = False,
    title: Optional[str] = None,
    resource_paths: Optional[List[str]] = None,
    *,
    lua_filters: Optional[Sequence[str]] = None,
    metadata: Optional[Dict[str, Sequence[str] | str]] = None,
    variables: Optional[Dict[str, str]] = None,
    header_path: Optional[str] = None,
    pdf_engine: Optional[str] = None,
    from_format: Optional[str] = None,
    to_format: Optional[str] = None,
    extra_args: Optional[Sequence[str]] = None,
    toc_depth: Optional[int] = None,
    emoji_options: Optional[EmojiOptions] = None,
    abort_if_missing_glyph: bool = True,
) -> None:
    _ensure_dir(os.path.dirname(pdf_out))

    defaults = _get_pandoc_defaults()

    if resource_paths:
        resource_path_values = _build_resource_paths(resource_paths)
        resource_path_arg = (
            os.pathsep.join(resource_path_values) if resource_path_values else None
        )
        logger.info(
            "🔍 PANDOC-RUN: resource_path_arg für Pandoc: %s", resource_path_arg
        )
    else:
        resource_path_arg = None
        logger.info("🔍 PANDOC-RUN: Keine resource_paths für Pandoc angegeben.")

    filters = (
        list(lua_filters) if lua_filters is not None else list(defaults["lua_filters"])
    )
    logger.info("🔍 PANDOC-RUN: Lua-Filters für Pandoc: %s", filters)

    metadata_map: Dict[str, List[str]] = {
        key: list(values) for key, values in defaults["metadata"].items()
    }
    logger.info("🔍 PANDOC-RUN: Initial metadata_map from defaults: %s", metadata_map)
    if metadata:
        logger.info("🔍 PANDOC-RUN: Caller-provided metadata parameter: %s", metadata)
        for key, value in metadata.items():
            if isinstance(value, Mapping):
                try:
                    metadata_map[key] = list(
                        _merge_sequence(tuple(metadata_map.get(key, [])), value)
                    )
                except TypeError as exc:
                    logger.warning(
                        "Metadaten-Override für %s konnte nicht angewendet werden: %s",
                        key,
                        exc,
                    )
            elif isinstance(value, (list, tuple, set)):
                metadata_map[key] = [str(v) for v in value]
            else:
                metadata_map[key] = [str(value)]
        logger.info("🔍 PANDOC-RUN: Merged metadata_map: %s", metadata_map)

    variable_map: Dict[str, str] = dict(defaults["variables"])
    logger.info("🔍 PANDOC-RUN: Initial variable_map from defaults: %s", variable_map)
    user_supplied_mainfontfallback = False
    if variables:
        for key, value in variables.items():
            if value is None:
                variable_map.pop(key, None)
            else:
                if key == "mainfontfallback":
                    user_supplied_mainfontfallback = True
                variable_map[key] = str(value)
        logger.info("🔍 PANDOC-RUN: Merged variable_map: %s", variable_map)
        logger.info(
            "🔍 PANDOC-RUN: user_supplied_mainfontfallback: %s",
            user_supplied_mainfontfallback,
        )

    fallback_override = variable_map.pop("mainfontfallback", None)
    logger.info(
        "🔍 FONT-STACK: fallback_override aus variable_map: %s", fallback_override
    )
    if fallback_override is not None:
        fallback_override = str(fallback_override).strip() or None
        logger.info(
            "🔍 FONT-STACK: fallback_override nach strip: %s", fallback_override
        )

    options = emoji_options or EmojiOptions()

    if options.color:
        metadata_map["color"] = ["true"]
    else:
        metadata_map["color"] = ["false"]

    use_bxcoloremoji = _decide_bxcoloremoji(options)
    if use_bxcoloremoji:
        metadata_map["bxcoloremoji"] = ["true"]
    else:
        metadata_map.pop("bxcoloremoji", None)

    pandoc_version = _get_pandoc_version()
    if pandoc_version:
        logger.info("ℹ Erkannte Pandoc-Version: %s", ".".join(map(str, pandoc_version)))
    else:
        logger.warning("⚠ Pandoc-Version konnte nicht bestimmt werden")

    emoji_font, needs_harfbuzz = _select_emoji_font(options.color)
    logger.info(
        "🎯 FONT-STACK: _select_emoji_font() returned: font='%s', harfbuzz=%s",
        emoji_font,
        needs_harfbuzz,
    )

    main_font = variable_map.get("mainfont", _DEFAULT_VARIABLES["mainfont"])
    sans_font = variable_map.get(
        "sansfont", variable_map.get("mainfont", _DEFAULT_VARIABLES["sansfont"])
    )
    mono_font = variable_map.get(
        "monofont",
        variable_map.get("sansfont", _DEFAULT_VARIABLES["monofont"]),
    )

    # For testing: force manual Lua fallback path (use LaTeX header) instead of
    # relying on Pandoc's CLI `mainfontfallback` handling. Set to False to
    # reproduce manual fallback behaviour quickly.
    # To Be Approved ->
    # Font fallback mode decision:
    # Force manual LaTeX fallback (False) instead of Pandoc CLI fallback (True)
    # Reason: Pandoc 3.6+ CLI -V mainfontfallback=... is broken (fonts don't load)
    # Manual fallback uses \directlua{luaotfload.add_fallback(...)} which works reliably
    # <- To Be Approved
    supports_mainfont_fallback = (
        False  # bool(pandoc_version and pandoc_version >= (3, 1, 12))
    )
    cli_fallback_spec: Optional[str] = None
    manual_fallback_spec: Optional[str] = None
    if fallback_override:
        logger.info(
            "🎯 FONT-STACK: Verarbeite mainfontfallback Override: %s",
            fallback_override,
        )
        fallback_font_name = fallback_override.split(":", 1)[0].strip() or None
        override_needs_harfbuzz = _needs_harfbuzz(fallback_override)
        if override_needs_harfbuzz:
            needs_harfbuzz = True
        normalized_override = _normalize_fallback_spec(
            fallback_override,
            primary_font=fallback_font_name or emoji_font,
            needs_harfbuzz=needs_harfbuzz,
        )
        logger.info(
            "🎯 FONT-STACK: normalisierte mainfontfallback Override: %s",
            normalized_override,
        )

        if supports_mainfont_fallback:
            cli_fallback_spec = normalized_override
            logger.info("🎯 FONT-STACK: mainfontfallback via cli fallback spec")
        else:
            manual_fallback_spec = normalized_override
            logger.info("🎯 FONT-STACK: mainfontfallback via manuellen Fallback Header")

        if fallback_font_name and user_supplied_mainfontfallback:
            logger.info(
                "🎯 FONT-STACK: mainfontfallback override controls emoji font: %s",
                fallback_font_name,
            )
            emoji_font = fallback_font_name
    elif emoji_font:
        fallback_spec = _normalize_fallback_spec(
            f"{emoji_font}{':mode=harf' if needs_harfbuzz else ''}",
            primary_font=emoji_font,
            needs_harfbuzz=needs_harfbuzz,
        )
        logger.info(
            "🎯 FONT-STACK: generiere mainfontfallback aus emoji_font: %s",
            fallback_spec,
        )
        if supports_mainfont_fallback:
            cli_fallback_spec = fallback_spec
            logger.info("🎯 FONT-STACK: mainfontfallback via cli fallback spec")
        else:
            manual_fallback_spec = fallback_spec
            logger.info("🎯 FONT-STACK: mainfontfallback via manuellen Fallback Header")

    if emoji_font:
        logger.info(
            "🎯 FONT-STACK: Setze metadata_map['emojifont'] = ['%s']", emoji_font
        )
        metadata_map["emojifont"] = [emoji_font]
        if needs_harfbuzz:
            logger.info(
                "🎯 FONT-STACK: Setze metadata_map['emojifontoptions'] = ['Renderer=HarfBuzz']"
            )
            metadata_map["emojifontoptions"] = ["Renderer=HarfBuzz"]
        elif "emojifontoptions" in metadata_map:
            metadata_map.pop("emojifontoptions", None)
    else:
        logger.warning(
            "⚠️  FONT-STACK: Kein emoji_font - entferne emojifont aus metadata_map"
        )
        metadata_map.pop("emojifont", None)
        metadata_map.pop("emojifontoptions", None)

    header_defaults = defaults["header_path"]
    engine = pdf_engine if pdf_engine is not None else defaults["pdf_engine"]

    additional_args: List[str] = list(defaults["extra_args"])
    if extra_args:
        additional_args.extend(str(arg) for arg in extra_args)
    if cli_fallback_spec:
        additional_args.extend(["-V", f"mainfontfallback={cli_fallback_spec}"])

    header_override = header_path

    keep_latex_temp = os.getenv("ERDA_KEEP_LATEX_TEMP", "0").lower() in _TRUE_VALUES
    temp_ctx = Path(tempfile.mkdtemp(prefix="gbw-latex-"))
    with temp_ctx as temp_dir_raw:
        logger.info(
            "ℹ Verwende temporäres Verzeichnis für Pandoc/LaTeX: %s", temp_dir_raw
        )
        temp_dir = Path(temp_dir_raw).resolve()
        header_file = temp_dir / "pandoc-fonts.tex"
        font_header_content = _build_font_header(
            main_font=main_font,
            sans_font=sans_font,
            mono_font=mono_font,
            emoji_font=emoji_font,
            include_mainfont=not supports_mainfont_fallback,
            needs_harfbuzz=needs_harfbuzz,
            manual_fallback_spec=manual_fallback_spec,
            abort_if_missing_glyph=abort_if_missing_glyph,
            temp_dir=temp_dir,
        )
        header_file.write_text(font_header_content, encoding="utf-8")
        logger.info(
            "📄 FONT-STACK: pandoc-fonts.tex @ %s\n%s", header_file, font_header_content
        )

        # If a title was provided, prefer passing it via Pandoc metadata so the
        # standard template handles \maketitle once. Injecting our own title
        # header previously duplicated the title block (and an extra
        # \AtBeginDocument{\maketitle}), which could break the preamble.
        # Pandoc escapes titles for LaTeX, so we can safely rely on metadata.
        title_header_path = None
        if title:
            metadata_map["title"] = [str(title)]

        header_args = _combine_header_paths(
            header_defaults,
            header_override,
            [
                str(p)
                for p in ([title_header_path] if title_header_path else [])
                + [str(header_file)]
            ],
        )

        cmd: List[str] = ["pandoc", md_path, "-o", pdf_out]
        if from_format:
            cmd.extend(["-f", from_format])
        if to_format:
            cmd.extend(["-t", to_format])
        if engine:
            cmd.extend(["--pdf-engine", engine])
        if resource_path_arg:
            cmd.extend(["--resource-path", resource_path_arg])
            logger.info("ℹ Pandoc resource paths: %s", resource_path_arg)
        for header in header_args:
            cmd.extend(["-H", header])
        for filter_path in filters:
            cmd.extend(["--lua-filter", filter_path])
        logger.info(
            "🚀 FONT-STACK ABNEHMER [Pandoc CLI]: Konstruiere -M Argumente aus metadata_map: %s",
            metadata_map,
        )
        for key, values in metadata_map.items():
            for value in values:
                if (
                    "emoji" in key.lower()
                    or "color" in key.lower()
                    or "bxcolor" in key.lower()
                ):
                    logger.info(
                        "🚀 FONT-STACK ABNEHMER [Pandoc CLI]:   -M %s=%s", key, value
                    )
                cmd.extend(["-M", f"{key}={value}"])
        logger.info(
            "🚀 FONT-STACK ABNEHMER [Pandoc CLI]: Konstruiere --variable Argumente aus variable_map: %s",
            variable_map,
        )
        for key, value in variable_map.items():
            # If we injected a title header, avoid passing a title variable
            # to Pandoc as this can create duplicate/unescaped title output
            # in some templates.
            if title_header_path and key == "title":
                continue
            cmd.extend(["--variable", f"{key}={value}"])
        if add_toc:
            cmd.append("--toc")
            if toc_depth is not None:
                cmd.extend(["--toc-depth", str(toc_depth)])
        # Only pass the title via -V if we did not create a title header.
        # When a title header exists we rely on the header file and must not
        # also pass the title to Pandoc (see rationale above).
        if title and not title_header_path:
            # Escape LaTeX special characters to avoid errors like
            # "Misplaced alignment tab character &" when the title contains
            # an ampersand or other special chars.
            safe_title = _escape_latex(str(title))
            cmd.extend(["-V", f"title={safe_title}"])

        # Add --verbose for better error diagnostics
        cmd.append("--verbose")

        cmd.extend(additional_args)

        tex_source = Path(temp_dir) / Path(pdf_out).with_suffix(".tex").name
        logger.info("ℹ LaTeX debug output target: %s", tex_source)

        # ALWAYS set output directory to temp so LaTeX finds SVG conversions
        cmd.extend(["--pdf-engine-opt", f"-output-directory={temp_dir}"])
        # ALWAYS enable shell-escape for SVG conversion via Inkscape (NOTE: use = syntax!)
        cmd.append("--pdf-engine-opt=-shell-escape")

        # save current env tempdir setting
        original_tmpdir = os.environ.get("TMPDIR")
        logger.info("ℹ Original TMPDIR: %s", original_tmpdir)
        # set a env variable to keep latex temp for debugging
        os.environ["TMPDIR"] = temp_dir.as_posix()
        os.environ["TMP"] = temp_dir.as_posix()
        os.environ["TEMP"] = temp_dir.as_posix()
        logger.info("ℹ Set TMPDIR for Pandoc/LaTeX run: %s", os.environ["TMPDIR"])

        if keep_latex_temp:

            # Emit a standalone LaTeX file for easier debugging without relying on --keep-tex
            tex_cmd: List[str] = ["pandoc", md_path, "-o", str(tex_source)]
            if from_format:
                tex_cmd.extend(["-f", from_format])
            # Force LaTeX output so we always keep a readable .tex file
            tex_cmd.extend(["-t", "latex"])
            if resource_path_arg:
                tex_cmd.extend(["--resource-path", resource_path_arg])
            for header in header_args:
                tex_cmd.extend(["-H", header])
            for filter_path in filters:
                tex_cmd.extend(["--lua-filter", filter_path])
            for key, values in metadata_map.items():
                for value in values:
                    tex_cmd.extend(["-M", f"{key}={value}"])
            for key, value in variable_map.items():
                if title_header_path and key == "title":
                    continue
                tex_cmd.extend(["--variable", f"{key}={value}"])
            if add_toc:
                tex_cmd.append("--toc")
                if toc_depth is not None:
                    tex_cmd.extend(["--toc-depth", str(toc_depth)])
            if title and not title_header_path:
                safe_title = _escape_latex(str(title))
                tex_cmd.extend(["-V", f"title={safe_title}"])
            tex_cmd.append("--verbose")
            tex_cmd.extend(additional_args)
            logger.info(
                "🧩 Keeping LaTeX source via dedicated pandoc -t latex run: %s",
                tex_cmd,
            )
            _run(tex_cmd)

        try:
            logger.info("🚀 Führe Pandoc aus: %s", cmd)
            _run(cmd)
        except subprocess.CalledProcessError:
            # With -output-directory we expect LuaLaTeX to write .log files into
            # the temporary output directory. Pandoc commonly uses a tex2pdf.*
            # job name, so we must search broadly and pick the best candidate.
            temp_root = Path(temp_dir)
            pdf_path = Path(pdf_out)
            pdf_name = pdf_path.stem
            log_candidates: list[Path] = []

            try:
                log_candidates = list(temp_root.glob("**/*.log"))
            except Exception:
                log_candidates = []

            chosen_log: Path | None = None
            if log_candidates:
                preferred = [
                    p
                    for p in log_candidates
                    if p.name.startswith("tex2pdf") and p.suffix.lower() == ".log"
                ]
                if not preferred:
                    preferred = [
                        p
                        for p in log_candidates
                        if p.stem == pdf_name and p.suffix.lower() == ".log"
                    ]
                pool = preferred or log_candidates
                # Pick the newest log (best chance to contain the failure)
                chosen_log = max(
                    pool,
                    key=lambda p: p.stat().st_mtime if p.exists() else 0,
                )

            if chosen_log and chosen_log.exists():
                try:
                    log_content = chosen_log.read_text(
                        encoding="utf-8", errors="replace"
                    )
                    log_lines = log_content.splitlines()
                    excerpt = (
                        "\n".join(log_lines[-200:])
                        if len(log_lines) > 200
                        else log_content
                    )
                    logger.error(
                        "=== TeX LOG FILE (%s) ===\n%s\n=== END TeX LOG ===",
                        str(chosen_log),
                        excerpt,
                    )
                    logger.error(
                        "Hinweis: Für Debugging kann ERDA_KEEP_LATEX_TEMP=1 gesetzt werden, dann wird das Temp-Verzeichnis nach '_latex-debug' kopiert."
                    )
                except Exception as log_exc:
                    logger.warning(
                        "Could not read TeX log file %s: %s", chosen_log, log_exc
                    )
            else:
                logger.warning(
                    "No TeX log file found under %s (pdf_out=%s)", temp_root, pdf_out
                )
            raise
        finally:
            if keep_latex_temp:
                try:
                    debug_root = Path(pdf_out).parent / "_latex-debug"
                    debug_root.mkdir(parents=True, exist_ok=True)
                    target = debug_root / Path(temp_dir).name
                    shutil.copytree(temp_dir, target, dirs_exist_ok=True)
                    if tex_source.exists():
                        dest_tex = target / tex_source.name
                        shutil.copy2(tex_source, dest_tex)
                        logger.info(
                            "🧩 Copied LaTeX source for debugging: %s", dest_tex
                        )
                    logger.info(
                        "🧩 Kept LaTeX temp dir for debugging (ERDA_KEEP_LATEX_TEMP=1): %s",
                        target,
                    )
                except Exception as copy_exc:
                    logger.warning(
                        "Konnte LaTeX Temp-Verzeichnis nicht sichern: %s", copy_exc
                    )
    if not keep_latex_temp:
        try:
            shutil.rmtree(temp_ctx, ignore_errors=True)
            logger.info("🧹 Gelöscht LaTeX Temp-Verzeichnis: %s", temp_dir)
        except Exception as tex_exc:
            logger.warning("Konnte LaTeX Temp-Verzeichnis nicht löschen: %s", tex_exc)

    # restore original TMPDIR setting
    if original_tmpdir and os.environ.get("TMPDIR") != original_tmpdir:
        logger.info("ℹ Restoring original TMPDIR: %s", original_tmpdir)
        os.environ.update({"TMPDIR": original_tmpdir})


@dataclass(frozen=True)
class SummaryEntry:
    path: Path
    depth: int


def _extract_md_entries_from_summary(
    summary_path: Path, root_dir: Path
) -> List[SummaryEntry]:
    if not summary_path.exists():
        return []

    resolved: "OrderedDict[Path, SummaryEntry]" = OrderedDict()
    pattern = re.compile(r"\(([^)]+\.(?:md|markdown))\)", re.IGNORECASE)
    indent_stack: list[int] = []

    try:
        with summary_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                matches = pattern.findall(line)
                if not matches:
                    continue

                expanded = line.expandtabs(4)
                indent = len(expanded) - len(expanded.lstrip(" "))

                while indent_stack and indent < indent_stack[-1]:
                    indent_stack.pop()
                if not indent_stack or indent > indent_stack[-1]:
                    indent_stack.append(indent)
                depth = len(indent_stack) or 1

                for match in matches:
                    target = match.split("#", 1)[0].strip()
                    if not target or target.startswith(("http://", "https://")):
                        continue
                    candidate = (root_dir / target).resolve()
                    if candidate.suffix.lower() not in {".md", ".markdown"}:
                        continue
                    if not candidate.exists():
                        logger.debug(
                            "SUMMARY.md references non-existent file: %s", target
                        )
                        continue
                    if candidate not in resolved:
                        resolved[candidate] = SummaryEntry(candidate, depth)
    except Exception as exc:
        logger.warning("Konnte SUMMARY in %s nicht lesen: %s", summary_path, exc)
        return []

    return list(resolved.values())


def _extract_md_paths_from_summary(summary_path: Path, root_dir: Path) -> List[str]:
    return [
        str(entry.path)
        for entry in _extract_md_entries_from_summary(summary_path, root_dir)
    ]


def _iter_summary_candidates(folder: Path, summary_path: Optional[Path]) -> List[Path]:
    candidates: List[Path] = []
    seen: set[Path] = set()

    if summary_path is not None:
        resolved = summary_path.resolve()
        candidates.append(resolved)
        seen.add(resolved)

    for name in ("SUMMARY.md", "summary.md"):
        candidate = (folder / name).resolve()
        if candidate not in seen:
            candidates.append(candidate)
            seen.add(candidate)

    return candidates


@dataclass(frozen=True)
class MarkdownCollection:
    # list of markdown file paths
    files: List[str]
    # mapping of markdown file path to desired heading target depth (header level)
    heading_targets: dict[Path, int]


def _build_default_heading_targets(
    md_files: List[str], folder_path: Path
) -> dict[Path, int]:
    targets: dict[Path, int] = {}
    for name in md_files:
        try:
            resolved = Path(name).resolve()
        except Exception:
            continue

        try:
            rel_parts = resolved.relative_to(folder_path).parts
            depth = max(1, len(rel_parts))
        except Exception:
            depth = 1

        targets[resolved] = depth
    return targets


def _collect_folder_md(
    folder: str,
    use_summary: bool,
    *,
    summary_layout: Optional[SummaryContext] = None,
) -> MarkdownCollection:
    folder_path = Path(folder).resolve()
    root_dir = summary_layout.root_dir if summary_layout else folder_path
    summary_candidates = _iter_summary_candidates(
        folder_path, summary_layout.summary_path if summary_layout else None
    )

    if use_summary:
        for candidate in summary_candidates:
            entries = _extract_md_entries_from_summary(candidate, root_dir)
            logger.info(
                "ℹ %d Markdown-Dateien aus %s gelesen.",
                len(entries),
                candidate,
            )
            if entries:
                files = [str(entry.path) for entry in entries]
                heading_targets = {
                    entry.path.resolve(): max(1, entry.depth) for entry in entries
                }
                return MarkdownCollection(files=files, heading_targets=heading_targets)
    # Fallback: alle .md rekursiv, README bevorzugt
    md_files: List[str] = []
    for root, _, files in os.walk(folder_path):
        for fname in sorted(files):
            if fname.lower().endswith((".md", ".markdown")):
                full = os.path.join(root, fname)
                if fname.lower() == "readme.md":
                    md_files.insert(0, full)
                else:
                    md_files.append(full)
    logger.info("ℹ %d Markdown-Dateien in %s gefunden.", len(md_files), folder_path)
    heading_targets = _build_default_heading_targets(md_files, folder_path)
    return MarkdownCollection(files=md_files, heading_targets=heading_targets)


def convert_a_file(
    md_file: str,
    pdf_out: str,
    keep_converted_markdown: bool = False,
    publish_dir: str = "publish",
    paper_format: str = "a4",
    assets: Optional[List[Dict[str, Any]]] = None,
    emoji_options: Optional[EmojiOptions] = None,
    variables: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Sequence[str] | str]] = None,
    abort_if_missing_glyph: bool = True,
) -> None:
    logger.info(
        "========================================================================"
    )
    logger.info("Convert a new single file")
    logger.info(
        "------------------------------------------------------------------------"
    )
    logger.info("File                    : %s", md_file)
    logger.info("PDF OUT                 : %s", pdf_out)
    logger.info("Keep Converted Markdown : %s", keep_converted_markdown)
    logger.info("Publish Dir             : %s", publish_dir)
    logger.info("Paper Format            : %s", paper_format)
    if assets:
        logger.info("Assets to copy          : %s", assets)

    # preprocess for wide content (tables, images), will change page geometry
    processed = process(md_file, paper_format=paper_format)
    logger.info("%s: Nach Preprocessing %d Zeichen.", md_file, len(processed))
    # normalize for pandoc
    normalized = normalize_md(processed)
    logger.info("%s: Nach Normalisierung %d Zeichen.", md_file, len(normalized))
    # add geometry package
    content = add_geometry_package(
        normalized,
        paper_format=paper_format,
    )
    # Get temp dir for converted markdown
    tempfile.tempdir = Path(publish_dir) / "temp" if publish_dir else None
    # Ensure temp dir exists
    if tempfile.tempdir:
        _ensure_dir(tempfile.tempdir)
    logger.info("ℹ Using temp dir: %s", tempfile.tempdir)
    with tempfile.NamedTemporaryFile(
        "w",
        suffix=".md",
        delete=False,
        encoding="utf-8",
        newline="\n",
        dir=tempfile.tempdir,
    ) as tmp:
        tmp.write(content)
        tmp_md = tmp.name
    try:
        options = emoji_options or EmojiOptions()
        _emit_emoji_report(tmp_md, Path(pdf_out), options)

        # Extract title from markdown file frontmatter or filename
        title = None
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                if first_line.startswith("# "):
                    title = first_line[2:].strip()
        except Exception:
            pass

        metadata_map = dict(metadata) if metadata else {}
        if title and "title" not in metadata_map:
            metadata_map["title"] = [title]

        resource_paths = _resource_paths_for_source(
            md_file,
            [
                asset.get("path")
                for asset in assets or []
                if asset.get("path") is not None and asset.get("copy_to_output") is True
            ],
        )

        _run_pandoc(
            tmp_md,
            pdf_out,
            add_toc=False,  # Single files typically don't need TOC
            title=title,
            resource_paths=resource_paths,
            emoji_options=options,
            variables=variables,
            metadata=metadata_map or None,
            abort_if_missing_glyph=abort_if_missing_glyph,
        )
    finally:
        try:
            if not keep_converted_markdown:
                os.unlink(tmp_md)
            else:
                converted_md_path = pdf_out.replace(".pdf", ".md")
                logger.info(
                    "Keeping converted markdown in %s",
                    converted_md_path,
                )
                print(
                    "Keeping converted markdown in " + converted_md_path,
                )
                shutil.move(str(tmp_md), str(converted_md_path))
        except OSError as e:
            logger.error("Failed to operate on converted markdown caused by %s", e)
            pass
        logger.info(
            "------------------------------------------------------------------------"
        )
        logger.info("%s", content)
        logger.info(
            "========================================================================"
        )


def convert_a_folder(
    folder: str,
    pdf_out: str,
    use_summary: bool = True,
    keep_converted_markdown: bool = False,
    publish_dir: str = "publish",
    paper_format: str = "a4",
    summary_layout: Optional[SummaryContext] = None,
    assets: Optional[List[Dict[str, Any]]] = None,
    emoji_options: Optional[EmojiOptions] = None,
    variables: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Sequence[str] | str]] = None,
    abort_if_missing_glyph: bool = True,
) -> None:

    logger.info(
        "========================================================================"
    )
    logger.info("Convert a folder")
    logger.info(
        "------------------------------------------------------------------------"
    )
    logger.info("Folder                  : %s", folder)
    logger.info("PDF OUT                 : %s", pdf_out)
    logger.info("Keep Converted Markdown : %s", keep_converted_markdown)
    logger.info("Publish Dir             : %s", publish_dir)
    logger.info("Paper Format            : %s", paper_format)
    logger.info("Use Summary             : %s", use_summary)
    if summary_layout:
        logger.info("Summary Layout Root Dir : %s", summary_layout.root_dir)
        logger.info("Summary Layout Summary  : %s", summary_layout.summary_path)
    if assets:
        logger.info("Assets to copy          : %d", len(assets))

    md_collection = _collect_folder_md(
        folder, use_summary=use_summary, summary_layout=summary_layout
    )
    md_files = md_collection.files
    heading_targets = md_collection.heading_targets
    if not md_files:
        logger.info("ℹ Keine Markdown-Dateien in %s – übersprungen.", folder)
        raise Exception(f"No markdown files found in {folder}")
    combined = add_geometry_package(
        combine_markdown(
            md_files,
            paper_format=paper_format,
            heading_targets=heading_targets,
        ),
        paper_format=paper_format,
    )
    # Escape the first/top-level Markdown heading in the combined document to
    # avoid LaTeX errors (e.g. unescaped '&' in titles).
    try:
        import re

        m = re.search(r"(?m)^(#\s+)(.+)$", combined)
        if m:
            prefix = m.group(1)
            txt = m.group(2)
            combined = (
                combined[: m.start()]
                + prefix
                + _escape_latex(txt)
                + combined[m.end() :]
            )
    except Exception:
        # best-effort only
        pass
    # 🔧 FIX: Strip ../ from .gitbook/assets/ image paths BEFORE Pandoc processing
    import re

    logger.info("🔍 DEBUG combined length BEFORE fix: %d", len(combined))
    logger.info("🔍 DEBUG contains ../.gitbook pattern: %s", "../.gitbook" in combined)
    combined = re.sub(r"\(\.\.\/\.gitbook\/assets\/", r"(.gitbook/assets/", combined)
    logger.info("🔍 DEBUG combined length AFTER fix: %d", len(combined))

    # Prepare resource paths
    resolved_resource_paths: List[str] = []

    # Get temp dir for combined md
    tempfile.tempdir = Path(publish_dir) / "temp" if publish_dir else None
    # Ensure temp dir exists
    if tempfile.tempdir:
        _ensure_dir(tempfile.tempdir)
    logger.info("ℹ Using temp dir: %s", tempfile.tempdir)

    # Write combined md to temp file
    with tempfile.NamedTemporaryFile(
        "w",
        suffix=".md",
        delete=False,
        encoding="utf-8",
        newline="\n",
        dir=tempfile.tempdir,
    ) as tmp:
        tmp.write(combined)
        tmp_md = tmp.name

    logger.info("🔍 DEBUG REACHED asset copying section, tmp_md=%s", tmp_md)

    # Copy assets marked with copy_to_output=true to temp directory
    # Pandoc resolves images relative to the markdown file (temp directory)
    import shutil

    if assets:
        copy_assets_to_temp(
            Path(tmp_md),
            Path(folder),
            assets,
            resolved_resource_paths=resolved_resource_paths,
        )

    try:
        title = _get_book_title(folder)
        if title:
            logger.info("ℹ Buch-Titel aus book.json: %s", title)
        else:
            logger.info("ℹ Kein Buch-Titel")
        options = emoji_options or EmojiOptions()
        _emit_emoji_report(tmp_md, Path(pdf_out), options)
        if summary_layout:
            # Allow GitBook-style asset folders below the content root.
            resolved_resource_paths.append(str(summary_layout.root_dir))

        metadata_map = dict(metadata) if metadata else {}
        if title and "title" not in metadata_map:
            metadata_map["title"] = [title]

        # Add publish directory (parent of temp MD) to resource paths
        # This ensures Pandoc can find images relative to the working dir
        temp_parent = Path(tmp_md).resolve().parent
        final_paths = [str(temp_parent)]
        if resolved_resource_paths:
            final_paths.extend(resolved_resource_paths)
        # Add standard defaults from _build_resource_paths
        final_paths.extend(_build_resource_paths([]))

        _run_pandoc(
            tmp_md,
            pdf_out,
            add_toc=True,
            title=title,
            resource_paths=final_paths,
            emoji_options=options,
            variables=variables,
            metadata=metadata_map or None,
            abort_if_missing_glyph=abort_if_missing_glyph,
        )
    finally:
        try:
            if not keep_converted_markdown:
                os.unlink(tmp_md)
            else:
                converted_markdown = pdf_out.replace(".pdf", ".md")
                logger.info("ℹ Behalte kombiniertes Markdown in %s", converted_markdown)
                _ensure_dir(publish_dir)
                shutil.move(str(tmp_md), str(converted_markdown))
        except OSError as e:
            logger.error("Failed to operate on converted markdown caused by %s", e)
            pass
        logger.info(
            "------------------------------------------------------------------------"
        )
        logger.info("%s", combined)
        logger.info(
            "========================================================================"
        )


def build_pdf(
    path: str | Path,
    out: str,
    typ: str,
    use_summary: bool = False,
    use_book_json: bool = False,
    keep_combined: bool = False,
    publish_dir: str = "publish",
    paper_format: str = "a4",
    summary_mode: Optional[str] = None,
    summary_order_manifest: Optional[Path] = None,
    summary_manual_marker: Optional[str] = DEFAULT_MANUAL_MARKER,
    summary_appendices_last: bool = False,
    document_manifest: Optional[Path] = None,
    locale: Optional[str] = None,
    validate_doc_types: bool = False,
    fail_on_doc_type_issues: bool = False,
    assets: Optional[List[Dict[str, Any]]] = None,
    emoji_options: Optional[EmojiOptions] = None,
    variables: Optional[Dict[str, str]] = None,
    project_metadata: Optional[ProjectMetadata] = None,
    abort_if_missing_glyph: bool = True,
) -> Tuple[bool, Optional[str]]:
    """
    Baut ein PDF gemäß Typ ('file'/'folder').
    Gibt True bei Erfolg zurück und False bei Fehlern plus eine detaillierte Fehlernachricht.
    """
    publish_path = Path(publish_dir).resolve()
    _ensure_dir(str(publish_path))
    pdf_out = publish_path / out
    path_obj = Path(path).resolve()

    base_metadata = project_metadata.as_pandoc_metadata() if project_metadata else None

    logger.info("✔ Building %s from %s (type=%s)", pdf_out, path_obj, typ)

    # Typ autodetektion, falls leer/ungewohnt
    _typ = (typ or "").lower().strip()
    if not _typ or _typ not in {"file", "folder"}:
        if path_obj.is_dir():
            _typ = "folder"
        else:
            _typ = "file"

    try:
        if _typ == "file":
            # _convert_single_file(
            #    path,
            #    pdf_out,
            #    paper_format=paper_format,
            # )
            convert_a_file(
                str(path_obj),
                str(pdf_out),
                keep_converted_markdown=True,
                publish_dir=str(publish_path),
                paper_format=paper_format,
                assets=assets,
                emoji_options=emoji_options,
                variables=variables,
                metadata=base_metadata,
                abort_if_missing_glyph=abort_if_missing_glyph,
            )
        elif _typ == "folder":
            summary_layout: Optional[SummaryContext] = None
            needs_summary_refresh = (
                use_book_json
                or summary_mode is not None
                or summary_order_manifest is not None
                or document_manifest is not None
                or validate_doc_types
                or fail_on_doc_type_issues
                or (
                    summary_manual_marker is not None
                    and summary_manual_marker != DEFAULT_MANUAL_MARKER
                )
            )
            if needs_summary_refresh:
                try:
                    summary_layout = get_summary_layout(path_obj)
                    ensure_clean_summary(
                        summary_layout.base_dir,
                        run_git=False,
                        summary_mode=summary_mode,
                        summary_order_manifest=summary_order_manifest,
                        manual_marker=summary_manual_marker,
                        summary_appendices_last=summary_appendices_last,
                        document_manifest=document_manifest,
                        locale=locale,
                        validate_doc_types=validate_doc_types,
                        fail_on_doc_type_issues=fail_on_doc_type_issues,
                    )
                except Exception as exc:  # pragma: no cover - best effort logging
                    logger.warning(
                        "Konnte SUMMARY via book.json nicht aktualisieren: %s", exc
                    )
            convert_a_folder(
                str(path_obj),
                str(pdf_out),
                use_summary=use_summary or use_book_json or summary_layout is not None,
                keep_converted_markdown=keep_combined,
                publish_dir=str(publish_path),
                paper_format=paper_format,
                summary_layout=summary_layout,
                assets=assets,
                emoji_options=emoji_options,
                variables=variables,
                metadata=base_metadata,
                abort_if_missing_glyph=abort_if_missing_glyph,
            )
        else:
            logger.warning("⚠ Unbekannter type='%s' – übersprungen.", typ)
            return False, f"Unknown type='{typ}' - skipped"
        return True, None
    except subprocess.CalledProcessError as e:
        logger.error("Pandoc/LaTeX Build fehlgeschlagen (rc=%s).", e.returncode)
        error_details = [f"Command failed with exit code {e.returncode}"]
        error_details.append(
            f"Command: {' '.join(e.cmd) if hasattr(e, 'cmd') else 'unknown'}"
        )

        if e.stdout:
            stdout_str = (
                e.stdout
                if isinstance(e.stdout, str)
                else e.stdout.decode("utf-8", errors="replace")
            )
            logger.error("STDOUT:\n%s", stdout_str)
            error_details.append(f"STDOUT:\n{stdout_str}")

        if e.stderr:
            stderr_str = (
                e.stderr
                if isinstance(e.stderr, str)
                else e.stderr.decode("utf-8", errors="replace")
            )
            logger.error("STDERR:\n%s", stderr_str)
            error_details.append(f"STDERR:\n{stderr_str}")

        return False, "\n".join(error_details)
    except Exception as e:
        logger.error("Build-Fehler: %s", e)
        error_details = [f"Exception: {type(e).__name__}: {e}"]

        stdout = getattr(e, "stdout", "")
        stderr = getattr(e, "stderr", "")

        if stdout:
            stdout_str = (
                stdout
                if isinstance(stdout, str)
                else stdout.decode("utf-8", errors="replace")
            )
            logger.error("STDOUT:\n%s", stdout_str)
            error_details.append(f"STDOUT:\n{stdout_str}")

        if stderr:
            stderr_str = (
                stderr
                if isinstance(stderr, str)
                else stderr.decode("utf-8", errors="replace")
            )
            logger.error("STDERR:\n%s", stderr_str)
            error_details.append(f"STDERR:\n{stderr_str}")

        return False, "\n".join(error_details)


# -------------------------------- Main (D) --------------------------------- #


def _write_github_outputs(built: List[str], failed: List[str], manifest: str) -> None:
    gh_out = os.getenv("GITHUB_OUTPUT")
    if gh_out:
        try:
            with open(gh_out, "a", encoding="utf-8") as f:
                f.write(f"built_count={len(built)}\n")
                f.write(f"built_files={json.dumps(built, ensure_ascii=False)}\n")
                f.write(f"failed_files={json.dumps(failed, ensure_ascii=False)}\n")
                f.write(f"manifest={manifest}\n")
        except Exception as e:
            logger.warning("Konnte GITHUB_OUTPUT nicht schreiben: %s", e)


def main() -> None:
    logger.info("Selective Publisher gestartet: argv=%s", sys.argv)
    ap = argparse.ArgumentParser(description="Selective publisher für publish.yml")
    ap.add_argument("--root", type=Path, help="Repository root (Default: cwd)")
    ap.add_argument(
        "--content-config",
        type=Path,
        help="Pfad zu content.yaml (Default: Repository-Root)",
    )
    ap.add_argument(
        "--lang",
        "--language",
        dest="language",
        help="Sprach-ID aus content.yaml",
    )
    ap.add_argument("--manifest", help="Pfad zu publish.yml|yaml (Default: Root)")
    ap.add_argument(
        "--no-apt", action="store_true", help="Keine apt-Installation versuchen"
    )
    ap.add_argument(
        "--only-prepare",
        action="store_true",
        help="Nur Umgebung vorbereiten und beenden",
    )
    ap.add_argument(
        "--reset-script",
        default="gitbook_worker/tools/publishing/reset-publish-flag.py",
        help="Pfad zum Reset-Tool",
    )
    ap.add_argument(
        "--paper-format",
        help="Enable landscape orientation for wide content",
        default="a4",
    )
    ap.add_argument(
        "--publish-dir",
        help="The directory to publish to.",
        default="publish",
    )
    ap.add_argument(
        "--emoji-color",
        dest="emoji_color",
        action="store_true",
        default=True,
        help="Render emojis with the colour OpenMoji font when available.",
    )
    ap.add_argument(
        "--no-emoji-color",
        dest="emoji_color",
        action="store_false",
        help="Disable colour emoji rendering.",
    )
    ap.add_argument(
        "--emoji-bxcoloremoji",
        dest="emoji_bxcoloremoji",
        action="store_true",
        default=None,
        help="Force usage of the bxcoloremoji LaTeX package when rendering emojis.",
    )
    ap.add_argument(
        "--no-emoji-bxcoloremoji",
        dest="emoji_bxcoloremoji",
        action="store_false",
        help="Disable bxcoloremoji even if the package is available.",
    )
    ap.add_argument(
        "--emoji-report",
        action="store_true",
        help="Write a usage report for emojis encountered during the build.",
    )
    ap.add_argument(
        "--emoji-report-dir",
        help="Optional output directory for emoji reports (defaults to publish dir).",
    )
    args = ap.parse_args()

    raw_root = args.root.resolve() if args.root else Path.cwd()
    repo_root = detect_repo_root(raw_root)
    language_ctx = resolve_language_context(
        repo_root=repo_root,
        language=args.language,
        manifest=args.manifest,
        content_config=args.content_config,
        allow_missing_config=True,
        allow_remote_entries=True,
        require_manifest=True,
        fetch_remote=True,
    )
    env_payload = build_language_env(language_ctx)
    os.environ.update(env_payload)
    manifest = str(language_ctx.require_manifest())

    try:
        project_metadata = _resolve_project_metadata(
            Path(manifest), repository=os.getenv("GITHUB_REPOSITORY")
        )
    except ProjectMetadataError as exc:
        logger.error("Projekt-Metadaten ungültig: %s", exc)
        sys.exit(3)

    for warn in project_metadata.warnings:
        logger.warning(warn)

    if args.only_prepare:
        # B.1 + B
        prepare_publishing(no_apt=args.no_apt, manifest_path=manifest)
        logger.info("✔ Umgebung vorbereitet. (only-prepare)")
        return

    # prepareYAML()  # B.1
    prepareYAML()
    # get manifest publish list (A)
    targets = get_publish_list(manifest)

    if not targets:
        logger.info("ℹ Keine zu publizierenden Einträge (build: true).")
        _write_github_outputs([], [], manifest)
        return

    logger.info("ℹ %d zu publizierende Einträge gefunden.", len(targets))
    # prepare huge environment (B)
    prepare_publishing(no_apt=args.no_apt, manifest_path=manifest)
    built: List[str] = []
    failed: List[str] = []

    manifest_path = Path(manifest).resolve()
    manifest_dir = manifest_path.parent
    default_publish_dir = _resolve_publish_directory(manifest_dir, args.publish_dir)

    emoji_report_dir = (
        Path(args.emoji_report_dir).resolve() if args.emoji_report_dir else None
    )
    emoji_options = EmojiOptions(
        color=args.emoji_color,
        report=args.emoji_report,
        report_dir=emoji_report_dir,
        bxcoloremoji=args.emoji_bxcoloremoji,
    )

    # C + Reset je nach Erfolg
    for entry in targets:
        original_path = entry["path"]
        path = Path(original_path)
        if not path.is_absolute():
            path = (manifest_dir / path).resolve()
        out = entry["out"]
        out_format = entry.get("out_format", "pdf")
        if out_format.lower() != "pdf":
            msg = f"Unsupported out_format='{out_format}'"
            logger.warning("⚠ %s – Eintrag wird übersprungen.", msg)
            failed.append(f"{out}: {msg}")
            continue

        typ = entry.get("source_type") or entry.get("type", "")
        publish_base = entry.get("out_dir")
        publish_dir_path = (
            _resolve_publish_directory(manifest_dir, publish_base)
            if publish_base
            else default_publish_dir
        )
        summary_mode = entry.get("summary_mode")
        if summary_mode is not None:
            summary_mode = str(summary_mode).strip() or None
        manifest_value = entry.get("summary_order_manifest")
        summary_manifest_path: Optional[Path]
        if manifest_value:
            summary_manifest_path = Path(str(manifest_value))
            if not summary_manifest_path.is_absolute():
                summary_manifest_path = (manifest_dir / summary_manifest_path).resolve()
        else:
            summary_manifest_path = None
        summary_manual_marker_value = entry.get("summary_manual_marker")
        if summary_manual_marker_value is None:
            summary_manual_marker = DEFAULT_MANUAL_MARKER
        else:
            summary_manual_marker = str(summary_manual_marker_value)

        use_document_types = bool(entry.get("use_document_types"))
        document_manifest_value = entry.get("document_manifest")
        document_manifest_path: Optional[Path]
        if document_manifest_value:
            candidate = Path(str(document_manifest_value))
            document_manifest_path = (
                candidate
                if candidate.is_absolute()
                else (manifest_dir / candidate).resolve()
            )
        else:
            document_manifest_path = None

        assets_for_entry = entry.get("assets") or []
        resolved_assets_for_entry = _resolve_asset_paths(
            assets_for_entry, manifest_dir, path
        )
        logger.info("ℹ Assets für Eintrag aufgelöst: %s", resolved_assets_for_entry)

        # Resolve asset paths for copy_to_output assets
        assets_to_copy = [
            asset
            for asset in resolved_assets_for_entry
            if isinstance(asset, dict) and asset.get("copy_to_output")
        ]
        logger.info("ℹ Zu kopierende Assets: %s", assets_to_copy)

        pdf_options = entry.get("pdf_options") or {}
        variable_overrides = (
            _build_variable_overrides(pdf_options) if pdf_options else {}
        )
        abort_missing_glyph = pdf_options.get("abort_if_missing_glyph", True)
        color_override = pdf_options.get("emoji_color") if pdf_options else None
        bx_override = pdf_options.get("emoji_bxcoloremoji") if pdf_options else None
        if "emoji_color" in pdf_options or "emoji_bxcoloremoji" in pdf_options:
            entry_emoji_options = EmojiOptions(
                color=(
                    bool(color_override)
                    if color_override is not None
                    else emoji_options.color
                ),
                report=emoji_options.report,
                report_dir=emoji_options.report_dir,
                bxcoloremoji=(
                    bool(bx_override)
                    if bx_override is not None
                    else emoji_options.bxcoloremoji
                ),
            )
        else:
            entry_emoji_options = emoji_options

        ok, msg = build_pdf(
            path=path,
            out=out,
            typ=typ,
            use_summary=entry["use_summary"],
            use_book_json=entry.get("use_book_json", False),
            keep_combined=entry["keep_combined"],
            paper_format=args.paper_format,
            publish_dir=str(publish_dir_path),
            summary_mode=summary_mode,
            summary_order_manifest=summary_manifest_path,
            summary_manual_marker=summary_manual_marker,
            summary_appendices_last=_as_bool(entry.get("summary_appendices_last")),
            document_manifest=document_manifest_path if use_document_types else None,
            locale=(language_ctx.language_id if use_document_types else None),
            validate_doc_types=use_document_types,
            assets=assets_to_copy if assets_to_copy else None,
            emoji_options=entry_emoji_options,
            variables=variable_overrides or None,
            project_metadata=project_metadata,
            abort_if_missing_glyph=bool(abort_missing_glyph),
        )
        if ok:
            built.append(str((publish_dir_path / out).resolve()))
            # Reset publish-Flag (D) – nur bei Erfolg und wenn reset_build_flag true ist
            if entry.get("reset_build_flag", False):
                reset_tool = args.reset_script
                if os.path.exists(reset_tool):
                    try:
                        _run(
                            [
                                sys.executable or "python",
                                reset_tool,
                                "--path",
                                str(path),
                                "--multi",
                            ],
                            check=True,
                        )
                    except Exception as e:
                        logger.warning(
                            "Konnte reset-publish-flag nicht aufrufen: %s", e
                        )
                else:
                    # Fallback: direkt im Manifest auf false setzen
                    try:
                        data = _load_yaml(manifest)
                        for e in data.get("publish", []):
                            if str(e.get("path")) == original_path:
                                e["build"] = False
                        _save_yaml(manifest, data)
                    except Exception as e:
                        logger.warning(
                            "Konnte Manifest-Fallback-Reset nicht schreiben: %s", e
                        )
        else:
            failed.append(
                str((publish_dir_path / out).resolve()) + (f": {msg}" if msg else "")
            )

    # Outputs
    logger.info("::group::publisher.outputs")
    logger.info(
        json.dumps(
            {
                "built_count": len(built),
                "built_files": built,
                "failed_files": failed,
                "manifest": manifest,
            },
            ensure_ascii=False,
        )
    )
    logger.info("::endgroup::")

    _write_github_outputs(built, failed, manifest)

    # Exit-Code, wenn Builds fehlgeschlagen sind (aber nicht hart abbrechen, wenn ein Teil ok ist)
    if built and not failed:
        sys.exit(0)
    elif failed and not built:
        sys.exit(1)
    else:
        # Teilweise erfolgreich
        sys.exit(0)


if __name__ == "__main__":
    main()
