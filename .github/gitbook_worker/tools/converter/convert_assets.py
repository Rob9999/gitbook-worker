#!/usr/bin/env python3
"""Batch convert CSV assets to Markdown tables and charts.

Reads ``publish.yml`` (from repo root or legacy docs/public location) to discover
published paths and converts any CSV files found in sibling assets directories.
For each CSV the table is written to ``assets/tables`` and, if a matching template
exists under ``assets/templates``, the table is also copied to the template's
target path. If numeric columns exist, a chart is written to ``assets/diagrams``.
"""
from pathlib import Path
import argparse

import pandas as pd
import yaml
from tools.logging_config import get_logger

from tools.utils.smart_manifest import resolve_manifest

from .csv2md_and_chart import save_chart, save_markdown

logger = get_logger(__name__)

try:
    from gh_paths import REPO_ROOT
except ImportError:
    logger.warning(
        "Failed to gather directories from python tree. Falling back to manual resolution."
    )
    REPO_ROOT = Path(__file__).resolve().parents[2]
    logger.info("REPO_ROOT : %s", REPO_ROOT)

# PUBLIC, TEMPLATES and MANIFEST will be populated at runtime so the converter
# can be used against any repository layout. They are set by main() using the
# provided --manifest CLI option or by resolving a manifest with the smart
# manifest rules.
MANIFEST = None
PUBLIC = None
TEMPLATES = None


def discover_asset_dirs() -> set:
    cfg = yaml.safe_load(MANIFEST.read_text())
    assets = set()
    for item in cfg.get("publish", []):
        rel = item.get("path")
        if not rel:
            continue
        target = (PUBLIC / rel).resolve()
        if target.is_file():
            target = target.parent
        cand = (target.parent / "assets").resolve()
        if cand.is_dir():
            assets.add(cand)
    return assets


def convert_csv(csv_path: Path, assets_dir: Path):
    df = pd.read_csv(csv_path)
    out_md = assets_dir / "tables" / f"{csv_path.stem}.md"
    note = f"Quelle: {csv_path.name}"
    save_markdown(df, out_md, note=note)

    table_tpl = TEMPLATES / "table.md"
    if table_tpl.is_file():
        logger.info(
            "Found template for %s: %s, producing markdown table from template",
            csv_path.name,
            table_tpl,
        )
        # read and process template
        tpl_text = table_tpl.read_text()
        # simple templating: replace {table} and {table-title}
        out_text = tpl_text.replace("{table}", out_md.read_text())
        table_title = csv_path.stem.replace("-", " ").replace("_", " ").title()
        out_text = out_text.replace("{table-title}", table_title)
        # get target path from template front matter
        front_matter = yaml.safe_load(out_text.split("---", 2)[1])
        target_str = front_matter.get("target") if front_matter else ""
        target_path = Path(target_str) if target_str else None
        logger.info("Determined target: %s", target_path)
        if target_path:
            if not target_path.is_absolute():
                target_path = (PUBLIC / target_path).resolve()
            target_dir = target_path.parent
            logger.info("Resolved target directory: %s", target_dir)
            existing = list(target_dir.glob(f"table-*-{csv_path.stem}.md"))
            if existing:
                # overwrite existing file
                table_path = existing[0]
                # extract table number from existing file name
                table_number = table_path.stem.split("-")[1]
                out_text = out_text.replace("{table-number}", table_number)
                logger.info("Overwriting existing table file: %s", table_path)
                table_path.write_text(out_text)
            else:
                # get count of "table-*" files in target directory
                count = len(list(target_dir.glob("table-*.md")))
                # replace table-number
                out_text = out_text.replace("{table-number}", f"{count + 1:02d}")
                table_path = target_dir / f"table-{count + 1}-{csv_path.stem}.md"
                table_path.parent.mkdir(parents=True, exist_ok=True)
                logger.info(
                    "Writing table %s templated with %s to %s",
                    csv_path.name,
                    table_tpl,
                    table_path,
                )
                # write processed markdown table template to target
                table_path.write_text(out_text)
    num_cols = [c for c in df.columns[1:] if pd.api.types.is_numeric_dtype(df[c])]
    if num_cols:
        out_png = assets_dir / "diagrams" / f"{csv_path.stem}.png"
        save_chart(df, out_png, x=df.columns[0], y_cols=num_cols)


def main():
    parser = argparse.ArgumentParser(
        description="Convert CSV assets to markdown and charts."
    )
    parser.add_argument(
        "--manifest",
        help="Path to publish.yml (defaults to repo root or legacy location)",
    )
    args = parser.parse_args()

    manifest_path = resolve_manifest(explicit=args.manifest, cwd=Path.cwd(), repo_root=REPO_ROOT)
    global MANIFEST, PUBLIC, TEMPLATES
    MANIFEST = manifest_path
    PUBLIC = manifest_path.parent
    TEMPLATES = PUBLIC / "assets" / "templates"

    for assets in discover_asset_dirs():
        csv_dir = assets / "csvs"
        if not csv_dir.is_dir():
            continue
        for csv_file in csv_dir.glob("*.csv"):
            convert_csv(csv_file, assets)


if __name__ == "__main__":
    main()
