---
version: 0.1.0
date: 2025-12-28
history: Initial overview for hexagonal refactor track.
---

# Hexagonal Architecture Track – Overview

## Intent
Move the GitBook Worker toolchain toward a modular monolith with clear ports/adapters, enabling testable core logic and swappable infrastructure (renderers, storage, font backends).

## Guiding Principles
- Domain-first: core logic free of I/O, subprocess, and OS assumptions.
- Ports over imports: adapters provide filesystems, processes, renderers, fonts, and asset storage.
- Reproducibility: deterministic builds, explicit font sources, no implicit environment coupling.
- Small, verifiable steps: each sprint delivers a thin slice that keeps current behaviour intact.

## Target Module Boundaries
- Domain: project config, conversion plan, font policy, licence policy, citation rules.
- Application (use-cases): publish workflow, conversion orchestration, validation, font sync orchestration.
- Adapters: CLI, filesystem, subprocess/process runner, renderer (Pandoc/LuaLaTeX), font discovery, asset storage.
- Plugins: converters per input/output pair registered via a lightweight registry.

## Sprint Themes (first waves)
1) Stabilise Ports: extract process runner, filesystem, font OS setup, asset storage.
2) Use-case Shells: carve out publish/conversion use-cases that depend only on ports.
3) Plugin Surface: define converter registry contract and migrate one converter.
4) Hardening: regression tests around use-cases and adapters (including Windows paths and font cache hints).

## Success Criteria
- Domain/application layers run in unit tests without touching disk or subprocess.
- Publisher/orchestrator logic uses injected ports, no direct `subprocess.run` or raw path munging.
- Asset/font handling lives behind adapters; behaviour remains backward compatible.
- New converters can be added without modifying domain/application code (registry only).
