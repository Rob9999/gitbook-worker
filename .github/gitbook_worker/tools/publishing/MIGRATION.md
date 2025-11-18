# Smart Publish Flag Management Migration

## Overview
This directory contains **deprecated wrapper files** for backward compatibility.

**New location**: `tools/utils/smart_manage_publish_flags.py`

## Migration Status

### Completed
- ✅ Created unified module `smart_manage_publish_flags.py` with book.json awareness
- ✅ Implemented `set_publish_flags()` (git-based flag setting)
- ✅ Implemented `reset_publish_flags()` (target-based flag resetting)
- ✅ Created deprecation wrappers (this directory)
- ✅ Integrated with `smart_publish_target` for content_root resolution

### Files

#### Deprecated Wrappers (Compatibility Only)
- `set_publish_flag.py` → wraps `smart_manage_publish_flags.set_publish_flags()`
- `reset_publish_flag.py` → wraps `smart_manage_publish_flags.reset_publish_flags()`

#### Legacy Backups
- `set_publish_flag_LEGACY.py` - original implementation (pre-migration)
- `reset_publish_flag_LEGACY.py` - original implementation (pre-migration)

## New API

### Set Flags (Git-Based)
```python
from tools.utils.smart_manage_publish_flags import set_publish_flags

results = set_publish_flags(
    manifest_path=None,  # Auto-detect publish.yml
    commit="HEAD",
    base=None,  # Optional comparison base
    reset_others=False,  # Set non-matching to false
    dry_run=False,
    debug=False,
)

# Returns:
# {
#   "changed_files": [...],
#   "modified_entries": [...],
#   "any_build_true": bool
# }
```

### Reset Flags (Target-Based)
```python
from tools.utils.smart_manage_publish_flags import reset_publish_flags

results = reset_publish_flags(
    manifest_path=None,
    path="content/",  # Match by path
    out=None,  # Or match by output filename
    index=None,  # Or match by index (0-based)
    multi=False,  # Allow multiple matches
    error_on_no_match=False,
    dry_run=False,
    debug=False,
)

# Returns:
# {
#   "reset_count": int,
#   "matched_indices": [...],
#   "matched_paths": [...],
#   "matched_outs": [...],
#   "changed": [...]
# }
```

## Book.json Awareness

The new implementation uses `smart_publish_target` to resolve content roots from `book.json`:

```yaml
# publish.yml
publish:
  - path: "."
    use_book_json: true  # Discovers book.json in path
    # ... other fields
```

If `use_book_json: true`, the module will:
1. Call `discover_book(path)` to find `book.json`
2. Extract `content_root` from `book.json` (e.g., `"root": "./content"`)
3. Use `content_root` for path matching instead of entry `path`

This fixes the root path matching bug where `"release-notes.md" == "."` returned FALSE.

## Smart Merge Philosophy

The unified module follows Smart Merge hierarchy:

1. **Explicit**: Use `content_root` from `book.json` if `use_book_json: true`
2. **Convention**: Use `entry.path` if no book.json or `use_book_json: false`
3. **Fallback**: Gracefully handle missing resources

## CLI Compatibility

Old CLI calls continue to work (with deprecation warnings):

```bash
# Set flags (old syntax)
python tools/publishing/set_publish_flag.py --commit HEAD --reset-others

# Reset flags (old syntax)
python tools/publishing/reset_publish_flag.py --path content/ --multi
```

Warnings emitted:
```
DeprecationWarning: tools.publishing.set_publish_flag deprecated. 
Use tools.utils.smart_manage_publish_flags.set_publish_flags() instead.
```

## Testing

```bash
# Test set flags
python -m pytest tests/test_smart_manage_publish_flags.py::test_set_flags_with_book_json

# Test reset flags
python -m pytest tests/test_smart_manage_publish_flags.py::test_reset_flags_by_path

# Test CLI wrappers
python tools/publishing/set_publish_flag.py --dry-run --debug
python tools/publishing/reset_publish_flag.py --path "." --dry-run
```

## Removal Timeline

These wrapper files will be removed in **v2.0.0** (tentative).

All internal code should migrate to:
```python
from tools.utils.smart_manage_publish_flags import (
    set_publish_flags,
    reset_publish_flags,
)
```

## Related Modules

- `tools/utils/smart_book.py` - book.json discovery
- `tools/utils/smart_publish_target.py` - target resolution with book.json binding
- `tools/utils/smart_publisher.py` - publishing coordination
- `tools/utils/smart_manifest.py` - manifest resolution
- `tools/utils/content_discovery.py` - content discovery with Smart Merge

## See Also

- `tools/utils/README.md` - Smart modules overview
- `content-discovery-implementation.md` - Smart Merge documentation
