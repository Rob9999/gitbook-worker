---
title: Translator's Note
doc_type: translators-note
order: 6
---

# Translator's Note

This document demonstrates multilingual publishing capabilities and translation workflows.

## Translation principles

When translating technical documentation:

- **Terminology consistency**: Maintain consistent translation of technical terms
- **Cultural adaptation**: Adapt examples and metaphors to target culture
- **Format preservation**: Keep structure, headings, and formatting identical
- **Technical accuracy**: Verify all code examples, commands, and references

## Language considerations

### British English conventions

This English version follows British English spelling and grammar conventions:

- Spelling: colour, organise, licence (noun)
- Punctuation: Single quotes for regular text, double for nested
- Date format: DD/MM/YYYY
- Number formatting: Comma for thousands (1,000)

### Unicode support

The document includes extensive Unicode content:

- **100+ languages**: Covering major writing systems
- **Emoji rendering**: Proper display of flags, symbols, and combined sequences
- **Right-to-left text**: Support for Arabic, Hebrew, and other RTL scripts

## Translation workflow

Content is maintained in parallel language directories:

```
de/     # German (Deutsch)
en/     # English (British)
```

Each language maintains:

- Independent SUMMARY.md (navigation structure)
- Language-specific metadata (book.json)
- Localised frontmatter and terminology
