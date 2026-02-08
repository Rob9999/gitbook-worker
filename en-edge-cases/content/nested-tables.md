# Nested Tables and Code Blocks

## Simple Table

| Column A | Column B | Column C |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |

## Table with Code

| Feature | Example  | Status |
|---------|----------|--------|
| Inline  | `code()` | ✅     |
| Block   | see below | 🚧   |

## Code Block after Table

```python
def edge_case():
    """Code block after table — tests Pandoc rendering."""
    return True
```

## Nested Content

> **Quote with table:**
>
> | A | B |
> |---|---|
> | 1 | 2 |
>
> End of quote.

## Empty Table

| | |
|---|---|
| | |
