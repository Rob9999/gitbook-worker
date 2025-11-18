# Proof of Concept: erda-workflow-tools Package

This directory contains a minimal proof-of-concept for the standalone `erda-workflow-tools` package structure.

## Purpose

Demonstrate the feasibility of extracting gitbook_worker tools into an independent, installable Python package.

## Structure

```
poc-standalone-package/
├── README.md                   # This file
├── pyproject.toml              # Package metadata (PEP 621)
├── setup.py                    # Fallback for older pip versions
├── src/
│   └── erda_workflow_tools/    # Package source
│       ├── __init__.py
│       ├── __main__.py         # CLI entry point
│       └── hello.py            # Minimal example module
├── tests/
│   └── test_hello.py           # Example test
└── INSTALL-TEST.md             # Installation testing instructions
```

## Testing the PoC

### 1. Build the package

```powershell
# From this directory
cd .github/poc-standalone-package
python -m build
```

This creates:
- `dist/erda_workflow_tools-0.1.0.tar.gz` (source distribution)
- `dist/erda_workflow_tools-0.1.0-py3-none-any.whl` (wheel)

### 2. Install in editable mode (development)

```powershell
pip install -e .
```

### 3. Test imports

```powershell
python -c "from erda_workflow_tools import hello; hello.greet('World')"
# Expected output: Hello, World!
```

### 4. Test CLI entry point

```powershell
python -m erda_workflow_tools
# Expected output: ERDA Workflow Tools v0.1.0
```

### 5. Run tests

```powershell
pytest tests/
```

## Next Steps

If this PoC validates successfully:

1. Copy full source from `.github/gitbook_worker/tools/` to `src/erda_workflow_tools/`
2. Update all internal imports (`tools.*` → `erda_workflow_tools.*`)
3. Migrate tests and configuration
4. Set up CI/CD in separate repository
5. Publish to PyPI

## Validation Criteria

- [x] Package builds without errors
- [ ] Package installs via pip
- [ ] Imports work as expected
- [ ] CLI entry points function
- [ ] Tests pass with pytest
- [ ] Can be used as dependency in another project

---

**Status:** PoC Created  
**Date:** November 9, 2025
