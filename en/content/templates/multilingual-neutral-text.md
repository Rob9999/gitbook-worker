---
title: Template for multilingual neutral text
date: 2024-06-02
version: 1.1
doc_type: template
show_in_summary: false
---

# Template for multilingual neutral text

This template provides guidelines for creating content suitable for all language versions.

## Principles

Multilingual neutral content:

- **Cultural neutrality**: Avoid culture-specific references, idioms, or examples
- **Universal concepts**: Use internationally recognised ideas and terminology
- **Technical focus**: Emphasise technical accuracy over cultural context
- **Symbol preference**: Use symbols, diagrams, and code over prose where possible

## Language considerations

### Avoid

❌ **Culture-specific examples:**

```markdown
Like preparing a traditional Sunday roast...
As American as apple pie...
```

❌ **Regional idioms:**

```markdown
It's raining cats and dogs
The proof is in the pudding
```

❌ **Country-specific references:**

```markdown
As required by UK GDPR...
Similar to the US ZIP code system...
```

### Prefer

✅ **Universal examples:**

```markdown
Like preparing a meal...
A widely recognised pattern...
```

✅ **Clear, literal language:**

```markdown
Heavy rainfall
Evidence demonstrates that...
```

✅ **International standards:**

```markdown
As required by ISO 8601...
Following RFC 3339 date format...
```

## Content patterns

### Technical documentation

Technical content is naturally more neutral:

```markdown
## Installation

1. Download the package
2. Extract to a directory
3. Run the installer
4. Verify installation with `command --version`
```

### Code examples

Code transcends language barriers:

```python
# Universal technical concepts
def calculate_total(items):
    return sum(item.price for item in items)
```

### Mathematical notation

Mathematics is international:

```markdown
The Pythagorean theorem: $a^2 + b^2 = c^2$
```

### Visual elements

Diagrams and symbols work across languages:

- Flowcharts
- Sequence diagrams
- Icons and symbols (Unicode)
- Tables and matrices

## Metadata structure

For multilingual documents:

```yaml
---
title: Your Title
date: YYYY-MM-DD
version: X.Y
doc_type: chapter  # or appropriate type
language_neutral: true  # Flag for neutral content
translation_notes: "Focus on technical accuracy"
---
```

## Testing checklist

Before publishing multilingual content:

- [ ] No culture-specific references
- [ ] No idioms or colloquialisms
- [ ] Technical terms properly defined
- [ ] Code examples are universal
- [ ] Numbers and dates use ISO formats
- [ ] Currency symbols avoided (use generic "units")
- [ ] Time zones specified if relevant
- [ ] Measurements use metric (SI) units

## Translation workflow

When translating neutral content:

1. **Preserve structure**: Keep headings and formatting identical
2. **Technical accuracy**: Verify technical terms in target language
3. **Literal translation**: Avoid creative interpretation
4. **Code unchanged**: Never translate code variable names or commands
5. **Metadata sync**: Keep version and date metadata consistent
