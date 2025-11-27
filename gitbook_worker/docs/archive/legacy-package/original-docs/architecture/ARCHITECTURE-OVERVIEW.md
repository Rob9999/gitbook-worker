---
version: 1.0.0
created: 2025-11-09
modified: 2025-11-10
status: stable
type: architecture-documentation
---

# Package Architecture Overview

## Current State (Before Migration)

```
┌─────────────────────────────────────────────────────────────┐
│ ERDA-Book Repository                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  tools/                  ← Legacy shim (PYTHONPATH hack)   │
│  └── __init__.py                                           │
│                                                             │
│  .github/                                                   │
│  └── gitbook_worker/                                       │
│      └── tools/          ← Actual implementation           │
│          ├── workflow_orchestrator/                         │
│          ├── publishing/                                    │
│          ├── converter/                                     │
│          ├── quality/                                       │
│          ├── emoji/                                         │
│          ├── utils/                                         │
│          └── docker/                                        │
│                                                             │
│  PYTHONPATH = ".:. github:.github/gitbook_worker" ❌        │
│              (3 paths needed!)                              │
└─────────────────────────────────────────────────────────────┘

Imports:  from tools.publishing import publisher  ⚠️  Confusing!
```

## Target State - Phase 1 (Internal Refactoring)

```
┌─────────────────────────────────────────────────────────────┐
│ ERDA-Book Repository                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  tools/                  ← Backward-compat shim             │
│  └── __init__.py            (with DeprecationWarning)       │
│                                                             │
│  .github/                                                   │
│  ├── pyproject.toml      ← Package definition              │
│  └── gitbook_worker/                                       │
│      ├── __init__.py     ← Package root with metadata      │
│      └── tools/                                             │
│          ├── __init__.py                                    │
│          ├── workflow_orchestrator/                         │
│          ├── publishing/                                    │
│          ├── converter/                                     │
│          ├── quality/                                       │
│          ├── emoji/                                         │
│          ├── utils/                                         │
│          └── docker/                                        │
│                                                             │
│  PYTHONPATH = ".github" ✅  (Single source of truth!)       │
└─────────────────────────────────────────────────────────────┘

Imports:  from gitbook_worker.tools.publishing import publisher  ✅
Legacy:   from tools.publishing import publisher  ⚠️  (still works)
```

## Target State - Phase 2 (Standalone Package)

```
┌───────────────────────────────┐   ┌─────────────────────────┐
│ erda-workflow-tools (PyPI)    │   │ ERDA-Book Repository    │
├───────────────────────────────┤   ├─────────────────────────┤
│                               │   │                         │
│  src/                         │   │  pyproject.toml         │
│  └── erda_workflow_tools/     │   │  dependencies:          │
│      ├── __init__.py          │   │  - erda-workflow-tools  │
│      ├── workflow_orchestrator│   │    >=1.0.0              │
│      ├── publishing/          │   │                         │
│      ├── converter/           │   │  content/               │
│      ├── quality/             │   │  ├── chapters/          │
│      ├── emoji/               │   │  └── assets/            │
│      ├── utils/               │   │                         │
│      └── docker/              │   │  publish.yml            │
│                               │   │                         │
│  Published to PyPI ✅          │   │  No tools/ ✅            │
│  Version: 1.0.0               │   │  No .github/gitbook_    │
│  License: MIT                 │   │         worker/tools/ ✅ │
└───────────────────────────────┘   └─────────────────────────┘
            │                                     │
            └─────────── pip install ─────────────┘

Installation:  pip install erda-workflow-tools
Imports:       from erda_workflow_tools.publishing import publisher  ✅
CLI:           erda-orchestrator --profile default
```

## Import Migration Path

### Before (Legacy)

```python
# ❌ Old style (repository root)
from tools.workflow_orchestrator import run
from tools.publishing.publisher import publish_entry
from tools.quality.link_audit import audit_directory

# Requires: PYTHONPATH=.:. github:.github/gitbook_worker
```

### Phase 1 (Internal)

```python
# ✅ New style (package-based)
from gitbook_worker.tools.workflow_orchestrator import run
from gitbook_worker.tools.publishing.publisher import publish_entry
from gitbook_worker.tools.quality.link_audit import audit_directory

# Requires: PYTHONPATH=.github

# ⚠️ Legacy still works with deprecation warning
from tools.workflow_orchestrator import run  # DeprecationWarning
```

### Phase 2 (Standalone)

```python
# ✅ Final style (pip package)
from erda_workflow_tools.workflow_orchestrator import run
from erda_workflow_tools.publishing.publisher import publish_entry
from erda_workflow_tools.quality.link_audit import audit_directory

# Requires: pip install erda-workflow-tools
# No PYTHONPATH manipulation needed!
```

## CLI Evolution

### Current

```powershell
# Must be in repo root with complex PYTHONPATH
$env:PYTHONPATH = "$PWD;$PWD\.github;$PWD\.github\gitbook_worker"
python -m tools.workflow_orchestrator --profile local
```

### Phase 1

```powershell
# Simpler PYTHONPATH
$env:PYTHONPATH = "$PWD\.github"
python -m gitbook_worker.tools.workflow_orchestrator --profile local

# Legacy still works
python -m tools.workflow_orchestrator --profile local  # ⚠️  Deprecated
```

### Phase 2

```powershell
# No PYTHONPATH needed!
erda-orchestrator --profile local

# Or module form
python -m erda_workflow_tools.workflow_orchestrator --profile local
```

## Dependency Graph

### Phase 1 (Embedded)

```
ERDA-Book
└── .github/gitbook_worker (embedded)
    └── tools/ (not a proper package)
        ├── depends on: pyyaml, pandas, matplotlib, ...
        └── used by: ERDA-book only
```

### Phase 2 (Standalone)

```
erda-workflow-tools (PyPI package)
├── version: 1.x.x
├── depends on: pyyaml, pandas, matplotlib, ...
└── used by:
    ├── ERDA-book
    ├── Other GitBook projects
    └── Custom automation scripts

ERDA-Book
└── depends on: erda-workflow-tools>=1.0.0
```

## Benefits Comparison

| Aspect | Current | Phase 1 | Phase 2 |
|--------|---------|---------|---------|
| **Import Clarity** | ❌ Confusing | ✅ Clear | ✅ Intuitive |
| **PYTHONPATH** | ❌ 3 paths | ⚠️ 1 path | ✅ Not needed |
| **Package Structure** | ❌ Ad-hoc | ✅ Proper | ✅ Professional |
| **Reusability** | ❌ Copy-paste | ⚠️ Via git | ✅ Via pip |
| **Versioning** | ❌ Git commits | ⚠️ Git tags | ✅ SemVer |
| **Distribution** | ❌ None | ❌ None | ✅ PyPI |
| **Testing** | ⚠️ Embedded | ✅ Isolated | ✅ Independent |
| **CI/CD** | ⚠️ Mixed | ⚠️ Mixed | ✅ Dedicated |
| **Backward Compat** | N/A | ✅ Yes | ⚠️ Via import |

## Risk Matrix

| Phase | Breaking Changes | Migration Effort | Maintenance | Community |
|-------|------------------|------------------|-------------|-----------|
| Current | N/A | N/A | ❌ High | ❌ No |
| Phase 1 | ✅ None (shimmed) | ⚠️ Medium | ⚠️ Medium | ❌ No |
| Phase 2 | ⚠️ Import paths | ⚠️ High (once) | ✅ Low | ✅ Yes |

## Timeline Visualization

```
Current State
     │
     ├─ Phase 1: Internal Refactoring (2-3 days)
     │  ├─ gitbook_worker package setup ✅
     │  ├─ Backward-compat shim ✅
     │  ├─ Update imports (pending)
     │  ├─ Simplify PYTHONPATH (pending)
     │  └─ Validation testing (pending)
     │
     └─ Phase 2: Standalone Package (6-8 weeks)
        ├─ Repository setup (1 week)
        ├─ Code migration (2 weeks)
        ├─ Testing (1 week)
        ├─ Documentation (1 week)
        ├─ ERDA integration (1 week)
        └─ Release v1.0.0 (1 week)
```

## Success Criteria

### Phase 1 ✅ (Foundation Complete)

- ✅ Package structure defined
- ✅ Backward compatibility ensured
- ✅ Migration guide documented
- ✅ PoC validated
- ⏳ Imports updated (pending)
- ⏳ PYTHONPATH simplified (pending)
- ⏳ Tests passing (pending)

### Phase 2 ⏳ (Planned)

- ⏳ Standalone repository created
- ⏳ Package published to PyPI
- ⏳ ERDA-book using as dependency
- ⏳ Documentation on ReadTheDocs
- ⏳ CI/CD pipeline operational
- ⏳ Community adoption started

---

**Visual Guide Version:** 1.0  
**Last Updated:** November 9, 2025  
**License:** CC BY 4.0
