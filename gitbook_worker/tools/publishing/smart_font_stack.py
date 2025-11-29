from __future__ import annotations

import atexit
import hashlib
import os
import shutil
import sys
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import yaml

from gitbook_worker.tools.logging_config import get_logger

from .font_config import FontConfig, FontConfigLoader, get_font_config

logger = get_logger(__name__)

__all__ = [
    "SmartFontError",
    "ResolvedFont",
    "SmartFontResult",
    "prepare_runtime_font_loader",
]


class SmartFontError(RuntimeError):
    """Raised when required fonts cannot be prepared."""


@dataclass(frozen=True)
class ResolvedFont:
    key: str
    name: str
    paths: Tuple[Path, ...]
    source: str
    downloaded: bool = False


@dataclass(frozen=True)
class SmartFontResult:
    loader: FontConfigLoader
    meta_path: Path
    resolved_fonts: Tuple[ResolvedFont, ...]
    downloads: int = 0


def prepare_runtime_font_loader(
    manifest_fonts: Optional[Sequence[Dict[str, str]]] = None,
    *,
    extra_search_paths: Optional[Sequence[Path]] = None,
    cache_dir: Optional[Path] = None,
    config_path: Optional[Path] = None,
    repo_root: Optional[Path] = None,
    allow_partial: bool = False,
    loader: Optional[FontConfigLoader] = None,
) -> SmartFontResult:
    """Ensure fonts exist locally and return a loader bound to a meta config."""

    stack = _SmartFontStack(
        manifest_fonts=manifest_fonts,
        extra_search_paths=extra_search_paths,
        cache_dir=cache_dir,
        config_path=config_path,
        repo_root=repo_root,
        loader=loader,
    )

    resolved = stack.resolve_fonts(allow_partial=allow_partial)
    meta_path = stack.write_meta_config(resolved)
    runtime_loader = FontConfigLoader(config_path=meta_path)
    return SmartFontResult(
        loader=runtime_loader,
        meta_path=meta_path,
        resolved_fonts=tuple(resolved),
        downloads=stack.downloads,
    )


class _SmartFontStack:
    def __init__(
        self,
        *,
        manifest_fonts: Optional[Sequence[Dict[str, str]]],
        extra_search_paths: Optional[Sequence[Path]],
        cache_dir: Optional[Path],
        config_path: Optional[Path],
        repo_root: Optional[Path],
        loader: Optional[FontConfigLoader],
    ) -> None:
        self._repo_root = _detect_repo_root(repo_root)
        self._cache_dir = _determine_cache_dir(cache_dir)
        self._manifest_fonts = list(manifest_fonts or [])
        self._search_paths = self._build_search_paths(extra_search_paths)
        self._work_dir = Path(tempfile.mkdtemp(prefix="gitbook-worker-fonts-"))
        self._cleaned = False
        atexit.register(self._cleanup)
        self.downloads = 0

        if loader is not None:
            base_loader = loader
        elif config_path is not None:
            base_loader = FontConfigLoader(Path(config_path))
        else:
            base_loader = get_font_config()

        if self._manifest_fonts:
            base_loader = base_loader.merge_manifest_fonts(list(self._manifest_fonts))

        self._loader = base_loader

    def resolve_fonts(self, allow_partial: bool = False) -> List[ResolvedFont]:
        resolved: List[ResolvedFont] = []
        missing: List[str] = []

        for key in self._loader.get_all_font_keys():
            font = self._loader.get_font(key)
            if not font:
                continue
            try:
                paths, downloaded = self._resolve_font_paths(key, font)
            except SmartFontError as exc:
                if allow_partial:
                    logger.warning(str(exc))
                    continue
                raise

            if not paths:
                if allow_partial:
                    logger.warning(
                        "Font %s (%s) konnte nicht gefunden werden.", key, font.name
                    )
                    continue
                missing.append(font.name or key)
                continue

            source = "downloaded" if downloaded else "existing"
            resolved.append(
                ResolvedFont(
                    key=key,
                    name=font.name or key,
                    paths=tuple(paths),
                    source=source,
                    downloaded=downloaded,
                )
            )

        if missing:
            raise SmartFontError("Missing fonts: " + ", ".join(sorted(missing)))

        return resolved

    def write_meta_config(self, fonts: Sequence[ResolvedFont]) -> Path:
        data = {
            "version": self._loader.version,
            "fonts": {},
        }

        for resolved_font in fonts:
            original = self._loader.get_font(resolved_font.key)
            if not original:
                continue
            data["fonts"][resolved_font.key] = {
                "name": original.name,
                "paths": [path.as_posix() for path in resolved_font.paths],
                "license": original.license,
                "license_url": original.license_url,
            }
            if original.source_url:
                data["fonts"][resolved_font.key]["source_url"] = original.source_url
            if original.download_url:
                data["fonts"][resolved_font.key]["download_url"] = original.download_url
            if original.sha256:
                data["fonts"][resolved_font.key]["sha256"] = original.sha256
            if original.version:
                data["fonts"][resolved_font.key]["version"] = original.version

        meta_path = self._work_dir / "fonts.meta.yml"
        with meta_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True)
        return meta_path

    def _cleanup(self) -> None:
        if self._cleaned:
            return
        try:
            shutil.rmtree(self._work_dir, ignore_errors=True)
        finally:
            self._cleaned = True

    def _build_search_paths(
        self, extra_search_paths: Optional[Sequence[Path]]
    ) -> List[Path]:
        paths: List[Path] = []
        repo_candidates = [
            self._repo_root / ".github" / "fonts",
            self._repo_root / "fonts",
        ]
        paths.extend(repo_candidates)

        os_specific = _system_font_directories()
        paths.extend(os_specific)

        if extra_search_paths:
            for raw in extra_search_paths:
                path = Path(raw)
                paths.append(path)

        deduped: List[Path] = []
        seen: set[Path] = set()
        for path in paths:
            try:
                resolved = path.resolve()
            except OSError:
                resolved = path
            if resolved in seen:
                continue
            seen.add(resolved)
            deduped.append(resolved)
        return deduped

    def _resolve_font_paths(
        self, key: str, font: FontConfig
    ) -> Tuple[List[Path], bool]:
        resolved: List[Path] = []

        path_candidates = self._expand_declared_paths(font)
        resolved.extend(path_candidates)

        if not resolved:
            resolved.extend(self._find_in_search_paths(font))

        downloaded = False
        if not resolved:
            downloaded_paths = self._download_font(key, font)
            if downloaded_paths:
                resolved.extend(downloaded_paths)
                downloaded = True

        resolved = [path for path in resolved if path.exists()]
        return resolved, downloaded

    def _expand_declared_paths(self, font: FontConfig) -> List[Path]:
        expanded: List[Path] = []
        for raw_path in font.paths:
            candidate = Path(raw_path)
            if not candidate.is_absolute():
                candidate = (self._repo_root / candidate).resolve()
            if candidate.is_file():
                expanded.append(candidate)
            elif candidate.is_dir():
                expanded.extend(self._collect_font_files(candidate))
        return expanded

    def _collect_font_files(self, directory: Path) -> List[Path]:
        results: List[Path] = []
        for extension in ("*.ttf", "*.otf", "*.ttc"):
            results.extend(directory.rglob(extension))
        return results

    def _find_in_search_paths(self, font: FontConfig) -> List[Path]:
        filenames = self._expected_filenames(font)
        matches: List[Path] = []
        for directory in self._search_paths:
            if not directory.exists():
                continue
            for name in filenames:
                candidate = directory / name
                if candidate.exists():
                    matches.append(candidate.resolve())
                    continue
                try:
                    found = next(directory.rglob(name))
                except StopIteration:
                    continue
                matches.append(found)
        return matches

    def _expected_filenames(self, font: FontConfig) -> List[str]:
        filenames: List[str] = []
        for raw in font.paths:
            name = Path(raw).name
            if name:
                filenames.append(name)
        if font.download_url:
            parsed = urllib.parse.urlparse(font.download_url)
            candidate = Path(parsed.path).name
            if candidate:
                filenames.append(candidate)
        return list(dict.fromkeys(filenames))

    def _download_font(self, key: str, font: FontConfig) -> List[Path]:
        if not font.download_url:
            return []

        target_dir = self._cache_dir / key.lower()
        target_dir.mkdir(parents=True, exist_ok=True)

        parsed = urllib.parse.urlparse(font.download_url)
        filename = Path(parsed.path).name
        if not filename:
            raise SmartFontError(f"Ungültige download_url für Font {font.name or key}")

        final_paths = self._maybe_existing_cache(target_dir, filename)
        if final_paths:
            return final_paths

        temp_path = target_dir / f"{filename}.part"
        try:
            _download_stream(font.download_url, temp_path)
        except urllib.error.URLError as exc:  # pragma: no cover - network issues
            raise SmartFontError(
                f"Download für Font {font.name or key} fehlgeschlagen: {exc}"
            ) from exc

        extracted = self._finalize_download(temp_path, target_dir, filename)
        self.downloads += 1

        if font.sha256:
            for candidate in extracted:
                _verify_sha256(candidate, font.sha256)

        return extracted

    def _maybe_existing_cache(self, target_dir: Path, filename: str) -> List[Path]:
        cached_file = target_dir / filename
        if cached_file.exists():
            return [cached_file]
        if filename.endswith((".zip", ".tar", ".tar.gz", ".tgz")):
            extracted_dir = target_dir / filename.rsplit(".", 1)[0]
            if extracted_dir.exists():
                return self._collect_font_files(extracted_dir)
        return []

    def _finalize_download(
        self, temp_path: Path, target_dir: Path, filename: str
    ) -> List[Path]:
        suffix = filename.lower()
        if suffix.endswith(".zip"):
            return self._extract_zip(temp_path, target_dir)
        if suffix.endswith((".tar", ".tar.gz", ".tgz")):
            return self._extract_tar(temp_path, target_dir)

        final_path = target_dir / filename
        temp_path.replace(final_path)
        return [final_path]

    def _extract_zip(self, archive_path: Path, target_dir: Path) -> List[Path]:
        extracted: List[Path] = []
        with zipfile.ZipFile(archive_path, "r") as archive:
            archive.extractall(target_dir)
        archive_path.unlink(missing_ok=True)
        extracted.extend(self._collect_font_files(target_dir))
        return extracted

    def _extract_tar(self, archive_path: Path, target_dir: Path) -> List[Path]:
        extracted: List[Path] = []
        with tarfile.open(archive_path, "r:*") as archive:
            archive.extractall(target_dir)
        archive_path.unlink(missing_ok=True)
        extracted.extend(self._collect_font_files(target_dir))
        return extracted


def _download_stream(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response, destination.open("wb") as target:
        shutil.copyfileobj(response, target)


def _verify_sha256(path: Path, expected_hash: str) -> None:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest.lower() != expected_hash.lower():
        path.unlink(missing_ok=True)
        raise SmartFontError(
            f"SHA256 mismatch for {path.name}: expected {expected_hash}, got {digest}"
        )


def _determine_cache_dir(explicit: Optional[Path]) -> Path:
    if explicit:
        resolved = Path(explicit).expanduser().resolve()
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved

    if sys.platform == "win32":
        root = os.getenv("LOCALAPPDATA") or (Path.home() / "AppData" / "Local")
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache"))

    cache_dir = Path(root) / "gitbook-worker" / "fonts"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _detect_repo_root(explicit: Optional[Path]) -> Path:
    if explicit:
        return Path(explicit).resolve()

    def _search(start: Path) -> Optional[Path]:
        for candidate in [start, *start.parents]:
            if (candidate / ".git").is_dir():
                return candidate
            if (candidate / "publish.yml").exists() or (
                candidate / "publish.yaml"
            ).exists():
                return candidate
            if (candidate / "book.json").exists():
                return candidate
        return None

    cwd_root = _search(Path.cwd().resolve())
    if cwd_root:
        return cwd_root

    module_root = _search(Path(__file__).resolve())
    if module_root:
        return module_root

    return Path(__file__).resolve().parent


def _system_font_directories() -> List[Path]:
    directories: List[Path] = []
    if sys.platform == "win32":
        windir = Path(os.getenv("WINDIR", "C:/Windows"))
        directories.append(windir / "Fonts")
        directories.append(
            Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts"
        )
    elif sys.platform == "darwin":
        directories.extend(
            [
                Path("/System/Library/Fonts"),
                Path("/Library/Fonts"),
                Path.home() / "Library" / "Fonts",
            ]
        )
    else:
        directories.extend(
            [
                Path.home() / ".local" / "share" / "fonts",
                Path("/usr/local/share/fonts"),
                Path("/usr/share/fonts"),
            ]
        )

    texmf = Path.home() / "texmf-local" / "fonts"
    directories.append(texmf)
    directories.append(Path("/var/cache/gitbook-worker/fonts"))
    return directories
