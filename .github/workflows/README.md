# GitHub Actions Workflows

Continuous integration, testing and publishing workflows for the project.

## Active Workflows

### `orchestrator.yml` (Main CI/CD Pipeline)
**Trigger:** Push to any branch, manual dispatch  
**Purpose:** Main publishing and deployment pipeline

- Builds Docker image from `.github/gitbook_worker/tools/docker/Dockerfile`
- Executes `workflow_orchestrator` CLI with configured profile
- Supports multiple profiles via `publish.yml`:
  - `default`: Full pipeline (check, convert, publish)
  - `local`: Local development (convert, publish only)
  - `publisher`: Publish-only mode

**Manual execution:**
```bash
# In GitHub Actions UI
Actions → Orchestrator → Run workflow → Select profile
```

**Local execution:**
```bash
cd .github
python -m venv .venv
.venv/Scripts/Activate.ps1  # or source .venv/bin/activate on Linux
pip install -e .
python -m tools.workflow_orchestrator --profile default --manifest ../publish.yml
```

### `test.yml` (Test Suite)
**Trigger:** Pull requests, manual dispatch  
**Purpose:** Comprehensive test suite for code quality and compliance

Test suites available:
- **unit**: Fast unit tests for `gitbook_worker` package
- **integration**: PDF integration tests with Pandoc/LaTeX
- **emoji-harness**: Emoji/font compliance and licensing checks
- **qa**: Documentation quality assurance (link audits, sources)
- **all**: Run all test suites

**Manual execution:**
```bash
# In GitHub Actions UI
Actions → Tests → Run workflow → Select test suite
```

## Orchestrator Steps

The orchestrator executes steps defined in `publish.yml` profiles:

| Step | Purpose | Implementation |
|------|---------|----------------|
| `check_if_to_publish` | Detects which PDFs need rebuilding | `tools/publishing/set_publish_flag.py` |
| `ensure_readme` | Creates missing readme.md files | Built into orchestrator |
| `update_citation` | Updates citation.cff metadata | Built into orchestrator |
| `converter` | Converts CSV assets to Markdown/diagrams | `tools/converter/convert_assets.py` |
| `engineering-document-formatter` | Ensures YAML front matter | Built into orchestrator |
| `publisher` | Builds PDFs via Pandoc | `tools/publishing/pipeline.py` |

## Architecture

```
GitHub Actions Trigger
        ↓
orchestrator.yml
        ↓
   Docker Image
        ↓
workflow_orchestrator CLI
        ↓
   publish.yml (profile selection)
        ↓
Individual steps (tools/*)
```

## Migration Notes

This workflow structure consolidates 13 legacy workflows into 2 workflows:
- See `MIGRATION-PLAN.md` for details on the consolidation
- All functionality from legacy workflows is preserved
- Legacy workflows removed: check-if-to-publish.yml, converter.yml, ensure-readme.yml, 
  update_citation.yml, engineering-document-formatter.yml, gitbook-style.yml, 
  publisher.yml, emoji-pdf-harness.yml, pdf-integration.yml, python-package.yml, qa.yml
