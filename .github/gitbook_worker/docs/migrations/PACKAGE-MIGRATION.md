---
version: 1.0.0
created: 2025-11-09
modified: 2025-11-10
status: in-progress
type: migration-guide
---

# Package Structure Migration Guide

**Status:** In Progress  
**Version:** 1.0.0  
**Date:** November 9, 2025

## Overview

This document describes the migration from the legacy `tools.*` import structure to the new canonical `gitbook_worker.tools.*` package hierarchy.

## Goals

1. **Single Source of Truth**: All implementation lives in `.github/gitbook_worker/tools/`
2. **Proper Package Structure**: Use standard Python package conventions
3. **Simplified PYTHONPATH**: Only `.github/` needs to be in PYTHONPATH
4. **Backward Compatibility**: Legacy imports continue to work during transition
5. **Future-Ready**: Prepare for extraction to standalone PyPI package

## Package Structure

### New Structure (Target)

```
.github/
├── pyproject.toml              # Package definition
└── gitbook_worker/
    ├── __init__.py             # Package root with metadata
    └── tools/
        ├── __init__.py
        ├── workflow_orchestrator/
        ├── publishing/
        ├── converter/
        ├── quality/
        ├── emoji/
        ├── utils/
        └── docker/
```

### Legacy Structure (Deprecated)

```
tools/                          # Repository root (DEPRECATED)
├── __init__.py                 # Backward-compatibility shim
└── __pycache__/
```

## Migration Steps

### Phase 1: Structural Refactoring (Current)

#### 1. Import Path Changes

**Before:**
```python
from tools.workflow_orchestrator import run
from tools.publishing.publisher import publish_entry
from tools.utils import git
```

**After:**
```python
from gitbook_worker.tools.workflow_orchestrator import run
from gitbook_worker.tools.publishing.publisher import publish_entry
from gitbook_worker.tools.utils import git
```

#### 2. Module Invocation Changes

**Before:**
```bash
python -m tools.workflow_orchestrator --profile local
python -m tools.quality.link_audit --root .
```

**After:**
```bash
python -m gitbook_worker.tools.workflow_orchestrator --profile local
python -m gitbook_worker.tools.quality.link_audit --root .
```

#### 3. PYTHONPATH Simplification

**Before:**
```powershell
# PowerShell
$env:PYTHONPATH = "$PWD;$PWD\.github;$PWD\.github\gitbook_worker"

# Bash
export PYTHONPATH="${PWD}:${PWD}/.github:${PWD}/.github/gitbook_worker"
```

**After:**
```powershell
# PowerShell
$env:PYTHONPATH = "$PWD\.github"

# Bash
export PYTHONPATH="${PWD}/.github"
```

### Phase 2: Long-term Migration (Future)

Extract `gitbook_worker` to standalone repository/package:

1. Create separate `erda-workflow-tools` repository
2. Publish to PyPI or GitHub Packages
3. Install as dependency in ERDA-book:
   ```toml
   [project]
   dependencies = ["erda-workflow-tools>=1.0.0"]
   ```
4. Remove `.github/gitbook_worker/` from ERDA-book
5. Remove backward-compatibility shim

## Files Requiring Updates

### Python Source Files (63 locations)

**Tools:**
- `.github/gitbook_worker/tools/**/*.py` - Internal imports within tools
- `.github/demo_smart_merge.py` - Utility script

**Tests:**
- `.github/gitbook_worker/tests/**/*.py` - Test imports

### Configuration Files

**VS Code:**
- `.vscode/launch.json` - Debug configurations (4 locations)
  - Update `module` fields
  - Update `PYTHONPATH` environment

**Docker:**
- `.github/gitbook_worker/tools/docker/Dockerfile` - PYTHONPATH setup
- `.github/gitbook_worker/tests/test_docker_container.py` - Test expectations

**Scripts:**
- `.github/gitbook_worker/scripts/build-pdf.sh` - PYTHONPATH export
- `.github/gitbook_worker/scripts/build-pdf.ps1` - PYTHONPATH setup
- `.github/gitbook_worker/tools/run-emoji-harness.sh` - PYTHONPATH export

**Workflows:**
- All GitHub Actions workflows using orchestrator

### Documentation

- `.github/gitbook_worker/tools/README.md` - Update import examples
- `.github/gitbook_worker/tools/*/README.md` - Module-specific docs
- `.github/gitbook_worker/defaults/README.md` - Usage examples
- `.github/gitbook_worker/docs/*.md` - Implementation notes

## Backward Compatibility

The legacy `tools/__init__.py` shim provides temporary compatibility:

1. **Deprecation Warning**: Issued on first import
2. **Automatic Re-routing**: `tools.X` → `gitbook_worker.tools.X`
3. **PYTHONPATH Handling**: Adds `.github/` if missing

**Timeline:**
- **Now - 3 months**: Deprecation warnings active, shim functional
- **3-6 months**: All internal code migrated to new imports
- **6+ months**: Shim removed, `tools/` directory deleted

## Testing Strategy

### Validation Checklist

- [ ] Unit tests pass: `pytest .github/gitbook_worker/tests -v -m "not slow"`
- [ ] Integration tests pass: `pytest .github/gitbook_worker/tests -v -m "slow"`
- [ ] Orchestrator runs locally: `python -m gitbook_worker.tools.workflow_orchestrator --profile local --dry-run`
- [ ] VS Code debugger launches successfully
- [ ] Docker builds complete: `docker build -f .github/gitbook_worker/tools/docker/Dockerfile .`
- [ ] GitHub Actions workflows succeed

### Regression Tests

Add tests to ensure both import styles work during transition:

```python
def test_legacy_import_compatibility():
    """Verify tools.* imports still work (deprecated)."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        from tools.workflow_orchestrator import run
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)

def test_new_import_path():
    """Verify gitbook_worker.tools.* imports work."""
    from gitbook_worker.tools.workflow_orchestrator import run
    assert callable(run)
```

## Benefits

### Immediate (Phase 1)

- ✅ Clear package ownership (single source of truth)
- ✅ Standard Python import conventions
- ✅ Simplified PYTHONPATH configuration
- ✅ Better IDE/linter support
- ✅ Clearer dependency graph

### Long-term (Phase 2)

- ✅ Reusable across multiple GitBook projects
- ✅ Independent versioning
- ✅ CI/CD in dedicated repo
- ✅ Publishable to PyPI
- ✅ Installable via `pip install erda-workflow-tools`

## Migration Checklist

### Developer Setup

- [ ] Update local `.env` with `PYTHONPATH=.github`
- [ ] Update VS Code settings/launch configs
- [ ] Reinstall package: `cd .github && pip install -e .`
- [ ] Verify imports: `python -c "from gitbook_worker.tools import workflow_orchestrator"`

### Code Updates

- [ ] Replace all `from tools.` with `from gitbook_worker.tools.`
- [ ] Update all `-m tools.` to `-m gitbook_worker.tools.`
- [ ] Update PYTHONPATH in all scripts/configs
- [ ] Update documentation with new examples

### CI/CD

- [ ] Update GitHub Actions workflows
- [ ] Update Docker PYTHONPATH configuration
- [ ] Verify all workflow steps execute successfully

## Support

For questions or issues during migration:

1. Check this document first
2. Review `tools/__init__.py` docstring for quick reference
3. See `.github/gitbook_worker/tools/README.md` for module docs
4. Open issue in repository with `migration` label

---

**License:** CC BY 4.0 (documentation), MIT (code changes)  
**Maintained by:** ERDA Book Project  
**Last Updated:** November 9, 2025
