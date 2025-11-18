---
version: 1.0.0
created: 2025-11-13
modified: 2025-11-13
status: stable
type: implementation
author: GitHub Copilot
tags: [content-discovery, smart-merge, gitbook, publishing]
---

# Content Discovery Implementation

## Overview

The `content_discovery` module provides a robust, unified system for discovering markdown content across different project layouts. It implements the **Smart Merge** philosophy to handle GitBook projects, plain folders, multi-project setups, and single files with graceful fallbacks.

**Module Location:** `tools/utils/content_discovery.py`  
**Test Coverage:** `tests/test_content_discovery.py` (19 tests, all passing)  
**Status:** Production-ready, stable

## Motivation

### Problem Statement

Prior to this implementation, content discovery logic was scattered across multiple modules:

1. **`publisher.py`** - Ad-hoc path resolution and file collection
2. **`gitbook_style.py`** - GitBook-specific structure handling
3. **`set_publish_flag.py`** - Path matching without book.json awareness

This resulted in:
- ❌ Inconsistent behavior across different project types
- ❌ Duplicate path resolution logic
- ❌ No central handling of `book.json` root configuration
- ❌ Fragile fallback mechanisms
- ❌ Difficult to test edge cases

### Goals

1. ✅ **Unified API** for all content discovery scenarios
2. ✅ **Smart Merge** prioritization (explicit → convention → fallback)
3. ✅ **Graceful degradation** when GitBook artifacts are missing
4. ✅ **Comprehensive testing** covering all modes and edge cases
5. ✅ **Clear separation** of concerns from publishing logic

## Architecture

### Smart Merge Hierarchy

The implementation follows a three-tier priority system:

```
┌─────────────────────────────────────────────────────┐
│ 1. EXPLICIT CONFIGURATION (Highest Priority)       │
│    - use_book_json flag                            │
│    - use_summary flag                              │
│    - User-provided source_type                     │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ 2. CONVENTION OVER CONFIGURATION (Middle Priority) │
│    - Search for book.json in parent directories    │
│    - Look for SUMMARY.md in standard locations     │
│    - Auto-detect file vs folder from path          │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ 3. GRACEFUL FALLBACK (Lowest Priority)            │
│    - Use path directly as content root             │
│    - Recursive markdown collection                 │
│    - Alphabetical file ordering                    │
└─────────────────────────────────────────────────────┘
```

### Core Components

#### 1. `ContentDiscoveryResult` (Dataclass)

Immutable result object containing all discovered paths:

```python
@dataclass(frozen=True)
class ContentDiscoveryResult:
    base_dir: Path              # Where book.json or manifest resides
    content_root: Path          # Root directory of markdown content
    summary_path: Optional[Path] # Path to SUMMARY.md (if exists)
    markdown_files: List[Path]  # List of discovered .md files
    book_json_path: Optional[Path] # Path to book.json (if exists)
    source_type: str            # "file" or "folder"
    use_summary: bool           # Whether SUMMARY.md is being used
```

#### 2. `discover_content()` (Main Function)

Single entry point for all content discovery:

```python
def discover_content(
    *,
    path: str | Path,              # Entry path from publish.yml
    source_type: Optional[str] = None,  # "file", "folder", or auto
    use_book_json: bool = False,   # Respect book.json structure
    use_summary: bool = False,     # Use SUMMARY.md ordering
    base_dir: Optional[Path] = None  # Override base directory
) -> ContentDiscoveryResult
```

#### 3. Helper Functions

- **`_find_book_json()`** - Walk up directory tree to find book.json
- **`_read_book_json()`** - Parse JSON with error handling
- **`_find_summary()`** - Locate SUMMARY.md in content root
- **`_collect_markdown_recursive()`** - Glob all .md files
- **`_extract_paths_from_summary()`** - Parse SUMMARY.md links
- **`_normalize_source_type()`** - Auto-detect file vs folder

## Supported Scenarios

### Scenario 1: GitBook with book.json + SUMMARY.md

**Project Structure:**
```
my-book/
├── book.json           # {"root": "content/", "structure": {"summary": "SUMMARY.md"}}
└── content/
    ├── README.md
    ├── SUMMARY.md
    ├── chapter-1.md
    └── chapter-2.md
```

**Usage:**
```python
result = discover_content(
    path="./my-book",
    source_type="folder",
    use_book_json=True,
    use_summary=True
)
# result.content_root = Path("./my-book/content")
# result.markdown_files = [README.md, chapter-1.md, chapter-2.md] (ordered by SUMMARY)
```

**Key Behaviors:**
- ✅ Reads `book.json` → Resolves `root` field → Sets `content_root`
- ✅ Reads `SUMMARY.md` → Extracts file paths → Preserves order
- ✅ Ignores files not listed in SUMMARY.md
- ✅ Skips broken links (files referenced but not existing)

### Scenario 2: Multi-GitBook (Multiple Projects)

**Project Structure:**
```
multi-project/
├── project-a/
│   ├── book.json       # {"root": "content/"}
│   └── content/
│       └── README.md
└── project-b/
    ├── book.json       # {"root": "docs/"}
    └── docs/
        └── README.md
```

**Usage:**
```python
# Discover project A
result_a = discover_content(
    path="./multi-project/project-a",
    use_book_json=True
)
# result_a.content_root = Path("./multi-project/project-a/content")

# Discover project B
result_b = discover_content(
    path="./multi-project/project-b",
    use_book_json=True
)
# result_b.content_root = Path("./multi-project/project-b/docs")
```

**Key Behaviors:**
- ✅ Each project has independent book.json
- ✅ Different content roots supported (content/ vs docs/)
- ✅ No interference between projects

### Scenario 3: Single File

**Project Structure:**
```
complex-doc_with-special&chars@2024 & !.md
```

**Usage:**
```python
result = discover_content(
    path="./complex-doc_with-special&chars@2024 & !.md",
    source_type="file"
)
# result.source_type = "file"
# result.markdown_files = [Path("./complex-doc_with-special&chars@2024 & !.md")]
```

**Key Behaviors:**
- ✅ Handles special characters in filenames
- ✅ No SUMMARY.md lookup (single file mode)
- ✅ Direct path-to-file mapping

### Scenario 4: Plain Folder (No GitBook)

**Project Structure:**
```
docs/
├── index.md
├── guide.md
└── advanced/
    └── advanced-guide.md
```

**Usage:**
```python
result = discover_content(
    path="./docs",
    source_type="folder",
    use_book_json=False,
    use_summary=False
)
# result.content_root = Path("./docs")
# result.markdown_files = [index.md, guide.md, advanced/advanced-guide.md] (recursive)
```

**Key Behaviors:**
- ✅ No book.json required
- ✅ Recursive file collection
- ✅ Alphabetical ordering (natural fallback)
- ✅ README.md prioritized first if exists

## Error Handling

The implementation is robust against common failure modes:

### Invalid book.json

```python
# book.json contains: "{ invalid json"
result = discover_content(path="./", use_book_json=True)
# Logs: WARNING - Failed to parse book.json: ...
# Behavior: Falls back to using path directly
```

### Missing SUMMARY.md

```python
result = discover_content(path="./", use_summary=True)
# SUMMARY.md not found
# Behavior: Falls back to recursive collection
```

### Empty SUMMARY.md

```python
# SUMMARY.md exists but contains no valid links
result = discover_content(path="./", use_summary=True)
# Logs: WARNING - SUMMARY.md exists but contains no valid files
# Behavior: Falls back to recursive collection
# Result: use_summary=True, but markdown_files from recursive scan
```

### Broken Links in SUMMARY.md

```markdown
# SUMMARY.md
* [Exists](exists.md)
* [Missing](missing.md)
```

```python
result = discover_content(path="./", use_summary=True)
# Logs: DEBUG - SUMMARY.md references non-existent file: missing.md
# Result: markdown_files = [Path("exists.md")] (only existing files)
```

### Non-existent Path

```python
result = discover_content(path="./nonexistent", source_type="folder")
# Behavior: Falls back to current directory or base_dir
# Result: markdown_files = [] (empty list)
```

## API Reference

### `discover_content()`

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str \| Path` | *required* | Entry path from publish.yml (file or folder) |
| `source_type` | `Optional[str]` | `None` | `"file"`, `"folder"`, or `None` for auto-detect |
| `use_book_json` | `bool` | `False` | Whether to respect book.json configuration |
| `use_summary` | `bool` | `False` | Whether to use SUMMARY.md for file ordering |
| `base_dir` | `Optional[Path]` | `None` | Override base directory (defaults to path parent) |

**Returns:** `ContentDiscoveryResult`

**Raises:** No exceptions (graceful error handling with logging)

### `ContentDiscoveryResult`

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `base_dir` | `Path` | Base directory (where book.json or manifest resides) |
| `content_root` | `Path` | Root directory containing markdown content |
| `summary_path` | `Optional[Path]` | Path to SUMMARY.md (if exists) |
| `markdown_files` | `List[Path]` | List of discovered markdown files |
| `book_json_path` | `Optional[Path]` | Path to book.json (if exists) |
| `source_type` | `str` | `"file"` or `"folder"` |
| `use_summary` | `bool` | Whether SUMMARY.md is being used for ordering |

## Test Coverage

**Location:** `tests/test_content_discovery.py`  
**Status:** 19 tests, all passing (100% success rate)

### Test Classes

1. **`TestSingleGitBook`** (4 tests)
   - GitBook with book.json + SUMMARY.md
   - Without SUMMARY (recursive fallback)
   - Without book.json (ignores it)
   - Direct path to content/ directory

2. **`TestMultiGitBook`** (2 tests)
   - Project A with `content/` root
   - Project B with `docs/` root

3. **`TestSingleFile`** (4 tests)
   - Single file discovery
   - Special characters in filename
   - Auto-detect file type
   - Non-existent file handling

4. **`TestFolderWithoutGitBook`** (2 tests)
   - Plain folder without book.json
   - SUMMARY.md fallback when requested but missing

5. **`TestEdgeCases`** (7 tests)
   - Empty folder
   - Non-existent folder
   - Invalid book.json (malformed JSON)
   - Empty SUMMARY.md
   - Broken links in SUMMARY.md
   - Nested book.json discovery
   - `.markdown` extension support

### Running Tests

```bash
# Run all content discovery tests
python -m pytest .github/gitbook_worker/tests/test_content_discovery.py -v

# Run specific test class
python -m pytest .github/gitbook_worker/tests/test_content_discovery.py::TestSingleGitBook -v

# Run with coverage
python -m pytest .github/gitbook_worker/tests/test_content_discovery.py --cov=tools.utils.content_discovery
```

## Integration Examples

### With `publisher.py`

```python
from tools.utils.content_discovery import discover_content
from tools.publishing.publisher import build_pdf

# Example: Build PDF from discovered content
for entry in publish_entries:
    result = discover_content(
        path=entry["path"],
        source_type=entry.get("source_type"),
        use_book_json=entry.get("use_book_json", False),
        use_summary=entry.get("use_summary", False),
    )
    
    if result.source_type == "file":
        # Single file mode
        build_pdf(
            path=result.markdown_files[0],
            typ="file",
            ...
        )
    else:
        # Folder mode
        build_pdf(
            path=result.content_root,
            typ="folder",
            use_summary=result.use_summary,
            summary_layout=SummaryContext(
                base_dir=result.base_dir,
                root_dir=result.content_root,
                summary_path=result.summary_path
            ),
            ...
        )
```

### With `set_publish_flag.py`

```python
from tools.utils.content_discovery import discover_content

# Example: Match changed files against content root
for entry in manifest["publish"]:
    result = discover_content(
        path=entry["path"],
        use_book_json=entry.get("use_book_json", False)
    )
    
    # Now check if changed files are within content_root
    for changed_file in git_changed_files:
        if Path(changed_file).is_relative_to(result.content_root):
            entry["build"] = True
            break
```

## Performance Considerations

### Lazy Evaluation

- File system operations are lazy (only performed when needed)
- book.json parsing skipped if `use_book_json=False`
- SUMMARY.md parsing skipped if `use_summary=False`

### Caching Strategy

- Path resolution results are not cached (stateless function)
- Repeated calls with same arguments will re-scan filesystem
- Caller should cache `ContentDiscoveryResult` if needed

### Optimization Tips

```python
# ✅ Good: Reuse result
result = discover_content(path="./", use_book_json=True)
for file in result.markdown_files:
    process(file)

# ❌ Bad: Multiple calls
for _ in range(10):
    result = discover_content(path="./", use_book_json=True)  # Re-scans each time!
```

## Logging

The module uses Python's standard logging with namespace `tools.utils.content_discovery`.

### Log Levels

| Level | Usage |
|-------|-------|
| `DEBUG` | Path resolution steps, file counts, discovery details |
| `INFO` | Summary of discovery results (content root, file count) |
| `WARNING` | Invalid book.json, broken SUMMARY links, fallback triggers |
| `ERROR` | (Not used - graceful degradation instead) |

### Enable Debug Logging

```python
import logging

logging.getLogger("tools.utils.content_discovery").setLevel(logging.DEBUG)

result = discover_content(path="./", use_book_json=True)
# Output:
# DEBUG: Found book.json at: /path/to/book.json
# DEBUG: Content root from book.json: /path/to/content
# INFO:  Using SUMMARY.md for content ordering: /path/to/content/SUMMARY.md
# DEBUG: Extracted 3 files from SUMMARY.md
# INFO:  Content discovery completed: markdown_files: 3 found
```

## Known Limitations

1. **SUMMARY.md Format**: Only GitBook-style `[text](path.md)` links supported
2. **URL Handling**: HTTP/HTTPS/FTP links in SUMMARY.md are ignored
3. **Extensions**: Only `.md` and `.markdown` files recognized
4. **Anchor Links**: Fragment identifiers (`#section`) stripped from paths
5. **Symlinks**: Not explicitly handled (follows Python's default behavior)

## Future Enhancements

### Planned (v1.1.0)

- [ ] Support for CommonMark-style table of contents
- [ ] Configurable file extension filter (beyond .md/.markdown)
- [ ] Symlink resolution policy (follow vs ignore)

### Under Consideration (v2.0.0)

- [ ] Plugin system for custom discovery strategies
- [ ] Parallel file scanning for large repositories
- [ ] Cache layer for book.json and SUMMARY.md parsing
- [ ] Watch mode for live content updates

## Migration Guide

### From Legacy Code

**Before (ad-hoc in publisher.py):**
```python
folder_path = Path(entry["path"])
if entry.get("use_book_json"):
    book_json = folder_path / "book.json"
    if book_json.exists():
        data = json.loads(book_json.read_text())
        folder_path = folder_path / data.get("root", ".")
md_files = list(folder_path.glob("**/*.md"))
```

**After (using content_discovery):**
```python
result = discover_content(
    path=entry["path"],
    use_book_json=entry.get("use_book_json", False)
)
folder_path = result.content_root
md_files = result.markdown_files
```

**Benefits:**
- ✅ Handles edge cases (invalid JSON, missing files)
- ✅ Consistent error handling
- ✅ Comprehensive logging
- ✅ Tested extensively

## Related Documentation

- **Module README**: `tools/utils/README.md` - Usage examples and module overview
- **GitBook Style**: `tools/publishing/gitbook_style.py` - SUMMARY generation
- **Publisher**: `tools/publishing/publisher.py` - PDF build system
- **Smart Manifest**: `tools/utils/smart_manifest.py` - Manifest resolution

## Change History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-13 | Initial implementation with Smart Merge philosophy |

## Authors

- **GitHub Copilot** - Initial implementation and documentation
- **Project Maintainers** - Code review and integration

## License

See repository root `LICENSE` file.
