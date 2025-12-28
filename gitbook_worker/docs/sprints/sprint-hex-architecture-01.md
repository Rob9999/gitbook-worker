---
version: 0.1.0
date: 2025-12-28
history: Kickoff sprint for hexagonal refactor track.
---

# Sprint 01 – Hexagonal Foundations

## Goal
Introduce explicit ports for process execution and asset handling, and wrap publisher/orchestrator logic with a use-case shell that depends only on those ports.

## Scope
- Extract a `ProcessRunnerPort` and adapt existing subprocess usage in publisher and orchestrator.
- Formalise `AssetStoragePort` around the current `copy_assets_to_temp` behaviour.
- Provide a thin `PublishUseCase` that composes these ports without direct filesystem/subprocess calls.
- Keep behaviour backward compatible (paths, env vars, logging).

## Deliverables
- New port interfaces and default adapters (process runner, asset storage) under `gitbook_worker/tools/utils`.
- Publisher wired to ports (no raw `subprocess.run` in core flow).
- Orchestrator delegating command execution to `ProcessRunnerPort`.
- Regression tests for the new adapters and the `PublishUseCase` happy-path.

## Stories / Tasks
1. Define `ProcessRunnerPort` (sync run, env injection, cwd, logging) and implement a default adapter using subprocess; add unit tests with a fake runner.
2. Define `AssetStoragePort` mirroring `copy_assets_to_temp`; keep .gitbook/assets handling; add tests for relative/absolute asset paths.
3. Extract `PublishUseCase` that orchestrates manifest resolution and delegates execution to ports; keep CLI surface unchanged.
4. Refactor orchestrator to accept a process runner dependency; cover with a basic regression test that mocks external calls.
5. Add developer notes in `docs/sprints/` about port usage and migration steps for future adapters (renderer, font OS config).

## Risks / Notes
- Windows path handling and OSFONTDIR setup must remain intact; add guards in adapters where needed.
- Ensure logs stay informative (retain existing INFO/WARN/ERROR patterns) to avoid debugging regressions.
- Tests must not rely on system fonts or real subprocesses; use fakes/mocks for ports.
