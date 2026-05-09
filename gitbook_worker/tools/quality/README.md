# Quality Assurance Tools

Command-line utilities that audit Markdown sources, repair references and
produce reports for editors.

## Commands

| Command | Summary |
| --- | --- |
| `python -m gitbook_worker.tools.quality.link_audit` | Validates external links, image references, heading collisions and TODO markers. Outputs logs or CSV reports depending on flags. |
| `python -m gitbook_worker.tools.quality.profile_link_audit` | Scans Markdown files matching configurable filename patterns such as `*profile*.md` and emits a CSV report with failing HTTP checks. |
| `python -m gitbook_worker.tools.quality.sources` | Extracts "Quellen"/"Sources" sections into a CSV file to simplify bibliography reviews. |
| `python -m gitbook_worker.tools.quality.ai_references` | Uses AI assistance to validate bibliography entries referenced in `SUMMARY.md`. Writes a redacted JSON report by default; applies accepted updates only with `--apply`. Supports OpenAI-compatible, Gemini/GenAI and Mistral providers, provider throttling via `--requests-per-minute`, `--min-request-interval` and `--throttle-jitter`, plus adaptive 429 retry backoff using `Retry-After` headers. |
| `python -m gitbook_worker.tools.quality.staatenprofil_links` | Legacy alias for `profile_link_audit --filename-pattern *staatenprofil*.md`. |

Pass `--help` to any command for detailed arguments.

## Workflow integration

These tools are consumed by the workflow orchestrator.  Ensure new flags or exit
codes remain backwards compatible with the steps defined in
`workflow_orchestrator/profiles.py`.

## Development checklist

1. Add unit tests in `gitbook_worker/tests` when extending behaviour.
2. Avoid network calls in tests—use fixtures or recorded responses.
3. Document any new reports or CSV schemas here so downstream scripts stay in
   sync.
