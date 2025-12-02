from __future__ import annotations

import hashlib
import shutil
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Optional

from gitbook_worker.tools.logging_config import get_logger

logger = get_logger(__name__)


class FontStorageError(RuntimeError):
    """Raised when repository font storage cannot be prepared."""


@dataclass(frozen=True)
class FontBundleSpec:
    slug: str
    version: str
    url: str
    required_files: Mapping[str, Optional[str]]
    license_files: Mapping[str, str] = field(default_factory=dict)
    description: str = ""


class FontStorageBootstrapper:
    """Ensures that repository-managed font bundles exist locally."""

    def __init__(
        self, storage_root: Path, bundles: Iterable[FontBundleSpec] | None = None
    ) -> None:
        self._storage_root = storage_root
        self._bundles = (
            list(bundles) if bundles is not None else list(_DEFAULT_FONT_BUNDLES)
        )

    def ensure_defaults(self) -> Path:
        self._storage_root.mkdir(parents=True, exist_ok=True)
        for bundle in self._bundles:
            self._ensure_bundle(bundle)
        return self._storage_root

    def _ensure_bundle(self, spec: FontBundleSpec) -> None:
        target_dir = self._storage_root / spec.slug
        target_dir.mkdir(parents=True, exist_ok=True)
        missing = self._missing_required_files(target_dir, spec.required_files)
        if not missing:
            return
        logger.info(
            "Downloading %s font bundle (version %s) to %s",
            spec.slug,
            spec.version,
            target_dir,
        )
        self._download_bundle(spec, target_dir)

    def _missing_required_files(
        self, directory: Path, required_files: Mapping[str, Optional[str]]
    ) -> list[str]:
        missing: list[str] = []
        for filename, expected_hash in required_files.items():
            candidate = directory / filename
            if not candidate.exists():
                missing.append(filename)
                continue
            if expected_hash and not self._verify_sha(candidate, expected_hash):
                logger.warning("Checksum mismatch for %s, will re-download", candidate)
                missing.append(filename)
        return missing

    def _download_bundle(self, spec: FontBundleSpec, target_dir: Path) -> None:
        with tempfile.TemporaryDirectory(
            prefix=f"gitbook-font-{spec.slug}-"
        ) as tmp_dir:
            tmp_path = Path(tmp_dir)
            archive_name = (
                Path(urllib.parse.urlparse(spec.url).path).name or f"{spec.slug}.zip"
            )
            archive_path = tmp_path / archive_name
            try:
                _download_file(spec.url, archive_path)
            except urllib.error.URLError as exc:
                raise FontStorageError(
                    f"Download for {spec.slug} fonts failed: {exc.reason if hasattr(exc, 'reason') else exc}"
                ) from exc

            extracted_root = self._extract_archive(archive_path)
            for filename, expected_hash in spec.required_files.items():
                source = self._find_in_archive(extracted_root, filename)
                if not source:
                    raise FontStorageError(
                        f"Could not locate {filename} inside bundle {spec.slug}"
                    )
                destination = target_dir / filename
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                if expected_hash:
                    self._assert_sha(destination, expected_hash)

            for source_name, target_name in spec.license_files.items():
                source = self._find_in_archive(extracted_root, source_name)
                if not source:
                    raise FontStorageError(
                        f"Could not locate {source_name} (license) inside bundle {spec.slug}"
                    )
                destination = target_dir / target_name
                shutil.copy2(source, destination)

    def _extract_archive(self, archive_path: Path) -> Path:
        suffix = archive_path.suffix.lower()
        parent = archive_path.parent
        if suffix == ".zip":
            with zipfile.ZipFile(archive_path, "r") as archive:
                archive.extractall(parent)
        elif suffix in {".tar", ".gz", ".tgz", ".bz2"}:
            with tarfile.open(archive_path, "r:*") as archive:
                archive.extractall(parent)
        else:
            raise FontStorageError(
                f"Unsupported font archive format: {archive_path.name}"
            )
        archive_path.unlink(missing_ok=True)
        return parent

    def _find_in_archive(self, root: Path, filename: str) -> Optional[Path]:
        try:
            return next(root.rglob(filename))
        except StopIteration:
            return None

    def _verify_sha(self, path: Path, expected_hash: str) -> bool:
        return path.exists() and self._checksum(path) == expected_hash.lower()

    def _assert_sha(self, path: Path, expected_hash: str) -> None:
        if not self._verify_sha(path, expected_hash):
            path.unlink(missing_ok=True)
            raise FontStorageError(
                f"Checksum verification failed for {path.name}: expected {expected_hash}"
            )

    def _checksum(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest().lower()


def _download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response, destination.open("wb") as target:
        shutil.copyfileobj(response, target)


_DEFAULT_FONT_BUNDLES: tuple[FontBundleSpec, ...] = (
    FontBundleSpec(
        slug="dejavu",
        version="2.37",
        url="https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip",
        required_files={
            "DejaVuSans.ttf": "7da195a74c55bef988d0d48f9508bd5d849425c1770dba5d7bfc6ce9ed848954",
            "DejaVuSansMono.ttf": "b4a6c3e4faab8773f4ff761d56451646409f29abedd68f05d38c2df667d3c582",
            "DejaVuSerif.ttf": "42d1edeb7952f31b1f96d767ed7030b08a39e0c372b0071641518864e2bffb51",
        },
        license_files={"LICENSE": "LICENSE.txt"},
        description="Baseline serif/sans/mono trio required for PDF output",
    ),
    FontBundleSpec(
        slug="twitter-color-emoji",
        version="15.1.0",
        url="https://github.com/13rac1/twemoji-color-font/releases/download/v15.1.0/TwitterColorEmoji-SVGinOT-15.1.0.zip",
        required_files={
            "TwitterColorEmoji-SVGinOT.ttf": None,  # Checksum validation will be added after first download
        },
        license_files={"LICENSE.md": "LICENSE.txt"},
        description="Twitter Color Emoji font with SVG-in-OpenType color glyphs (CC BY 4.0)",
    ),
)
