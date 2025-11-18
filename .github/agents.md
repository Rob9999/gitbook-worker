# Agents `.github` Workflow Tools

Follow these rules whenever you edit or add automation code under `.github`.

1. Treat `.github` as an isolated Python project.
   - Keep dependencies in `pyproject.toml` and install them only into `.venv/` inside this directory.
   - Use `.vscode/settings.json` to point at that interpreter; do not rely on repo-level path tricks.
2. Maintain documentation.
   - Update `.github/README.md` after structural or tooling changes.
   - Document new scripts or CLIs under `tools/` with docstrings and module-level comments when behaviour is non-obvious.
3. Code quality.
   - Format with `black`, sort imports with `isort`, and lint with `flake8` (configure via pre-commit if possible).
   - Require type hints on new functions and classes; prefer `pathlib.Path` for file work.
4. Testing.
   - Add or update tests in `tests/` for every new feature or bug fix. Run `pytest` locally before opening a PR.
   - Keep fixtures self-contained and avoid network or file-system side effects beyond the project tree.
5. Workflows.
   - When adjusting GitHub Actions (`workflows/`), ensure the Python steps create/activate the local `.venv` or use the published package rather than relying on global installs.
6. Propagation.
   - For any new top-level Python project contributed by partners, replicate this `agents.md` template and adapt it to their directory so the shared workflow remains consistent.
