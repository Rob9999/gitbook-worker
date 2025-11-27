---
version: 1.0.0
created: 2025-11-10
modified: 2025-11-10
status: stable
type: configuration-guide
---

# Front Matter Configuration in publish.yml

This document describes how to configure YAML front matter injection in `publish.yml`.

## Overview

The front matter system allows you to automatically inject YAML metadata into markdown files during the workflow orchestration. This is controlled by:

1. **Global defaults**: `.github/gitbook_worker/defaults/frontmatter.yml`
2. **Per-publication overrides**: `frontmatter:` section in `publish.yml`

## Configuration Schema

### Global Default (`frontmatter.yml`)

```yaml
version: 1.0.0

# Global enable/disable switch (default: false means no injection)
enabled: false

# Smart pattern matching for which files should receive front matter
patterns:
  # Include patterns (glob syntax, relative to repository root)
  include:
    - "content/**/*.md"
  
  # Exclude patterns (take precedence over include)
  exclude:
    - "**/readme.md"
    - "**/README.md"

# Front matter template (for book chapters and engineering documents)
template:
  id: ""
  title: ""
  version: "v0.0.0"
  state: "DRAFT"
  evolution: ""
  discipline: ""
  system: []
  system_id: []
  seq: []
  owner: ""
  reviewers: []
  source_of_truth: false
  supersedes: null
  superseded_by: null
  rfc_links: []
  adr_links: []
  cr_links: []
  date: "{{date}}"  # Auto-populated from git commit date
  lang: "EN"
```

### Per-Publication Override (`publish.yml`)

You can override any aspect of the front matter configuration per publication:

```yaml
version: 0.1.0

# ... profiles, meta, fonts, etc. ...

# Global frontmatter override (applies to all publications unless overridden)
frontmatter:
  enabled: true  # Enable front matter injection
  patterns:
    include:
      - "docs/**/*.md"
    exclude:
      - "**/README.md"
  template:
    # Only need to specify fields you want to override
    state: "APPROVED"
    lang: "DE"

publish:
  - path: ./
    out_format: pdf
    # ... other publish settings ...
    
    # Per-publication frontmatter override (merges with global override)
    frontmatter:
      enabled: false  # Disable for this specific publication
```

## Merging Behavior

The configuration is merged in the following order (later overrides earlier):

1. **Defaults** from `frontmatter.yml`
2. **Global override** from top-level `frontmatter:` in `publish.yml`
3. **Publication override** from `frontmatter:` under specific publication entry

### Example Merge

**frontmatter.yml:**
```yaml
enabled: false
patterns:
  include: ["content/**/*.md"]
  exclude: ["**/readme.md"]
template:
  state: "DRAFT"
  lang: "EN"
```

**publish.yml:**
```yaml
frontmatter:
  enabled: true      # Override: now enabled
  template:
    state: "REVIEW"  # Override: change state to REVIEW
                     # lang: "EN" is inherited from default
```

**Result:**
- enabled: `true` (from override)
- patterns: `include=["content/**/*.md"], exclude=["**/readme.md"]` (from default)
- template.state: `"REVIEW"` (from override)
- template.lang: `"EN"` (from default)

## Pattern Matching

Patterns use glob syntax relative to repository root:

- `**/*.md` - All markdown files recursively
- `content/**/*.md` - All markdown in `content/` and subdirectories
- `**/README.md` - All README.md files anywhere
- `docs/guides/*.md` - Markdown files directly in `docs/guides/`

**Exclusion takes precedence**: If a file matches both include and exclude patterns, it will be excluded.

## Template Placeholders

The following special placeholders are supported in template values:

- `{{date}}` - Replaced with the last git commit date of the file (YYYY-MM-DD format)

## Disabling Front Matter

To disable front matter injection entirely:

**Option 1:** In `frontmatter.yml` (affects all publications):
```yaml
enabled: false
```

**Option 2:** In `publish.yml` (per publication):
```yaml
publish:
  - path: ./
    frontmatter:
      enabled: false
```

**Option 3:** Don't include `frontmatter:` section at all (defaults to disabled).

## Current Implementation Status

✅ **Implemented:**
- Global defaults in `frontmatter.yml`
- Pattern matching (include/exclude globs)
- Template definition with 17 fields
- `{{date}}` placeholder (git commit date)
- FrontMatterConfigLoader with merge support
- Integration with orchestrator.py

🚧 **In Progress:**
- Per-publication override support in `publish.yml` schema
- Documentation in README

📋 **TODO:**
- Add validation for frontmatter section in publish.yml
- Add unit tests for merge behavior
- Document in main README.md
