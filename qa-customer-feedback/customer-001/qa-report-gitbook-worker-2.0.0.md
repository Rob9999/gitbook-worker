# QA Report: gitbook_worker v2.0.0 (Initial Consumer Test)

## Context
- Consumer repo: erda-book (branch: release_candidate)
- Package under test: gitbook_worker v2.0.0 (vendored tarball, installed via `pip install gitbook-worker @ file:packages/gitbook-worker/gitbook-worker-2.0.0.tar.gz`)
- Host OS: Windows (Python 3.11.3)
- Invocation: `python -m gitbook_worker.tools.workflow_orchestrator run --root . --manifest de/publish.yml --profile local --lang de`

## Observed Behavior
- Orchestrator resolves `repo_root` incorrectly to the site-packages path (`<site-packages>`), not the working copy (`<consumer-repo>`).
- Because `gitbook_worker/tools` is not present in the working copy, `tools_dir` is set to the site-packages copy, but pipeline and converter scripts are still not found, leading to skipped steps.
- Log excerpt:
  - `INFO Repository Root   :  <site-packages>`
  - `WARNING Konverter-Skripte nicht gefunden – Schritt wird übersprungen`
  - `WARNING pipeline.py nicht gefunden – Schritt wird übersprungen`
  - No PDF output produced; orchestrator exits 0 but does nothing.

  ### Tarball vs. installed package
  - The release tarball **does contain** `gitbook_worker/tools` (incl. `publishing/pipeline.py`) and `defaults/`.
  - The installed package in `site-packages` still reports missing pipeline/converter, suggesting the packaged install path is not used (or the wheel excludes tools).

  ### After extracting tools into the consumer repo
  - Extracted `gitbook_worker` from the tarball into `./gitbook_worker/` and ran with `PYTHONPATH=./gitbook_worker`.
  - Orchestrator still mis-detects `Repository Root` as `./gitbook_worker` (package dir), and still logs “pipeline.py nicht gefunden”.
  - Direct pipeline call works (see below), so the files are present and executable; the orchestrator’s discovery logic remains broken when run as installed package.

  ### Direct pipeline run (workaround)
  - Command: `PYTHONPATH=./gitbook_worker python -m gitbook_worker.tools.publishing.pipeline --root <consumer-repo> --manifest <consumer-repo>/de/publish.yml`
  - Behavior: pipeline runs and executes GitBook style rename on the content tree, changing file names (README→readme, SUMMARY→summary, license files lowercased, etc.).
  - Failure: publisher aborts with `project.license fehlt – bitte in publish.yml unter project.license setzen` (exit status 3). No PDF produced.
  - Side effect: mass renames in `de/` (book content). This is destructive unless reverted.

## Expected Behavior
- `--root .` should resolve to the working tree (`<consumer-repo>`).
- Orchestrator should locate `gitbook_worker/tools/publishing/pipeline.py` and run converter/publisher steps, producing the PDFs under `de/publish`.

## Suspected Root Causes
- `detect_repo_root` in `gitbook_worker.tools.utils.smart_manifest` (called by orchestrator) appears to walk up from the current working directory of the running process; when executed from site-packages context, it prefers that location.
- Package layout assumes `gitbook_worker/` (with `tools/`) exists in the repo; the published wheel/tarball installs code into site-packages but leaves no project-level `gitbook_worker` directory for scripts.
- `RuntimeContext` sets `tools_dir` to `gitbook_worker/tools` under `repo_root`; if `repo_root` is misdetected, pipeline paths will be wrong.

## Impact
- Out-of-the-box local runs on consumer repositories fail to produce outputs.
- CI workflows that rely on the packaged orchestrator (without copying `gitbook_worker/tools` into the repo) will no-op while returning exit code 0, hiding failures.

## Minimal Reproduction Steps
1. Install the package from the vendored tarball.
2. From a repo **without** `gitbook_worker/` sources checked in, run:
   `python -m gitbook_worker.tools.workflow_orchestrator run --root . --manifest de/publish.yml --profile local --lang de`
3. Observe root resolution to site-packages and skipped converter/publisher steps.

## Recommendations to Package Supplier
1. **Repo root detection**: Ensure `detect_repo_root` respects the provided `--root` argument as authoritative, not site-packages. If `--root` is relative, resolve from `cwd` but default to the caller’s working dir, not the package install dir.
2. **Tools discovery**: When `gitbook_worker/tools` is absent in the working tree, fall back to the installed package’s `tools` directory explicitly (e.g., `import gitbook_worker; Path(gitbook_worker.__file__).parent / "tools"`).
3. **Fail fast**: If `pipeline.py` or converter scripts are missing, exit non-zero with a clear hint instead of silently skipping. Include guidance: “Install package with tools, or vend `gitbook_worker/tools` into the repo.”
4. **Packaging layout**: Consider shipping `tools/` and defaults as package data and reference them via package-relative paths, so consumers do not need to copy sources into their repos.
5. **Logging**: Add a one-line summary when steps are skipped due to missing scripts, including the resolved `tools_dir` path.
6. **Docs**: Document that `gitbook_worker/tools` must be available (either packaged or vendored) and show a minimal setup recipe for consumers who only pip-install the release tarball.

### Additional QA findings
- Orchestrator remains non-functional even after vendoring tools and setting `PYTHONPATH` because it still fails the pipeline existence check (false negative) and picks `repo_root` as the package directory.
- The direct pipeline entrypoint runs but enforces GitBook-style renames and fails hard if `project.license` is missing in `publish.yml` (no graceful guidance). This creates mass file renames in the content tree.
- Recommendation: Provide a “safe mode” or dry-run that reports required metadata before mutating the tree; gate renames behind an explicit flag.

## Hotfix v2.0.1 (release-v.2.0.1-hotfix)
- Assets: release has no packaged wheel/tarball assets; downloaded source tarball via `https://api.github.com/repos/Rob9999/gitbook-worker/tarball/release-v.2.0.1-hotfix` and installed from `packages/gitbook-worker/gitbook-worker-2.0.1-hotfix.tar.gz`.
- Install: `pip install -r requirements.txt` upgrades gitbook-worker to 2.0.1.
- Validate run (safe): `python -m gitbook_worker.tools.workflow_orchestrator validate --root . --manifest de/publish.yml --profile local --lang de` → returns success.
- Observation: Logs still show `Repository Root : <site-packages>` even with `--root .`, so root logging remains confusing; however, validation succeeds and does not mutate content.
- Not yet rerun `run`/`pipeline` to avoid destructive renames; awaiting confirmation that new root handling is truly fixed before executing publish steps.

### Latest orchestrator run (2025-12-29, 2.0.1-hotfix)
- Command: `python -m gitbook_worker.tools.workflow_orchestrator run --root <consumer-repo> --manifest de/publish.yml --profile local --lang de`
- Result: step `converter` fails; `tools.converter.convert_assets` looks for `docs/public/publish.yml` (FileNotFoundError). Upstream path leak in stacktrace: a vendor-specific path inside `.github/tools/converter/convert_assets.py` was used instead of the installed package path.
- Publisher not executed; exit code 1. Logs at `<consumer-repo>/misc/desktop/qa-reports-for-supplier/workflow.log`.
- Root logging still reports `Repository Root : C:\Python311\Lib\site-packages` despite `--root C:/RAMProjects/ERDA`.

## Temporary Workaround for Consumers
- Extracted `gitbook_worker/` from the tarball into the repo and set `PYTHONPATH=./gitbook_worker`. This enables the direct pipeline entrypoint.
- Run pipeline directly (bypassing orchestrator): `PYTHONPATH=./gitbook_worker python -m gitbook_worker.tools.publishing.pipeline --root <repo> --manifest <repo>/de/publish.yml`. **Caveat:** this mutates the repo (GitBook style renames) and currently fails because `project.license` is missing in `publish.yml`.

## Next Steps (from consumer side)
- Await supplier fix; current workaround is destructive (renames) and still blocked by missing `project.license` metadata. Will pause further runs until guidance or a patched package is available.
