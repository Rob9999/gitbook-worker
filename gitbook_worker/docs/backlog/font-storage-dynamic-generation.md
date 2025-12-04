---
title: Dynamic Font Storage Generation from fonts.yml
version: 1.0.0
date: 2024-12-02
status: backlog
priority: high
labels: [fonts, architecture, single-source-of-truth]
---

# Dynamic Font Storage Generation from fonts.yml

## Problem Statement

Currently, `font_storage.py` contains hardcoded `FontBundleSpec` entries in `_DEFAULT_FONT_BUNDLES`. This violates the Single Source of Truth principle established in `AGENTS.md` - **fonts.yml should be the only configuration source for all fonts**.

**Current Issues:**
- Font configurations duplicated between `fonts.yml` and `font_storage.py`
- Manual sync required when adding/updating fonts
- Risk of configuration drift between local and Docker environments
- No validation that fonts.yml entries are actually downloadable

## Goals

1. **Single Source of Truth**: `fonts.yml` is the ONLY place where font metadata is defined
2. **Automatic Generation**: `FontBundleSpec` instances generated dynamically from `fonts.yml`
3. **Change Detection**: Detect when `fonts.yml` changes and trigger font storage rebuild
4. **Manual Control**: Provide CLI and launch.json options for manual rebuild
5. **Self-Sufficient**: All information needed must be in `fonts.yml`, downloaded archives, and `.env`
6. **Human-Readable Errors**: Clear, actionable error messages guiding users to solutions

## Architecture

### Component: FontBundleSpecGenerator

**Location**: `gitbook_worker/tools/publishing/font_bundle_generator.py`

**Responsibilities:**
```python
class FontBundleSpecGenerator:
    """Generates FontBundleSpec instances from fonts.yml configuration."""
    
    def __init__(self, fonts_yml_path: Path, repo_root: Path):
        """Load fonts.yml and prepare for generation."""
        
    def generate_specs(self) -> list[FontBundleSpec]:
        """Generate all FontBundleSpec entries from fonts.yml.
        
        For each font with download_url:
        - Extract slug from font key (e.g., "EMOJI" -> "twitter-color-emoji")
        - Parse version from fonts.yml
        - Download archive if needed to detect filenames
        - Generate required_files dict with checksums
        - Map license files
        """
        
    def detect_archive_structure(self, download_url: str) -> dict:
        """Download and inspect archive to discover:
        - Main font file(s) and their paths
        - License file names and locations
        - Required dependencies
        """
        
    def validate_spec(self, spec: FontBundleSpec) -> list[str]:
        """Validate that spec is complete and downloadable.
        
        Returns list of validation errors (empty if valid).
        """
```

### Change Detection System

**Location**: `gitbook_worker/tools/publishing/font_storage_watcher.py`

**Mechanism:**
```python
class FontStorageWatcher:
    """Detects changes to fonts.yml and triggers rebuild."""
    
    def __init__(self, fonts_yml_path: Path, storage_root: Path):
        self._fonts_yml = fonts_yml_path
        self._storage_root = storage_root
        self._state_file = storage_root / ".font-storage-state.json"
        
    def needs_rebuild(self) -> tuple[bool, str]:
        """Check if fonts.yml changed since last build.
        
        Returns:
            (needs_rebuild: bool, reason: str)
            
        Checks:
        - fonts.yml modification time vs. state file
        - fonts.yml content hash vs. stored hash
        - Missing font files in fonts-storage/
        """
        
    def record_build(self) -> None:
        """Record successful build in state file."""
        
    def prompt_user_for_rebuild(self) -> bool:
        """Interactive prompt asking user to rebuild.
        
        Displays:
        - Which fonts changed
        - Estimated download size
        - Command to rebuild: `python -m gitbook_worker.tools rebuild-fonts`
        """
```

**State File Format** (`.font-storage-state.json`):
```json
{
  "version": "1.0.0",
  "fonts_yml_hash": "sha256:abcd1234...",
  "fonts_yml_mtime": "2024-12-02T16:30:00Z",
  "last_build": "2024-12-02T16:30:00Z",
  "fonts": {
    "EMOJI": {
      "version": "15.1.0",
      "files_hash": "sha256:efgh5678..."
    },
    "MONO": {
      "version": "2.37",
      "files_hash": "sha256:ijkl9012..."
    }
  }
}
```

## Implementation Tasks

### Phase 1: Generator Foundation (2-3 hours)

- [ ] **Task 1.1**: Create `font_bundle_generator.py`
  - [ ] Parse fonts.yml using existing FontConfigLoader
  - [ ] Extract fonts with `download_url` field
  - [ ] Generate basic FontBundleSpec without checksums
  - [ ] Unit tests for YAML parsing

- [ ] **Task 1.2**: Archive Structure Detection
  - [ ] Implement `detect_archive_structure()`
  - [ ] Download to temp directory
  - [ ] Extract and scan for .ttf/.otf files
  - [ ] Find LICENSE/README files
  - [ ] Handle zip, tar.gz, tar.bz2 formats
  - [ ] Tests with mock archives

### Phase 2: Change Detection (2 hours)

- [ ] **Task 2.1**: Create `font_storage_watcher.py`
  - [ ] Implement state file management
  - [ ] Hash calculation for fonts.yml
  - [ ] Modification time tracking
  - [ ] File existence validation

- [ ] **Task 2.2**: Integration into SmartFontStack
  - [ ] Call `needs_rebuild()` in `_maybe_bootstrap_font_storage()`
  - [ ] Interactive prompt on detected changes
  - [ ] Automatic rebuild if non-interactive (CI/CD)
  - [ ] Tests for change detection logic

### Phase 3: CLI Commands (1-2 hours)

- [ ] **Task 3.1**: Add `rebuild-fonts` command to orchestrator
  ```bash
  python -m gitbook_worker.tools.workflow_orchestrator rebuild-fonts
    [--force]           # Ignore change detection
    [--validate-only]   # Validate fonts.yml without downloading
    [--font EMOJI]      # Rebuild only specific font
  ```

- [ ] **Task 3.2**: Create standalone CLI
  ```bash
  python -m gitbook_worker.tools.publishing.rebuild_fonts
    [--config fonts.yml]
    [--storage-root fonts-storage]
    [--force]
  ```

### Phase 4: VS Code Integration (30 minutes)

- [ ] **Task 4.1**: Add launch.json configuration
  ```json
  {
    "name": "Rebuild Font Storage",
    "type": "python",
    "request": "launch",
    "module": "gitbook_worker.tools.publishing.rebuild_fonts",
    "args": ["--config", "${workspaceFolder}/gitbook_worker/defaults/fonts.yml"],
    "console": "integratedTerminal"
  }
  ```

- [ ] **Task 4.2**: Add VS Code task in `.vscode/tasks.json`
  ```json
  {
    "label": "Rebuild Fonts",
    "type": "shell",
    "command": "python -m gitbook_worker.tools.publishing.rebuild_fonts",
    "problemMatcher": []
  }
  ```

### Phase 5: Documentation & Error Messages (2-3 hours)

- [ ] **Task 5.1**: User Documentation (`docs/font-management.md`)
  - [ ] Overview of font storage system
  - [ ] How to add new fonts to fonts.yml
  - [ ] Required fields (download_url, version, license)
  - [ ] Triggering rebuilds (automatic vs. manual)
  - [ ] Troubleshooting common issues

- [ ] **Task 5.2**: Error Message Templates
  ```python
  ERROR_TEMPLATES = {
      "download_failed": """
  ❌ Font Download Failed: {font_name}
  
  URL: {url}
  Error: {error}
  
  Troubleshooting:
  1. Check internet connection
  2. Verify URL is accessible: curl -I {url}
  3. Check if GitHub rate limit exceeded
  4. Try manual download and place in fonts-storage/{slug}/
  
  See: docs/font-management.md#troubleshooting-downloads
  """,
      
      "invalid_archive": """
  ❌ Invalid Font Archive: {font_name}
  
  Archive: {archive_path}
  Expected files: {expected_files}
  Found files: {found_files}
  
  The downloaded archive doesn't contain expected font files.
  This may indicate:
  - fonts.yml has incorrect download_url
  - Archive format changed (check latest release)
  - Archive extracted to unexpected directory structure
  
  Manual Fix:
  1. Download manually: {url}
  2. Extract and verify contents
  3. Update fonts.yml if structure changed
  4. Run: python -m gitbook_worker.tools.publishing.rebuild_fonts
  
  See: docs/font-management.md#archive-structure-issues
  """,
      
      "checksum_mismatch": """
  ⚠️  Font Checksum Mismatch: {font_name}
  
  File: {file_path}
  Expected: {expected_hash}
  Actual: {actual_hash}
  
  This usually means:
  - Font file was updated by publisher
  - Local file corruption
  - fonts.yml has outdated checksum
  
  Safe Actions:
  1. Delete: fonts-storage/{slug}/
  2. Rebuild: python -m gitbook_worker.tools.publishing.rebuild_fonts --font {key}
  3. If problem persists, update checksum in fonts.yml
  
  See: docs/font-management.md#checksum-validation
  """
  }
  ```

- [ ] **Task 5.3**: Developer Documentation
  - [ ] Architecture diagram (ASCII art in markdown)
  - [ ] Class relationships
  - [ ] Extension points for new font sources
  - [ ] Testing strategy

### Phase 6: Validation & Testing (2 hours)

- [ ] **Task 6.1**: Integration Tests
  - [ ] Test full rebuild cycle
  - [ ] Test incremental updates (only changed fonts)
  - [ ] Test change detection accuracy
  - [ ] Test error handling paths

- [ ] **Task 6.2**: Documentation Tests
  - [ ] Verify all error messages are helpful
  - [ ] Test with intentionally broken configs
  - [ ] Validate troubleshooting steps work

## fonts.yml Requirements

For dynamic generation to work, each font entry with `download_url` must include:

```yaml
fonts:
  EMOJI:
    name: "Twemoji Mozilla"              # Required: fontconfig family name
    version: "15.1.0"                         # Required: for state tracking
    download_url: "https://..."               # Required: source archive
    license: "CC BY 4.0"                      # Required: for license compliance
    license_url: "https://..."                # Required: for attribution
    source_url: "https://github.com/..."      # Optional: project homepage
    paths:                                     # Auto-populated after first download
      - "fonts-storage/twitter-color-emoji/TwitterColorEmoji-SVGinOT.ttf"
    archive_structure:                        # Optional: override auto-detection
      font_files:
        - "TwitterColorEmoji-SVGinOT.ttf"
      license_files:
        "LICENSE.md": "LICENSE.txt"
    checksum:                                 # Auto-generated after first download
      sha256: "abcd1234..."
```

**Auto-Detection Rules:**
1. If `archive_structure` not specified, download and scan archive
2. Find all `.ttf` and `.otf` files
3. Find `LICENSE*`, `COPYING*`, `README*` files
4. Generate checksum on first successful download
5. Update fonts.yml with detected structure (optional, for performance)

## Environment Variables

Optional configuration via `.env`:

```bash
# GitHub API token for higher rate limits (public repos don't require auth)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx

# Custom download timeout (default: 300s)
FONT_DOWNLOAD_TIMEOUT=600

# Disable automatic rebuild prompts (CI/CD environments)
FONT_STORAGE_AUTO_REBUILD=false

# Verbose logging for font operations
FONT_STORAGE_DEBUG=true
```

## Migration Plan

### Step 1: Parallel Operation (Week 1)
- Implement generator alongside existing hardcoded specs
- Test with small subset of fonts
- Validate generated specs match hardcoded ones

### Step 2: Gradual Rollout (Week 2)
- Use generated specs in development environments
- Monitor for issues
- Gather feedback on error messages

### Step 3: Full Migration (Week 3)
- Switch production to generated specs
- Remove hardcoded `_DEFAULT_FONT_BUNDLES`
- Update all documentation
- Announce deprecation of manual font_storage.py edits

### Step 4: Enhancement (Week 4+)
- Add font validation service (check URLs still valid)
- Implement font update notifications
- Add font usage analytics (which fonts actually used)

## Success Metrics

- [ ] Zero manual edits to `font_storage.py` required
- [ ] fonts.yml is single source for font metadata
- [ ] Users can add fonts by editing only fonts.yml
- [ ] Error messages resolve 90%+ of issues without developer intervention
- [ ] Font storage rebuilds complete in <60 seconds for typical configs
- [ ] Change detection has 100% accuracy (no false positives/negatives)

## Related Issues

- AGENTS.md Section 12-14: Font Management & License Compliance
- `smart-font-stack.md`: Leitprinzipien #5
- Font cache optimization (completed in this sprint)

## Notes

- **License Compliance**: Generator MUST validate all fonts have license info
- **Reproducibility**: Checksums ensure identical builds across machines
- **Performance**: Cache archive structure detection results in fonts.yml
- **Security**: Validate download URLs (https only, known domains)
- **Accessibility**: Error messages in German and English

## Open Questions

1. Should we auto-update fonts.yml with detected archive structure, or keep it read-only?
   - **Recommendation**: Auto-update only checksums, manual for structure
   
2. How to handle font version updates? Auto-detect newer versions?
   - **Recommendation**: Manual version bumps in fonts.yml, then rebuild
   
3. Should we support multiple download mirrors for redundancy?
   - **Recommendation**: Phase 2 feature, single URL for MVP

4. How to handle fonts that require account/API key to download?
   - **Recommendation**: Support `FONT_{KEY}_DOWNLOAD_URL` env var override

## Estimated Effort

**Total**: 10-13 hours
- Phase 1: 2-3 hours
- Phase 2: 2 hours
- Phase 3: 1-2 hours
- Phase 4: 30 minutes
- Phase 5: 2-3 hours
- Phase 6: 2 hours

**Team Size**: 1 developer
**Timeline**: 2-3 days (with testing and documentation)
**Risk**: Low (isolated change, good test coverage possible)
