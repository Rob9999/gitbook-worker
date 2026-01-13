---
version: 1.0.0
date: 2026-01-10
history:
  - "init: 2026-01-10 add release procedure"
---

# Release Procedure

This guide describes the release workflow for hotfixes such as `release-v.2.0.6-hotfix`. It follows the specifications defined in `AGENTS.md` and the established release process.

## Preparations

* Ensure the repository is clean, all intended changes are committed and pushed, and **either**:

  * you are performing the release from a release-candidate branch and will merge back into `main` afterwards, **or**
  * all other repository work is paused until the release is completed.
* Activate the Python environment (`.venv`) and ensure Pandoc/TeX/Docker are available.
* Fonts must be provided via `defaults/fonts.yml` (see `AGENTS.md`).

## Steps

1. **Create Release Notes and Update Release Version**

   * Create a new file in `docs/releases/` with front matter (`version`, `date`, `status`, `history`), structured according to `docs/releases/v2.0.5.md`.
   * Release version format:
     `release-v.<Major>.<Minor>.<Patch>[-hotfix|-<NAME>]`
   * Release short version format:
     `<Major>.<Minor>.<Patch>.[post1]`
   * Set the release short version in `setup.cfg`, e.g.
     `version = 2.0.6.post1`
   * Set the release short version in `gitbook_worker/__init__.py`, e.g.
     `__version__ = "2.0.6.post1"`

2. **Local Orchestrator Runs**

   * Edit content.yaml first if you need to test a specific case (e.g. customer-de or another target). 
   > ⚠️ Warning / Caution: Never commit or push customer content, or a content.yaml file that references customer content.
   * Run at least:
     `python -m gitbook_worker.tools.workflow_orchestrator run --root <repo> --content-config content.yaml --lang de --profile local`
     and
     `python -m gitbook_worker.tools.workflow_orchestrator run --root <repo> --content-config content.yaml --lang en --profile local`
   * May verify the TOC using:
     `python -m gitbook_worker.tools.utils.pdf_toc_extractor --pdf [de|en|...]/publish/das-erda-buch.pdf --format text`
   * Human verification: If a PDF was generated, open and review it manually to confirm quality and uncover any unknown issues.
   * Fix blockers, address simple bugs, or create a backlog entry in `gitbook_worker/docs/backlog/` → involve the PO.

3. **Docker-based Orchestrator Runs**

   * Run:
     `python -m gitbook_worker.tools.docker.run_docker orchestrator --use-dynamic --profile default --content-config content.yaml --lang customer-de --isolated --logs-dir logs/docker`
   * Human verification: If a PDF was generated, open and review it manually to confirm quality and uncover any unknown issues.
   * Fix blockers, address simple bugs, or create a backlog entry in `gitbook_worker/docs/backlog/` → involve the PO.

4. **Run Tests**

   * Execute:
     `python -m pytest gitbook_worker/tests -m "not slow" -q`
   * Fix blockers, address simple bugs, or create a backlog entry in `gitbook_worker/docs/backlog/` → involve the PO.

5. **Repeat Until Green**

   * Iterate steps 2–4 until all runs and tests complete without errors.
   * Fix blockers, address simple bugs, or create a backlog entry in `gitbook_worker/docs/backlog/` → involve the PO.

6. **Pip Install Smoke Test**

   * Build the package:
     `python -m build`
   * In a fresh virtual environment:
     `python -m venv .venv-smoke && .\.venv-smoke\Scripts\activate && pip install dist/gitbook_worker-<ver>-py3-none-any.whl`
   * Run:
     `python -m gitbook_worker.tools.workflow_orchestrator --help`
     (verify banner output and exit code 0), optionally perform a dry run.
   * Fix blockers, address simple bugs, or create a backlog entry in `gitbook_worker/docs/backlog/` → involve the PO.

7. **Repeat Until Green**

   * If issues occur, return to step 2 and repeat the process.

8. **Tag & Push**

   * Tag format:
     `release-v.<Major>.<Minor>.<Patch>[-hotfix|-<NAME>]`, e.g. `release-v.2.0.6-hotfix`
   * Run:
     `git tag release-v.2.0.6-hotfix`
     `git push origin main --tags` (adjust branch if required).

## Documentation

* Record every deviation or blocker in the appropriate backlog entry (`gitbook_worker/docs/backlog/`).
* In the release notes, document tested commands, relevant fixes, and any remaining risks.

## Notes

* Do not use fonts outside of `fonts.yml`; the Docker setup pulls fonts exclusively from this file (see `Dockerfile.dynamic`).
* For LaTeX issues, set `ERDA_KEEP_LATEX_TEMP=1` and collect logs under `logs/`.
* Maintain SemVer consistency (`__version__` in `gitbook_worker/__init__.py` and packaging metadata).