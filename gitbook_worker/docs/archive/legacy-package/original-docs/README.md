---
version: 1.1.0
created: 2025-11-10
modified: 2025-11-13
status: stable
type: index
---

# GitBook Worker Documentation

This directory contains all development documentation for the GitBook Worker publishing system.

## Directory Structure

### 📐 `architecture/`
System architecture and high-level overviews:
- `ARCHITECTURE-OVERVIEW.md` - Package architecture and structure
- `gitbook-worker-overview.md` - GitBook Worker capabilities overview

### 🔧 `implementations/`
Implementation summaries and technical details:
- `content-discovery-implementation.md` - Smart merge content discovery system
- `font-refactoring-summary.md` - Font configuration refactoring details
- `smart-merge-implementation.md` - Smart merge font configuration implementation

### 💡 `concepts/`
Technical concepts and design approaches:
- `font-config-hierarchy-concept.md` - Font configuration hierarchy design

### 🚀 `migrations/`
Migration guides and summaries:
- `MIGRATION-SUMMARY.md` - Package migration implementation summary
- `PACKAGE-MIGRATION.md` - Package structure migration guide
- `PHASE2-STANDALONE-PACKAGE.md` - Phase 2 standalone package plan
- `build-scripts-migration.md` - Build scripts migration summary

### 📚 `guides/`
How-to guides and configuration references:
- `FRONTMATTER.md` - Front matter configuration guide
- `naming-conventions.md` - Naming conventions and standards

### 🏃 `sprints/`
Sprint documentation and work-in-progress reports:
- `improve_capability/` - Capability improvement sprint

## Documentation Standards

All documents in this directory follow these standards:

1. **YAML Front Matter**: Every document includes semantic versioning and metadata
2. **Semantic Versioning**: Documents use `version: x.y.z` format
3. **Change Tracking**: Created and modified dates tracked in front matter
4. **Status Indicators**: Current state (stable/draft/planning/completed/etc.)
5. **Type Classification**: Document type (architecture/guide/migration/etc.)

## Related Documentation

- **Tool READMEs**: Each tool in `tools/` has its own README with usage details
- **AGENTS.md**: Agent directives for engineers and architects
- **Root docs**: Main project documentation in repository root

## Versioning

This documentation structure: **v1.0.0** (2025-11-10)
