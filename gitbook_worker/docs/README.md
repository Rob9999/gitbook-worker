---
version: 1.0.0
date: 2025-12-07
history: Documented PDF font fallback reporting/abort semantics for developers.
---

# Developer Docs

## PDF font fallback behavior

1. Missing glyph detection and reporting
The PDF build shall detect whenever a glyph required by the document cannot be rendered by the configured primary fonts. For all such cases, the build shall produce a clear, detailed report listing:
- the affected code points (and, if possible, their Unicode names),
- the fonts that were attempted,
- and the fact that they could not provide a valid glyph (i.e. the result would be a .notdef / empty box).
This report shall be written to the build log for troubleshooting.

2. Use of the mainfontfallback stack
The `mainfontfallback` stack exists to prevent missing-glyph boxes, not just to check font availability. For every glyph that the primary fonts cannot render, the PDF build shall try each font in the `mainfontfallback` stack in order and use the first fallback font that can provide a proper glyph (e.g. a regular text glyph, emoji glyph, etc.). As long as every required glyph can be rendered either by a primary font or by at least one font in the `mainfontfallback` stack, the PDF build shall succeed and no .notdef / empty box glyphs shall appear in the output.

3. Abort condition
The PDF build shall abort only if, after trying all configured primary fonts and all fonts in the `mainfontfallback` stack, there remains at least one required glyph that would still be rendered as a missing-glyph box (.notdef). In that case, the pipeline shall fail and emit the detailed missing-glyph report described in (1), instead of silently producing a PDF with empty boxes.

Control: `publish.yml` can opt out per entry via `pdf_options.abort_if_missing_glyph: false` (default: true). The missing-glyph report is still emitted even when the abort is disabled.

4. Central font configuration
a) All fonts, including the primary ones and the `mainfontfallback` ones, shall be configured exclusively in `gitbook_worker/defaults/fonts.yml`. 
b) In the unique book project `publish.yml` then is defined which fonts finally shall be used for the book project; e.g. as main font, as, sans font, as ... font, as mainfont fallback. 
c) The publishing header shall apply the configured fallback stack automatically; individual documents shall not configure their own font fallback behavior.


