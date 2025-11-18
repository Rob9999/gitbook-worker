# Test Workspace

This is a test workspace for the GitBook orchestrator pipeline tests.

## Purpose

This workspace contains anonymized test data to verify that the orchestrator:
- Does not delete any files during the `ensure_readme` step
- Preserves all markdown files
- Respects configuration from `publish.yml`
- Only creates READMEs in directories without existing README variants

## Structure

```
workspace/
├── content/
│   ├── section-4-test-content/    # Test section with nested structure
│   ├── section-9-test-content/    # Test section with deep nesting
│   ├── README.md                   # Root content README
│   └── SUMMARY.md                  # GitBook summary file
└── publish.yml                     # Publishing configuration
```

## Content

All content is anonymized Lorem Ipsum placeholder text:
- **README.md files**: Simple directory-based templates
- **Regular .md files**: Structured Lorem Ipsum with sections
- **SUMMARY.md**: Generic test item structure

## Usage

These tests run in Docker containers to match the production environment:

```bash
# Run README deletion test
pytest .github/gitbook_worker/tests/test_orchestrator_readme_docker.py -v

# Run full pipeline test
pytest .github/gitbook_worker/tests/test_full_orchestrator_pipeline.py -v
```

## Important

⚠️ **Do not use real project content in this test workspace!**
All content should remain anonymized to protect sensitive information.
