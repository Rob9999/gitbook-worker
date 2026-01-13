---
title: Image examples – Assets & layout
description: Neutral test images from .gitbook/assets (raster + SVG) for rendering and PDF regression tests.
date: 2026-01-10
version: 1.0
doc_type: example
category: "image-test"
show_in_summary: true
history:
  - version: 1.0
---

# Image examples – Assets & layout

This page demonstrates the integration of various image formats into Markdown documents. All assets used are located in the `content/.gitbook/assets/` directory and are legally safe.

## Image formats compared

### Raster images (PNG)

Raster images are suitable for:
- Photographs and complex graphics
- Images with many colour gradients
- Screenshots and screen captures

**Disadvantage**: Enlargement can lead to quality loss.

<div><figure><img src="../.gitbook/assets/SAMPLE_Logo_simple.png" alt="SAMPLE Logo"><figcaption><p>SAMPLE Logo (PNG)</p></figcaption></figure></div>

### Vector images (SVG)

Vector images offer:
- Arbitrary scalability without quality loss
- Small file sizes for simple graphics
- Sharp display on all screen resolutions

**Ideal for**: Diagrams, icons, technical drawings

![Neutral grid (SVG)](../.gitbook/assets/neutral-grid.svg)

### Diagrams and workflows

Structured representations such as flowcharts particularly benefit from vector graphics:

![Neutral workflow (SVG)](../.gitbook/assets/neutral-flow.svg)

## Best practices

### Image sizes

- **Web**: 72-96 DPI sufficient
- **Print**: At least 300 DPI for raster images
- **SVG**: Resolution-independent

### File formats

| Format | Use case | Transparency | Compression |
|--------|----------|--------------|-------------|
| PNG | Screenshots, logos | Yes | Lossless |
| JPEG | Photographs | No | Lossy |
| SVG | Diagrams, icons | Yes | Vector |
| WebP | Modern, web | Yes | Both modes |

### Alt texts

Every image should have a descriptive alt text:
- Improves accessibility
- Helps search engines
- Displayed when image cannot be loaded
