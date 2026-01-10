---
title: Image examples – Captions & density
description: Test page for repeated figures and captions in a short sequence.
date: 2026-01-10
version: 1.0
doc_type: example
category: "image-test"
show_in_summary: true
history:
  - version: 1.0
---

# Image examples – Captions & density

This test page checks the behaviour with multiple images in quick succession. Particularly relevant for:

- **Page breaks**: How does the layout behave with many images?
- **Image captions**: Are captions positioned correctly?
- **Spacing**: Sufficient space between images?
- **Numbering**: Sequential image numbers in lists of figures?

## Gallery (SVG)

Multiple similar images in sequence test the layout:

![Neutral shapes – A](../.gitbook/assets/neutral-shapes.svg)

_Figure 1: First instance of shape representation_

![Neutral shapes – B](../.gitbook/assets/neutral-shapes.svg)

_Figure 2: Second instance to check for repetitions_

## Mixed (SVG + PNG)

Combination of different image formats in one section:

![Neutral grid](../.gitbook/assets/neutral-grid.svg)

_Figure 3: Vector graphic with grid pattern_

![ERDA Logo](../.gitbook/assets/ERDA_Logo_simple.png)

_Figure 4: Raster graphic (PNG format)_

## Technical aspects

### Image captions

Image captions should:

1. Clearly describe the image
2. Establish context to surrounding text
3. Include source references where needed
4. Be consistently numbered

### Layout challenges

When placing multiple images, the following aspects must be considered:

- **Widow/orphan control**: Don't separate captions from images
- **Page breaks**: Don't split large images in the middle
- **Spacing**: Sufficient space between elements
- **Alignment**: Consistent positioning

### Accessibility

For better accessibility:

- Every image gets a meaningful alt text
- Captions supplement visually presented information
- Colour schemes consider colour blindness
- Contrasts are sufficiently high
