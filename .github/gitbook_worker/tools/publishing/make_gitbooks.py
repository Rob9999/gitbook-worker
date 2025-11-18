# make gitbook style documentation
# 1. run gitbook_style.py to convert markdown files to gitbook style
# 2. runf publisher.py to publish the gitbook style files to github pages

import sys
from gh_paths import REPO_ROOT, GH_TOOLS_DIR
from tools.utils.run import run as run_command
from tools.logging_config import get_logger

logger = get_logger(__name__)


def main():
    logger.info("Starting GitBook documentation publishing process")
    # Rename files to GitBook style
    renaming_dir = REPO_ROOT
    logger.info(f"Renaming files to GitBook style: {renaming_dir}")
    run_command(
        [
            "python",
            f'{GH_TOOLS_DIR / "publishing" / "gitbook_style.py"}',
            "rename",
            "--root",
            f"{renaming_dir}",
        ]
    )
    logger.info("File renaming to GitBook style completed")
    # Ensure clean GitBook summary
    logger.info(f"Ensuring clean GitBook summary in: {renaming_dir}")
    run_command(
        [
            "python",
            f"{GH_TOOLS_DIR / 'publishing' / 'gitbook_style.py'}",
            "summary",
            "--root",
            f"{REPO_ROOT}",
        ]
    )

    # Publish to GitHub Pages
    manifest_path = REPO_ROOT / "publish.yml"
    logger.info(f"Publishing to GitHub Pages using manifest: {manifest_path}")
    run_command(
        [
            "python",
            f"{GH_TOOLS_DIR / 'publishing' / 'publisher.py'}",
            f"--manifest={manifest_path}",
        ]
    )

    logger.info("GitBook documentation publishing process completed")


if __name__ == "__main__":
    main()
