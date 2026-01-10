---
title: Templates
date: 2024-06-02
version: 1.1
doc_type: template
---

# Templates

This directory contains reusable templates and patterns for documentation.

## Purpose

Templates provide:

- **Consistency**: Standardised structure across similar content
- **Efficiency**: Quick starting points for new documents
- **Quality**: Pre-validated formatting and metadata
- **Guidance**: Examples of best practices

## Available templates

### Multilingual neutral text

Template for content that must work across all language versions:

- Neutral cultural references
- Internationally recognised examples
- Language-independent code samples
- Universal symbols and notation

See [multilingual-neutral-text.md](multilingual-neutral-text.md) for details.

## Template structure

Each template includes:

```yaml
---
title: Template Name
date: YYYY-MM-DD
version: X.Y
doc_type: template
show_in_summary: false  # Usually hidden from main TOC
---
```

## How to use templates

1. **Copy** the template file to your target location
2. **Rename** to match your content purpose
3. **Update** frontmatter (title, date, version, doc_type)
4. **Replace** template content with your material
5. **Validate** structure and formatting

## Template categories

### Content templates

- Chapter structures
- Example patterns
- Reference documentation layouts

### Metadata templates

- Frontmatter configurations
- Navigation structures
- Build configurations

### Multilingual templates

- Parallel translation frameworks
- Language-neutral content patterns
- Internationalisation guidelines
