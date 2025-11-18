# Quality Assurance Tools

Command-line utilities that audit Markdown sources, repair references and
produce reports for editors.

## Commands

| Command | Summary |
| --- | --- |
| `python -m tools.quality.link_audit` | Validates external links, image references, heading collisions and TODO markers. Outputs logs or CSV reports depending on flags. |
| `python -m tools.quality.sources` | Extracts "Quellen"/"Sources" sections into a CSV file to simplify bibliography reviews. |
| `python -m tools.quality.ai_references` | Uses AI assistance to validate and repair bibliography entries referenced in `SUMMARY.md`. Writes a JSON report with accepted updates. |
| `python -m tools.quality.staatenprofil_links` | Scans Markdown files matching `*staatenprofil*.md` and emits a CSV report with failing HTTP checks. |

Pass `--help` to any command for detailed arguments.

## Workflow integration

These tools are consumed by the workflow orchestrator.  Ensure new flags or exit
codes remain backwards compatible with the steps defined in
`workflow_orchestrator/profiles.py`.

## Development checklist

1. Add unit tests in `.github/tests/quality` when extending behaviour.
2. Avoid network calls in tests—use fixtures or recorded responses.
3. Document any new reports or CSV schemas here so downstream scripts stay in
   sync.
