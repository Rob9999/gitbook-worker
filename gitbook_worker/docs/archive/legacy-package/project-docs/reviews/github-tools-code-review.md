# `.github/gitbook_worker/tools` code review – 2025-05

## Scope

Evaluated the Python automation housed under `.github/gitbook_worker/tools`, with emphasis on
workflow orchestration, publishing, conversion and QA modules. Documentation and
supporting Docker images were reviewed alongside the implementation.

## Highlights

* **Modular architecture** – The orchestrator cleanly delegates to specialised
  modules (`publishing`, `converter`, `quality`, `emoji`).  Steps compose via a
  thin runner that keeps subprocess environments consistent.
* **Pandoc integration** – `publishing/publisher.py` honours manifest-specific
  overrides and surfaces emoji-related options that align with GitBook output.
* **CSV conversion** – Converter utilities encapsulate Markdown and chart
  rendering logic, making them reusable both in CI and for one-off local runs.

## Improvement opportunities

1. **Setup automation** – Introduce `.github/setup-dev.sh` and `.ps1` helpers to
   reduce the manual steps required when onboarding contributors.
2. **Secret naming** – Workflows still reference historical PAT names; replace
   them with repo-specific placeholders and document the required secrets per
   environment.
3. **Test coverage** – Add regression tests covering orchestrator profile
   resolution, converter template handling and emoji report generation.
4. **Error reporting** – Harmonise logging output (structured JSON vs. plain
   text) so downstream automation can parse failures reliably.
5. **Docker parity** – Ensure the published Docker images are rebuilt whenever
   new fonts or LaTeX packages are added, and document the cadence in the module
   READMEs.

## Next steps

* Track documentation updates through the refreshed module READMEs.
* Capture sprint planning or follow-up items under
  `.github/gitbook_worker/project/docs/sprints/`.
* Revisit the recommendations above once new tests and setup scripts have been
  added.
