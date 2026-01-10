---
title: Appendix A – Data sources and table layout
date: 2024-06-01
version: 1.0
doc_type: appendix
appendix_id: "A"
category: "technical"
---

# Appendix A – Data sources and table layout

This appendix documents the data sources and structural conventions used in tables throughout this document.

## Table design principles

### Readability

Tables are designed for:

- **Quick scanning**: Clear headers and consistent alignment
- **Data comparison**: Parallel structure for easy comparison
- **Reference use**: Complete information without requiring external context

### Consistency

All tables follow:

- Consistent column ordering
- Uniform header formatting
- Standard alignment rules (left for text, right for numbers)
- Descriptive captions

## Table types

### Comparative tables

Structure for comparing options:

| Feature | Option A | Option B | Option C |
|---------|----------|----------|----------|
| Performance | High | Medium | Low |
| Complexity | Low | Medium | High |
| Cost | Low | Medium | High |

### Reference tables

Data lookup format:

| Key | Value | Description |
|-----|-------|-------------|
| Term 1 | Definition | Detailed explanation |
| Term 2 | Definition | Detailed explanation |

### Multi-level tables

Hierarchical information:

| Category | Subcategory | Details |
|----------|-------------|----------|
| Type A | Variant 1 | Specifications |
| | Variant 2 | Specifications |
| Type B | Variant 1 | Specifications |

## Data sources

### Primary sources

Tables are compiled from:

- Official documentation and specifications
- Published standards (ISO, RFC, etc.)
- Peer-reviewed research where applicable
- Vendor documentation and release notes

### Data verification

All tabulated data:

1. Cross-referenced with primary sources
2. Verified for current accuracy
3. Dated to indicate currency
4. Linked to source documentation where possible

### Update policy

Tables are reviewed:

- During major version updates
- When underlying specifications change
- Following significant technology releases
- As corrections are identified

## Formatting conventions

### Numerical data

- **Integers**: No decimal separator (1000, not 1,000)
- **Decimals**: Period as decimal separator (3.14)
- **Percentages**: Number followed by % symbol (85%)
- **Ranges**: En dash between values (10–20)

### Text alignment

- **Left-aligned**: Text, descriptions, category names
- **Right-aligned**: Numbers, dates, versions
- **Centre-aligned**: Yes/No, checkmarks, symbols

### Special symbols

- ✓ = Supported/Yes
- ✗ = Not supported/No
- — = Not applicable
- ≈ = Approximately
- ≥/≤ = Greater/less than or equal

## Caption format

Table captions include:

```markdown
Table X.Y: Descriptive title
```

Where:

- X = Chapter number
- Y = Sequential table number within chapter
- Title describes content succinctly

## Accessibility

### Screen readers

Tables use:

- Proper Markdown table syntax for correct HTML rendering
- Descriptive headers that work when read sequentially
- Captions that provide context independent of surrounding text

### Print readability

Table design considers:

- Page width constraints in PDF output
- Readability at standard print sizes
- Clear distinction between header and data rows

### Example table

| Item | Purpose |
|---|---|
| Heading | TOC/bookmarks |
| Table | list of tables |

### Example code block

```
python -m gitbook_worker.tools.workflow_orchestrator --help
```
