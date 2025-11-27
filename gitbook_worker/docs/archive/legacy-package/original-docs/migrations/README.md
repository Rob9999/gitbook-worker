---
version: 1.0.0
created: 2025-11-10
modified: 2025-11-10
status: stable
type: index
---

# Migration Documentation

## Documents

### MIGRATION-SUMMARY.md
**Status:** Completed | **Created:** 2025-11-09 | **Phase:** 1

Implementation summary of Phase 1 foundation for transitioning from legacy `tools.*` to `gitbook_worker.tools.*` package hierarchy. Covers import analysis, shim implementation, and backward compatibility.

### PACKAGE-MIGRATION.md
**Status:** In Progress | **Created:** 2025-11-09

Comprehensive guide for package structure migration including goals, current vs. target structure, shim mechanisms, transition strategy, and rollout phases.

### PHASE2-STANDALONE-PACKAGE.md
**Status:** Planning | **Created:** 2025-11-09 | **Target:** Q1 2026

Phase 2 plan for extracting `gitbook_worker.tools` into an independent `erda-workflow-tools` package that can be installed via pip and used by multiple projects.

### build-scripts-migration.md
**Status:** Completed | **Created:** 2025-11-07

Summary of build scripts modernization, including migration to `.github/gitbook_worker/scripts/` with PowerShell and Bash equivalents, and workflow profile support.

## Purpose

This directory contains migration guides, plans, and summaries documenting the evolution and restructuring of the GitBook Worker system.
