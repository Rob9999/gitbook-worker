# Installation and Testing Guide

## Prerequisites

```powershell
# Install build tools
pip install build pytest
```

## Installation

### Option 1: Editable Install (Development)

```powershell
cd .github/poc-standalone-package
pip install -e .
```

This installs the package in "development mode" - changes to source files are immediately reflected.

### Option 2: Build and Install

```powershell
cd .github/poc-standalone-package

# Build the package
python -m build

# Install from wheel
pip install dist/erda_workflow_tools-0.1.0-py3-none-any.whl
```

## Testing

### 1. Test Package Import

```powershell
python -c "import erda_workflow_tools; print(erda_workflow_tools.__version__)"
# Expected: 0.1.0
```

### 2. Test Module Functions

```powershell
python -c "from erda_workflow_tools import hello; hello.greet('PoC')"
# Expected: Hello, PoC!
```

### 3. Test CLI Entry Point

```powershell
python -m erda_workflow_tools
# Expected: ERDA Workflow Tools v0.1.0 + usage info
```

### 4. Test Console Script

```powershell
erda-workflow-tools
# Expected: Same as above (after installation)
```

### 5. Run Unit Tests

```powershell
cd .github/poc-standalone-package
pytest tests/ -v
```

Expected output:
```
tests/test_hello.py::test_greet PASSED
tests/test_hello.py::test_greet_with_empty_string PASSED
tests/test_hello.py::test_get_version PASSED
tests/test_hello.py::test_package_imports PASSED
tests/test_hello.py::test_cli_main PASSED

==================== 5 passed in 0.XX s ====================
```

## Validation Checklist

- [ ] Package builds without errors (`python -m build`)
- [ ] Editable install works (`pip install -e .`)
- [ ] Import succeeds (`import erda_workflow_tools`)
- [ ] Version accessible (`erda_workflow_tools.__version__`)
- [ ] Functions work (`hello.greet()`)
- [ ] CLI runs (`python -m erda_workflow_tools`)
- [ ] Console script works (`erda-workflow-tools`)
- [ ] All tests pass (`pytest tests/`)

## Uninstall

```powershell
pip uninstall erda-workflow-tools
```

## Next Steps After Validation

If all tests pass:

1. **Full Migration**: Copy entire `gitbook_worker/tools/` codebase
2. **Import Updates**: Replace `tools.*` with `erda_workflow_tools.*`
3. **Test Migration**: Port all tests from `.github/gitbook_worker/tests/`
4. **CLI Wiring**: Connect real orchestrator to `__main__.py`
5. **Dependencies**: Add all required packages to `pyproject.toml`
6. **Documentation**: Write comprehensive usage docs
7. **Repository Setup**: Create dedicated repo on GitHub
8. **CI/CD**: Set up automated testing and PyPI publishing

## Troubleshooting

### Import errors after installation

```powershell
# Check installation
pip show erda-workflow-tools

# Verify package location
python -c "import erda_workflow_tools; print(erda_workflow_tools.__file__)"
```

### Build errors

```powershell
# Clean build artifacts
Remove-Item -Recurse -Force dist, build, *.egg-info

# Rebuild
python -m build
```

### Test failures

```powershell
# Reinstall in editable mode
pip uninstall erda-workflow-tools
pip install -e .

# Run tests with verbose output
pytest tests/ -vv
```

---

**Last Updated:** November 9, 2025
