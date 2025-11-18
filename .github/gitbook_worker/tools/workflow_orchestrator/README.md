# Workflow Orchestrator

High-level CLI that coordinates the publishing, conversion and QA steps defined
in `publish.yml`.  This is the entry point used by GitHub Actions workflows and
local automation scripts.

## Usage

List available options and steps:

```bash
python -m tools.workflow_orchestrator --help
```

Dry-run the default profile configured in `publish.yml`:

```bash
python -m tools.workflow_orchestrator --profile default --dry-run
```

Override the manifest path and execute specific steps:

```bash
python -m tools.workflow_orchestrator \
  --manifest publish.yml \
  --profile nightly \
  --steps check_if_to_publish converter publisher
```

The orchestrator resolves the profile, expands templates, merges environment
variables and executes each step in order.  Steps map to scripts hosted in the
`publishing`, `converter`, `quality`, `emoji` and `support` packages.

## Implementation overview

* `orchestrator.py` parses command-line arguments, loads the manifest and builds
  the runtime configuration.
* `profiles.py` reads `publish.yml` and materialises the selected profile.
* `runner.py` executes the configured steps, exporting a consistent environment
  (log directories, manifest path, workspace root) for subprocesses.
* Additional helpers in `config.py`, `state.py` and `util.py` normalise file
  paths and provide shared constants.

## Development checklist

1. Update `pytest` coverage in `.github/tests/` when adding new steps or profile
   fields.
2. Keep the command examples above in sync with new arguments.
3. Ensure new steps are documented both here and in the module they delegate to
   so workflow authors understand the behaviour.
