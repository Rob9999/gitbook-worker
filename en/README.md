# English Edition (WIP)

This directory hosts the upcoming English translation of the ERDA GitBook. It mirrors the
`de/` structure (content, book.json, publish artifacts) but intentionally ships only with
scaffolding for now:

- `content/` contains placeholder files so contributors can add translated chapters.
- `book.json` and `publish.yml` will be copied from `de/` once the first chapters land.
- CI keeps `build: false` for `en` until the translation is ready for smoke PDFs.

See `docs/multilingual-content-guide.md` for instructions on adding a new language tree.
