---
title: Templates
date: 2024-06-02
version: 1.1
---

# Templates

This folder contains reusable text templates for multilingual, neutral documentation.

## Available Templates

### [Multilingual Neutral Text](multilingual-neutral-text.md)

A structured template for international documentation featuring:
- **Neutral phrasing**: No culture-, brand-, or person-specific terms
- **Multilingualism**: Example texts in 10+ major languages (DE, EN, FR, ES, ZH, JA, AR, HI, RU, PT)
- **Consistent structure**: Context description → Language-specific paragraphs → Tables

**Use Cases**:
- Template for global documentation projects
- Test material for Unicode coverage and font rendering
- Demonstration object for multilingual PDF generation

## Template Structure

Each template follows this schema:

```markdown
---
title: Template Title
date: YYYY-MM-DD
version: X.Y
---

# Context
Brief description of the scenario.

## Language (ISO Code)
Neutral paragraph without culture-specific references.
```

## Best Practices

**When using templates**:
- ✅ Use short, concise sentences
- ✅ Avoid idiomatic expressions
- ✅ Use ISO language codes (de-DE, en-US, fr-FR, etc.)
- ✅ Document modifications in version history
- ❌ No personally identifiable information
- ❌ No brand names without necessity
- ❌ No culture-specific metaphors

## Extension

New templates should:
1. Have YAML front matter with `title`, `date`, `version`
2. Cover at least 3 languages (DE, EN, +1)
3. Be documented in version history
4. Contain neutral, reusable text blocks

---

*This folder is expanded as needed. Suggestions for new templates are welcome.*
