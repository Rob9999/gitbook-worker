from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Iterable, List, Mapping, Any

from gitbook_worker.tools.logging_config import get_logger

logger = get_logger(__name__)

# Try to import SVG conversion libraries (prefer svglib, fallback to cairosvg)
HAS_SVGLIB = False
HAS_CAIROSVG = False

try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF

    HAS_SVGLIB = True
    logger.debug("svglib available for SVG conversion")
except (ImportError, OSError) as e:
    logger.debug("svglib not available: %s", e)

    try:
        import cairosvg

        HAS_CAIROSVG = True
        logger.debug("cairosvg available for SVG conversion")
    except (ImportError, OSError) as e:
        logger.debug("cairosvg not available: %s", e)


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
                        # Skip PDFs that were generated from SVGs in previous builds
                        if item.suffix.lower() == ".pdf":
                            svg_equivalent = item.with_suffix(".svg")
                            if svg_equivalent.exists():
                                logger.debug(
                                    "⏭️ Skipping %s (will be generated from %s)",
                                    item.name,
                                    svg_equivalent.name,
                                )
                                continue

                        rel_path = item.relative_to(asset_path)
                        dest_file = dest_dir / rel_path
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        logger.info(
                            "🔍 DEBUG copying asset file %s to %s", item, dest_file
                        )

                        # Convert SVG to PDF for LaTeX compatibility
                        if item.suffix.lower() == ".svg" and (
                            HAS_SVGLIB or HAS_CAIROSVG
                        ):
                            pdf_dest = dest_file.with_suffix(".pdf")
                            conversion_success = False

                            # Try svglib first (pure Python, no system dependencies)
                            if HAS_SVGLIB:
                                try:
                                    # Copy SVG to temp FIRST to isolate conversion
                                    temp_svg = dest_file
                                    temp_svg.parent.mkdir(parents=True, exist_ok=True)
                                    shutil.copy2(item, temp_svg)

                                    # Change working directory to temp to prevent pollution
                                    import os

                                    old_cwd = os.getcwd()
                                    try:
                                        os.chdir(temp_svg.parent)
                                        # Now convert from temp (svglib won't pollute content dir)
                                        drawing = svg2rlg(
                                            str(temp_svg.name)
                                        )  # Use relative path in temp
                                        if drawing:
                                            renderPDF.drawToFile(
                                                drawing, str(pdf_dest.name)
                                            )  # Use relative path
                                            logger.info(
                                                "🔄 Converted SVG to PDF (svglib): %s -> %s",
                                                item.name,
                                                pdf_dest.name,
                                            )
                                            conversion_success = True
                                        else:
                                            logger.warning(
                                                "⚠️ svglib could not parse %s", item.name
                                            )
                                    finally:
                                        os.chdir(old_cwd)
                                except Exception as e:
                                    logger.warning(
                                        "⚠️ svglib failed for %s: %s", item.name, e
                                    )

                            # Fallback to cairosvg if svglib failed
                            if not conversion_success and HAS_CAIROSVG:
                                try:
                                    # Convert from temp copy
                                    cairosvg.svg2pdf(
                                        url=str(dest_file), write_to=str(pdf_dest)
                                    )
                                    logger.info(
                                        "🔄 Converted SVG to PDF (cairosvg): %s -> %s",
                                        item.name,
                                        pdf_dest.name,
                                    )
                                    conversion_success = True
                                except Exception as e:
                                    logger.error(
                                        "❌ cairosvg failed for %s: %s", item.name, e
                                    )

                            if conversion_success:
                                # We have a PDF, optionally keep SVG copy too (already copied above)
                                if resolved_resource_paths is not None:
                                    resolved_resource_paths.append(str(pdf_dest))
                                files_copied += 1
                            else:
                                # Conversion failed, SVG already copied as fallback
                                logger.warning(
                                    "⚠️ All converters failed for %s, using SVG as-is",
                                    item.name,
                                )
                                if resolved_resource_paths is not None:
                                    resolved_resource_paths.append(str(dest_file))
                                files_copied += 1
                        elif item.suffix.lower() == ".svg":
                            # No conversion libraries available
                            logger.warning(
                                "⚠️ SVG file %s found but no converter available - "
                                "copying as-is (LaTeX will need Inkscape)",
                                item.name,
                            )
                            shutil.copy2(item, dest_file)
                            files_copied += 1
                            if resolved_resource_paths is not None:
                                resolved_resource_paths.append(str(dest_file))
                        else:
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
