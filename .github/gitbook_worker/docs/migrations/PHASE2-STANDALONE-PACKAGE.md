---
version: 1.0.0
created: 2025-11-09
modified: 2025-11-10
status: planning
type: migration-plan
target-date: Q1 2026
---

# Phase 2: Standalone Package Migration Plan

**Goal:** Extract `gitbook_worker.tools` into independent `erda-workflow-tools` package

**Target Date:** Q1 2026  
**Status:** Planning  
**Prerequisites:** Phase 1 complete (internal refactoring)

## Vision

Transform the workflow automation tools into a **reusable, versioned Python package** that can be:
- Installed via `pip install erda-workflow-tools`
- Used by multiple GitBook-based projects
- Maintained independently with its own CI/CD
- Published to PyPI or GitHub Packages

## Repository Structure

### New Repository: `erda-workflow-tools`

```
erda-workflow-tools/
├── .github/
│   └── workflows/
│       ├── test.yml                    # Unit + integration tests
│       ├── publish.yml                 # PyPI publishing
│       └── build-docker.yml            # Container image builds
├── src/
│   └── erda_workflow_tools/            # Note: underscore, not hyphen!
│       ├── __init__.py
│       ├── workflow_orchestrator/
│       ├── publishing/
│       ├── converter/
│       ├── quality/
│       ├── emoji/
│       ├── utils/
│       └── docker/
├── tests/                              # Move from .github/gitbook_worker/tests/
│   ├── conftest.py
│   ├── test_*.py
│   └── data/
├── docs/
│   ├── index.md
│   ├── quickstart.md
│   ├── api/                            # Auto-generated API docs
│   └── migration-from-embedded.md
├── docker/
│   ├── Dockerfile                      # Publishing container
│   └── Dockerfile.dev                  # Development container
├── scripts/
│   ├── build-pdf.sh
│   └── build-pdf.ps1
├── pyproject.toml                      # PEP 621 metadata
├── setup.py                            # Fallback for older pip
├── README.md
├── LICENSE-CODE (MIT)
├── LICENSE-DOCS (CC BY 4.0)
├── CHANGELOG.md
├── CONTRIBUTING.md
└── .gitignore
```

## Package Metadata

### `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "erda-workflow-tools"
version = "1.0.0"
description = "Workflow automation tools for GitBook-based publishing pipelines"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "ERDA Book Project", email = "info@erda-project.org"}
]
keywords = ["gitbook", "pandoc", "publishing", "markdown", "pdf"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Documentation",
    "Topic :: Software Development :: Build Tools",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "pyyaml>=6.0",
    "pandas>=2.0",
    "matplotlib>=3.7",
    "numpy>=1.24",
    "pillow>=10.0",
    "emoji>=2.0",
    "requests>=2.31",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-cov>=4.1",
    "black>=23.0",
    "isort>=5.12",
    "flake8>=6.1",
    "mypy>=1.5",
]
docs = [
    "sphinx>=7.0",
    "sphinx-rtd-theme>=1.3",
    "myst-parser>=2.0",
]

[project.urls]
Homepage = "https://github.com/erda-project/erda-workflow-tools"
Documentation = "https://erda-workflow-tools.readthedocs.io"
Repository = "https://github.com/erda-project/erda-workflow-tools"
Issues = "https://github.com/erda-project/erda-workflow-tools/issues"
Changelog = "https://github.com/erda-project/erda-workflow-tools/blob/main/CHANGELOG.md"

[project.scripts]
erda-orchestrator = "erda_workflow_tools.workflow_orchestrator.__main__:main"
erda-publisher = "erda_workflow_tools.publishing.pipeline:main"
erda-converter = "erda_workflow_tools.converter.convert_assets:main"
erda-link-audit = "erda_workflow_tools.quality.link_audit:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
erda_workflow_tools = [
    "publishing/lua/*.lua",
    "publishing/fonts/*",
    "publishing/texmf/**/*",
    "docker/Dockerfile*",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: integration tests requiring external tools",
]

[tool.black]
line-length = 100
target-version = ['py39', 'py310', 'py311', 'py312']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## Migration Steps

### Step 1: Repository Setup

```bash
# Create new repository
gh repo create erda-project/erda-workflow-tools --public --description "Workflow automation for GitBook publishing"

# Clone and initialize
git clone git@github.com:erda-project/erda-workflow-tools.git
cd erda-workflow-tools
git checkout -b main
```

### Step 2: Code Migration

```bash
# Copy source code
mkdir -p src/erda_workflow_tools
cp -r ../erda-book/.github/gitbook_worker/tools/* src/erda_workflow_tools/

# Copy tests
cp -r ../erda-book/.github/gitbook_worker/tests .

# Copy Docker files
mkdir docker
cp ../erda-book/.github/gitbook_worker/tools/docker/* docker/

# Copy scripts
mkdir scripts
cp ../erda-book/.github/gitbook_worker/scripts/*.{sh,ps1} scripts/
```

### Step 3: Import Path Updates

Replace all internal imports:

```python
# OLD (embedded in erda-book):
from tools.workflow_orchestrator import run
from tools.publishing.publisher import publish_entry

# NEW (standalone package):
from erda_workflow_tools.workflow_orchestrator import run
from erda_workflow_tools.publishing.publisher import publish_entry
```

**Automation script:**
```bash
# Update all Python files
find src tests -name "*.py" -type f -exec sed -i \
    's/from tools\./from erda_workflow_tools./g' {} +
find src tests -name "*.py" -type f -exec sed -i \
    's/import tools\./import erda_workflow_tools./g' {} +
```

### Step 4: CLI Entry Points

Add `__main__.py` wrappers for console scripts:

```python
# src/erda_workflow_tools/workflow_orchestrator/__main__.py
def main():
    """Entry point for erda-orchestrator command."""
    from .orchestrator import run
    import sys
    sys.exit(run())

if __name__ == "__main__":
    main()
```

### Step 5: Documentation

```markdown
# README.md

# ERDA Workflow Tools

Workflow automation tools for GitBook-based publishing pipelines.

## Features

- **Workflow Orchestrator**: Coordinates publishing, conversion, and QA steps
- **PDF Publisher**: Pandoc-based PDF generation with LaTeX support
- **CSV Converter**: Transform data into Markdown tables and charts
- **Quality Assurance**: Link auditing, source extraction, AI-powered reference checks
- **Emoji Support**: Unicode compliance and font coverage reporting
- **Docker Integration**: Reproducible builds in containerized environments

## Installation

```bash
pip install erda-workflow-tools
```

## Quick Start

```bash
# Run orchestrator
erda-orchestrator --profile default --manifest publish.yml

# Publish PDFs
erda-publisher --manifest publish.yml --entry my-book

# Audit links
erda-link-audit --root ./content --format csv
```

## Usage in Projects

```python
from erda_workflow_tools.publishing import publisher
from erda_workflow_tools.quality import link_audit

# Publish a PDF
publisher.publish_entry(
    entry_name="my-book",
    manifest_path="publish.yml"
)

# Check links
issues = link_audit.audit_directory("./content")
```

## Documentation

Full documentation: https://erda-workflow-tools.readthedocs.io

## License

- **Code**: MIT License
- **Documentation**: CC BY 4.0

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)
```

### Step 6: CI/CD Workflows

#### `.github/workflows/test.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      
      - name: Run tests
        run: pytest -v --cov=erda_workflow_tools --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

#### `.github/workflows/publish.yml`

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Build package
        run: |
          python -m pip install build
          python -m build
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

### Step 7: Update ERDA-Book Repository

#### `erda-book/pyproject.toml`

```toml
[project]
name = "erda-book"
dependencies = [
    "erda-workflow-tools>=1.0.0",
]
```

#### Remove embedded tools

```bash
cd erda-book
git rm -r .github/gitbook_worker/tools
git rm -r tools/
git commit -m "Migrate to erda-workflow-tools package"
```

#### Update workflows

```yaml
# .github/workflows/orchestrator.yml
- name: Install dependencies
  run: |
    pip install erda-workflow-tools

- name: Run orchestrator
  run: |
    erda-orchestrator --profile default --manifest publish.yml
```

## Versioning Strategy

Follow [Semantic Versioning 2.0.0](https://semver.org/):

- **1.0.0** - Initial stable release (Phase 2 completion)
- **1.x.x** - Backward-compatible features and bugfixes
- **2.0.0** - Breaking changes (import paths, CLI flags, etc.)

### Version Pinning

```toml
# ERDA-book: Conservative pinning
dependencies = ["erda-workflow-tools>=1.0,<2.0"]

# Other projects: More flexible
dependencies = ["erda-workflow-tools>=1.2"]
```

## Benefits

### For ERDA-Book Project

- ✅ Cleaner repository (content-focused)
- ✅ Faster CI/CD (no need to test tooling in every book build)
- ✅ Versioned tooling dependencies
- ✅ Rollback capability (pin to older version if needed)

### For Workflow Tools

- ✅ Independent release cycle
- ✅ Dedicated issue tracking
- ✅ Community contributions easier
- ✅ Reusable across projects
- ✅ Professional package distribution

### For Other Projects

- ✅ Ready-to-use publishing pipeline
- ✅ No need to copy/maintain tooling code
- ✅ Benefit from bug fixes and features
- ✅ Standardized workflow patterns

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking changes impact ERDA-book | Pin to major version (`>=1.0,<2.0`) |
| Tooling bugs delay book releases | Test in staging, have rollback plan |
| Maintenance burden of two repos | Automate releases, clear contribution docs |
| ERDA-specific features pollute general tool | Feature flags, plugin architecture |

## Success Criteria

- [ ] Package installable via `pip install erda-workflow-tools`
- [ ] All tests pass in standalone repo
- [ ] ERDA-book successfully uses package as dependency
- [ ] Documentation published on ReadTheDocs
- [ ] CI/CD publishes to PyPI on release
- [ ] At least one external project adopts the tools

## Timeline

| Phase | Duration | Milestone |
|-------|----------|-----------|
| Repo setup | 1 week | Repository created, basic structure |
| Code migration | 2 weeks | All code moved, imports updated |
| Testing | 1 week | Full test coverage passing |
| Documentation | 1 week | Docs site published |
| ERDA integration | 1 week | ERDA-book using package |
| First release | 1 week | v1.0.0 on PyPI |

**Total: ~6-8 weeks**

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Publishing](https://pypi.org/help/#publishing)
- [Semantic Versioning](https://semver.org/)
- [GitHub Packages](https://docs.github.com/en/packages)

---

**License:** CC BY 4.0  
**Status:** Planning Document  
**Last Updated:** November 9, 2025
