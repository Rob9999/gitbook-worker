# Shared Utilities

Reusable helpers for subprocess execution, Docker orchestration and virtual
environment management.

## Modules

### Core Utilities

| Module | Description |
| --- | --- |
| `run.py` | Wrapper around `subprocess.run` that standardises logging, environment merging and error handling. |
| `docker_runner.py` | Builds (if necessary) and runs Docker containers with a bind-mounted workspace. Attempts to start Docker Desktop on Windows or the daemon on Linux. |
| `docker.py` | Helper functions used by the runner to build images and manage bind mounts. |
| `python_workspace_runner.py` | Creates a `.venv` inside a target workspace, installs dependencies via `pip`, `requirements.txt` files or `uv`, and executes a command/module inside that environment. |
| `git.py` | Utilities for resolving repository metadata (e.g. the current commit) when running inside CI. |
| `semver.py` | Semantic version parsing and validation utilities. |

### Smart Modules (Smart Merge Ecosystem)

| Module | Description | Documentation |
| --- | --- | --- |
| `content_discovery.py` | Robust content discovery for GitBook projects, plain folders, and single files. Implements Smart Merge philosophy (explicit config → convention → fallback). | [Implementation Doc](../../docs/implementations/content-discovery-implementation.md) |
| `smart_manifest.py` | Configurable manifest resolution with support for multiple search strategies (CLI, cwd, repo root, custom directories). | - |
| `smart_book.py` | **NEW** Book.json discovery and content root resolution. Searches parent directories, validates structure, provides content_root for path matching. | - |
| `smart_publish_target.py` | **NEW** Publish target resolution with book.json binding. Loads targets from publish.yml, discovers book.json for each, provides unified PublishTarget dataclass. | - |
| `smart_publisher.py` | **NEW** High-level publishing coordination. Wraps legacy publisher.py, provides SmartPublisher class for workflow management. | - |
| `smart_manage_publish_flags.py` | **NEW** Unified publish flag management with book.json awareness. Replaces set_publish_flag.py + reset_publish_flag.py. Fixes root path matching bug. | [Implementation Doc](../../docs/implementations/smart-manage-publish-flags-implementation.md) |
| `smart_git.py` | **NEW** Git utilities with fallback support. Changed file detection with shallow clone handling, commit info, repository status. | - |

## Usage examples

Run a command with logging and strict error handling:

```python
from tools.utils import run

run(["pytest", "-q"], cwd=".github", check=True)
```

Execute a script inside a temporary virtual environment:

```bash
python -m tools.utils.python_workspace_runner \
  --workspace .github \
  --module tools.workflow_orchestrator \
  -- --profile default --dry-run
```

Discover content for publishing (GitBook, plain folder, or single file):

```python
from tools.utils.content_discovery import discover_content

# GitBook with book.json + SUMMARY.md
result = discover_content(
    path="./",
    source_type="folder",
    use_book_json=True,
    use_summary=True
)
print(f"Content root: {result.content_root}")  # ./content (from book.json)
print(f"Files: {len(result.markdown_files)}")  # Ordered by SUMMARY.md

# Plain folder (fallback mode)
result = discover_content(
    path="./docs",
    source_type="folder",
    use_book_json=False,
    use_summary=False
)
print(f"Files: {len(result.markdown_files)}")  # All .md files recursively

# Single file
result = discover_content(path="./README.md", source_type="file")
print(f"File: {result.markdown_files[0]}")  # Path('./README.md')
```

## Content Discovery

The `content_discovery` module implements a **Smart Merge** strategy for
locating markdown sources across different project layouts:

1. **Explicit Configuration First** – Honours `use_book_json` and `use_summary`
   flags from `publish.yml` to respect `book.json` structure and
   `SUMMARY.md` ordering.
2. **Convention Over Configuration** – Automatically searches for `book.json` in
   parent directories and `SUMMARY.md` in standard locations when flags are set.
3. **Graceful Fallback** – Collects all `.md` files recursively when GitBook
   artefacts are missing, ensuring builds succeed even in plain folder layouts.

**Supported modes:**

* **GitBook projects** with `book.json` (defines content root) and `SUMMARY.md`
  (defines file order)
* **Multi-GitBook** setups where each subdirectory has its own `book.json`
* **Plain folders** without GitBook structure (recursive Markdown collection)
* **Single files** (direct path to a `.md` or `.markdown` file)

**Key features:**

* Handles invalid/missing `book.json` gracefully (logs warning, falls back)
* Skips broken links in `SUMMARY.md` (only includes existing files)
* Supports both `.md` and `.markdown` extensions
* Returns structured result with content root, summary path, and file list

See `test_content_discovery.py` for comprehensive usage examples covering all
four modes and edge cases (empty summaries, invalid JSON, nested structures).

## Smart Modules Architecture

The **Smart Merge Ecosystem** provides unified, robust handling of GitBook projects and publishing workflows:

```
Workflow Layer:
  workflow_orchestrator.py
        ↓
Publishing Layer:
  smart_publisher.py (coordination)
        ↓
  smart_manage_publish_flags.py (flag management)
        ↓
Target Resolution Layer:
  smart_publish_target.py (target + book.json binding)
        ↓
Discovery Layer:
  smart_book.py (book.json discovery)
  content_discovery.py (content discovery)
  smart_manifest.py (manifest resolution)
        ↓
Infrastructure Layer:
  smart_git.py (git operations with fallbacks)
```

**Key Features:**
- **Book.json Awareness**: All modules respect book.json content_root for accurate path matching
- **Smart Merge**: Explicit configuration → Convention search → Graceful fallback
- **Shallow Clone Support**: Git operations work with fetch-depth=1 (CI optimization)
- **Root Path Fix**: `path: "."` correctly matches all files (fixed critical CI bug)
- **Unified API**: Consistent interfaces across all smart modules

**Test Coverage:**

| Module | Tests | Status |
| --- | ---:| --- |
| `content_discovery.py` | 19 | ✅ Complete |
| `smart_book.py` | 22 | ✅ Complete |
| `smart_git.py` | 22 | ✅ Complete |
| `smart_manage_publish_flags.py` | 30 | ✅ Complete |
| `smart_manifest.py` | 26 | ✅ Complete |
| `smart_merge.py` | 13 | ✅ Complete |
| `smart_publish_target.py` | 22 | ✅ Complete |
| `smart_publisher.py` | 26 | ✅ Complete |
| **TOTAL** | **180** | **100%** |

**Migration Status:**
- ✅ All 8 smart modules complete with comprehensive test coverage
- ✅ Root path matching bug fixed (`"." == "file.md"` now TRUE)
- ✅ Book.json awareness integrated across ecosystem
- ✅ Shallow clone support (fetch-depth=1) with 3-tier fallback
- ⚠️ Legacy scripts in `tools/publishing/` now deprecated wrappers

## Development notes

* Prefer pathlib paths when extending these utilities.
* Update callers in `workflow_orchestrator` if function signatures change.
* New smart modules follow Smart Merge philosophy (see implementation docs).
* All git operations should use `smart_git.py` for consistent fallback handling.
* Document new subcommands here so other modules can adopt them quickly.
* When adding content discovery logic, extend `content_discovery.py` rather than
  duplicating path resolution in other modules.
