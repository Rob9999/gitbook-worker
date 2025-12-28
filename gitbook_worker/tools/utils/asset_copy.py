from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Iterable, List, Mapping, Any

from gitbook_worker.tools.logging_config import get_logger

logger = get_logger(__name__)


def copy_assets_to_temp(
    tmp_md: Path,
    folder: Path,
    assets: Iterable[Mapping[str, Any]],
    resolved_resource_paths: List[str] = None,
) -> None:
    """Copy configured assets next to the temporary Markdown file.

    Keeps GitBook-style `.gitbook/assets` layout intact so Pandoc can resolve
    images relative to the temporary file. Non-content files are skipped.
    """

    logger.info("🔍 DEBUG assets parameter: %s", assets)
    temp_dir = Path(tmp_md).parent
    folder_path = Path(folder).resolve()
    manifest_dir = folder_path.parent if folder_path.is_file() else folder_path
    logger.info("🔍 DEBUG manifest_dir: %s", manifest_dir)

    for asset_config in assets:
        asset_path_str = asset_config.get("path")
        if not asset_path_str:
            continue

        asset_path = Path(asset_path_str)
        logger.info("🔍 DEBUG asset_path: %s", asset_path)

        if not asset_path.is_absolute():
            asset_path = (manifest_dir / asset_path).resolve()
            logger.info("🔍 DEBUG resolved asset_path: %s", asset_path)

        if not asset_path.exists():
            logger.warning("⚠️ Asset not found (copy_to_output): %s", asset_path)
            continue

        if asset_path.is_dir():
            if asset_path.name == "assets" and asset_path.parent.name == ".gitbook":
                dest_dir = temp_dir / ".gitbook" / "assets"
                dest_dir.mkdir(parents=True, exist_ok=True)
                files_copied = 0
                for item in asset_path.rglob("*"):
                    if item.is_file():
                        rel_path = item.relative_to(asset_path)
                        dest_file = dest_dir / rel_path
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        logger.info(
                            "🔍 DEBUG copying asset file %s to %s", item, dest_file
                        )
                        shutil.copy2(item, dest_file)
                        files_copied += 1
                        if resolved_resource_paths is not None:
                            resolved_resource_paths.append(str(dest_file))
                logger.info(
                    "📋 Copied %d files from %s to temp", files_copied, asset_path
                )
            else:
                logger.debug("Skipping non-.gitbook/assets directory: %s", asset_path)
            continue

        if asset_path.is_file():
            try:
                rel_to_content = asset_path.relative_to(folder_path / "content")
                dest_file = temp_dir / rel_to_content
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(asset_path, dest_file)
                if resolved_resource_paths is not None:
                    resolved_resource_paths.append(str(dest_file))
                logger.info(
                    "📋 Copied asset file: %s -> %s", asset_path.name, dest_file
                )
            except ValueError:
                logger.debug("Asset not in content directory, skipping: %s", asset_path)
