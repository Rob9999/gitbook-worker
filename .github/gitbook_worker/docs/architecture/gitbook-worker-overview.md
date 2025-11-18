<!-- License: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) -->
---
version: 1.0.0
created: 2025-11-01
modified: 2025-11-10
status: stable
type: overview-documentation
license: CC BY 4.0
---

# `gitbook-worker` Package Overview

The `gitbook-worker` toolkit streamlines publishing, quality assurance and asset
management for the ERDA GitBook. The package is currently released as
**version&nbsp;0.1.0**, matching the `.github` automation environment that ships with this
repository.

## Capabilities at a Glance

| Area | Highlights | Primary README |
| --- | --- | --- |
| Workflow coordination | Profile-aware runner that executes publishing, conversion, QA and emoji steps defined in `publish.yml`. | [`tools/workflow_orchestrator/README.md`](../../tools/workflow_orchestrator/README.md) |
| Publishing pipeline | Incremental PDF builds, GitBook asset normalisation and manifest flag management. | [`tools/publishing/README.md`](../../tools/publishing/README.md) |
| CSV conversion | Discovers CSV assets, renders Markdown tables and charts, supports LaTeX-wide table helpers. | [`tools/converter/README.md`](../../tools/converter/README.md) |
| Quality audits | Link validation, source extraction, AI-assisted bibliography repair and Staatenprofil link monitoring. | [`tools/quality/README.md`](../../tools/quality/README.md) |
| Emoji tooling | Emoji usage scans, font inventory, inline asset replacement and reporting. | [`tools/emoji/README.md`](../../tools/emoji/README.md) |
| Support helpers | Appendix layout inspection for quick GitBook navigation checks. | [`tools/support/README.md`](../../tools/support/README.md) |
| Shared utilities | Subprocess, Docker and virtual-environment helpers reused across the suite. | [`tools/utils/README.md`](../../tools/utils/README.md) |

## Detailed Capability Breakdown

### Workflow coordination
The workflow orchestrator resolves manifest profiles, expands templates and
executes ordered steps, providing a single CLI entry point for CI and local
runs. It exposes options to dry-run builds, override manifests and target
specific step sequences while ensuring subprocess environments remain
consistent.【F:.github/gitbook_worker/tools/workflow_orchestrator/README.md†L1-L34】

### Publishing pipeline
Publishing scripts toggle manifest flags, regenerate GitBook-friendly assets and
render PDFs via Pandoc. Core entry points include `pipeline.py` for orchestrated
runs, `publisher.py` for targeted builds, and `gitbook_style.py` for renaming and
summary regeneration. Commands support dry-runs, emoji reporting and Pandoc
customisation through environment variables.【F:.github/gitbook_worker/tools/publishing/README.md†L1-L60】【F:.github/gitbook_worker/tools/publishing/README.md†L62-L90】

### CSV conversion
Converter utilities discover CSV asset folders next to manifest entries, produce
Markdown tables, and generate charts when numeric data is present. They offer
flags for heading depth, wide-format LaTeX wrappers and manifest scoping so
publishers can iterate quickly on datasets.【F:.github/gitbook_worker/tools/converter/README.md†L1-L37】【F:.github/gitbook_worker/tools/converter/README.md†L39-L57】

### Quality assurance
QA commands validate links and images, harvest source sections, repair
bibliographies with AI assistance and audit Staatenprofil HTTP references. They
integrate tightly with the workflow orchestrator, so new flags must remain
compatible with automation profiles.【F:.github/gitbook_worker/tools/quality/README.md†L1-L24】【F:.github/gitbook_worker/tools/quality/README.md†L26-L34】

### Emoji tooling
Emoji helpers scan Markdown for emoji usage, report CSS font declarations, inline
SVG/PNG assets for HTML output and generate coverage summaries. They are
routinely executed before publishing so editors can monitor typography changes
and emoji completeness.【F:.github/gitbook_worker/tools/emoji/README.md†L1-L26】【F:.github/gitbook_worker/tools/emoji/README.md†L28-L36】

### Support helpers
Support modules such as `appendix_layout_inspector.py` mirror historical tests to
surface the active summary mode and navigation order. They simplify debugging
GitBook appendix placement without running the full pipeline.【F:.github/gitbook_worker/tools/support/README.md†L1-L25】

### Shared utilities
Utility modules wrap subprocess execution, manage Docker builds and provide
on-demand virtual environments, ensuring consistent execution contexts across
the toolkit.【F:.github/gitbook_worker/tools/utils/README.md†L1-L32】

## How-To Reference

1. **Run the orchestrator** – `python -m tools.workflow_orchestrator --profile default --dry-run` lists the steps the worker
   will execute without modifying artefacts. See the
   [orchestrator README](../../tools/workflow_orchestrator/README.md) for
   advanced profile and step selection.【F:.github/gitbook_worker/tools/workflow_orchestrator/README.md†L8-L31】
2. **Publish PDFs** – Use `python .github/gitbook_worker/tools/publishing/pipeline.py --manifest publish.yml` to execute the incremental
   publishing flow, or call `python -m tools.publishing.publisher --dry-run` for a
   preview build. Additional usage examples live in the
   [publishing README](../../tools/publishing/README.md).【F:.github/gitbook_worker/tools/publishing/README.md†L12-L37】
3. **Regenerate CSV-derived artefacts** – `python -m tools.converter.convert_assets` refreshes tables and charts for changed
   entries. Consult the [converter README](../../tools/converter/README.md) for
   flag details such as `--wide` or manifest scoping.【F:.github/gitbook_worker/tools/converter/README.md†L9-L33】【F:.github/gitbook_worker/tools/converter/README.md†L35-L45】
4. **Audit Markdown quality** – Commands like `python -m tools.quality.link_audit` and `python -m tools.quality.sources` emit
   reports consumed by editors. Usage summaries and integration notes are
   documented in the [quality README](../../tools/quality/README.md).【F:.github/gitbook_worker/tools/quality/README.md†L7-L28】
5. **Inspect emoji coverage** – Run `python -m tools.emoji.scan_emojis` before publishing to update usage reports, following the
   guidance in the [emoji README](../../tools/emoji/README.md).【F:.github/gitbook_worker/tools/emoji/README.md†L7-L34】
6. **Verify appendix layout** – `python -m tools.support.appendix_layout_inspector --base-dir . --appendices-last` reports the
   resolved navigation order. Refer to the [support README](../../tools/support/README.md)
   for context and expected output.【F:.github/gitbook_worker/tools/support/README.md†L9-L23】

## Licensing

All documentation in this directory, including this overview, is distributed
under the Creative Commons Attribution 4.0 International license.
