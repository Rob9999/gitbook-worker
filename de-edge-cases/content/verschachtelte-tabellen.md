# Verschachtelte Tabellen und Code-Blöcke

## Einfache Tabelle

| Spalte A | Spalte B | Spalte C |
|----------|----------|----------|
| Wert 1   | Wert 2   | Wert 3   |
| Wert 4   | Wert 5   | Wert 6   |

## Tabelle mit Code

| Feature | Beispiel | Status |
|---------|----------|--------|
| Inline  | `code()` | ✅     |
| Block   | siehe unten | 🚧  |

## Code-Block direkt nach Tabelle

```python
def edge_case():
    """Code-Block nach Tabelle — testet Pandoc-Rendering."""
    return True
```

## Verschachtelter Inhalt

> **Zitat mit Tabelle:**
>
> | A | B |
> |---|---|
> | 1 | 2 |
>
> Ende des Zitats.

## Leere Tabelle

| | |
|---|---|
| | |
