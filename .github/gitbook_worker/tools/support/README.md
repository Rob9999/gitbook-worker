# Support Utilities

Helper scripts that make it easier to inspect GitBook configuration and debug
publishing issues without running the full pipeline.

## Appendix layout inspector

`appendix_layout_inspector.py` mirrors the behaviour of the historical
`_test_appendix_check.py` script, but exposes it as a reusable module and CLI. It
inspects the resolved `SUMMARY.md` configuration, reports the active summary mode
and lists the top-level entries, making it straightforward to verify that
appendices are sorted to the end of the navigation tree.

Run the inspector with:

```bash
python -m tools.support.appendix_layout_inspector --base-dir . --appendices-last
```

The command prints the resolved summary path, mode/submode combination and the
ordered list of Markdown entries.  The module is primarily intended for tests but
is equally useful when debugging publishing issues locally.

## Development notes

* Keep dependencies limited to the shared `.github` virtual environment.
* When adding additional helpers, provide a short usage example so other team
  members can discover the scripts from this document.
