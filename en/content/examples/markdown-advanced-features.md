---
title: Markdown Advanced Features
date: 2026-01-11
version: 1.0
doc_type: example
category: documentation-features
---

# Markdown Advanced Features

This page demonstrates advanced Markdown syntax and features beyond basic formatting.

## Task Lists

- [x] Basic Markdown syntax documented
- [x] Emoji support implemented
- [x] Multilingual content tested
- [ ] Interactive examples added
- [ ] Video tutorials created
- [ ] Community feedback incorporated

### Nested Task Lists

- [x] Phase 1: Planning
  - [x] Requirements gathering
  - [x] Architecture design
- [x] Phase 2: Implementation
  - [x] Core features
  - [ ] Advanced features
- [ ] Phase 3: Release
  - [ ] Beta testing
  - [ ] Documentation review

## Strikethrough

~~This text is crossed out.~~

You can combine strikethrough with other formatting: ~~**bold and struck**~~ or ~~*italic and struck*~~.

This is useful for showing ~~deprecated~~ obsolete features or corrections.

## Subscript and Superscript

### Subscript

Water molecule: H~2~O

Chemical formula: C~6~H~12~O~6~ (glucose)

### Superscript

Mathematical notation: E = mc^2^

Footnote reference^[1]^

Exponentials: 2^10^ = 1024

## Highlighting / Mark

This is ==highlighted text== using the mark syntax.

You can ==**combine highlighting with bold**== or ==*with italic*==.

Use highlighting to ==draw attention to important information==.

## Definition Lists

Term 1
: Definition of term 1 with inline `code`.

Term 2
: First definition of term 2.
: Second definition of term 2.

API
: Application Programming Interface
: A set of protocols and tools for building software applications.

Markdown
: A lightweight markup language with plain text formatting syntax.
: Created by John Gruber in 2004.

## Abbreviations

The HTML specification is maintained by the W3C.

*[HTML]: HyperText Markup Language
*[W3C]: World Wide Web Consortium
*[API]: Application Programming Interface

This document uses UTF-8 encoding and follows ISO standards.

*[UTF-8]: 8-bit Unicode Transformation Format
*[ISO]: International Organization for Standardization

## Mathematical Equations

### Inline Math

The Pythagorean theorem is $a^2 + b^2 = c^2$.

Einstein's famous equation: $E = mc^2$.

The quadratic formula: $x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$.

### Display Math

$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$

Matrix notation:

$$
\begin{bmatrix}
a & b \\
c & d
\end{bmatrix}
\begin{bmatrix}
x \\
y
\end{bmatrix}
=
\begin{bmatrix}
ax + by \\
cx + dy
\end{bmatrix}
$$

Greek letters and symbols:

$$
\alpha + \beta = \gamma \quad \sum_{i=1}^{n} i = \frac{n(n+1)}{2}
$$

## Callouts / Admonitions

> **Note:**  
> This is an informational note using blockquote syntax.
> Use notes for additional context or clarification.

> **Warning:**  
> This is a warning message about potential issues.
> Warnings alert users to common mistakes or risks.

> **Tip:**  
> This is a helpful tip or best practice.
> Tips provide guidance for optimal usage.

> **Important:**  
> Critical information that users must read.
> Use for essential details that affect functionality.

## Extended Code Features

### Code with Line Numbers

```python {.numberLines startFrom="10"}
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

result = calculate_fibonacci(10)
print(f"Fibonacci(10) = {result}")
```

### Code with Highlighting

```javascript {highlight=[2,5-7]}
function processData(data) {
    const filtered = data.filter(item => item.active);  // highlighted
    const sorted = filtered.sort((a, b) => a.value - b.value);
    
    return sorted.map(item => ({  // start highlight
        id: item.id,
        value: item.value * 2
    }));  // end highlight
}
```

### Code with Filename

```python title="example.py"
# example.py
def greet(name):
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("World"))
```

## Tables with Alignment

### Complex Table

| Feature | Basic | Professional | Enterprise |
|:--------|:-----:|:------------:|-----------:|
| Users   | 5     | 50           | Unlimited  |
| Storage | 10GB  | 100GB        | 1TB        |
| Support | Email | Priority     | 24/7       |
| Price   | Free  | £50/month    | £200/month |

### Table with Formatting

| Code | Output | Description |
|------|--------|-------------|
| `**bold**` | **bold** | Bold text |
| `*italic*` | *italic* | Italic text |
| `~~strike~~` | ~~strike~~ | Strikethrough |
| `==mark==` | ==mark== | Highlighted |
| `H~2~O` | H~2~O | Subscript |
| `X^2^` | X^2^ | Superscript |

## Keyboard Keys

Press <kbd>Ctrl</kbd> + <kbd>C</kbd> to copy.

Use <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> to open the command palette.

Save with <kbd>Ctrl</kbd> + <kbd>S</kbd> (Windows/Linux) or <kbd>⌘</kbd> + <kbd>S</kbd> (macOS).

## HTML Entities and Special Characters

### Arrows and Symbols

← → ↑ ↓ ↔ ↕ ⇐ ⇒ ⇔

✓ ✗ ☐ ☑ ☒

★ ☆ ♠ ♣ ♥ ♦

### Mathematical Symbols

± × ÷ ≠ ≈ ≤ ≥ ∞ ∑ ∏ ∫ √ ∂

### Currency and Units

£ € $ ¥ ¢ ° º ª

### Typography

– — … ' ' " " « » ‹ ›

© ® ™ § ¶

## Details / Accordion

<details>
<summary>Click to expand: Installation instructions</summary>

To install the software:

1. Download the latest release
2. Extract the archive
3. Run the installer
4. Follow the setup wizard

```bash
wget https://example.com/software.tar.gz
tar -xzf software.tar.gz
cd software/
./install.sh
```

</details>

<details>
<summary>Troubleshooting common issues</summary>

### Issue 1: Installation fails

**Solution:** Ensure you have administrator privileges.

### Issue 2: Font rendering problems

**Solution:** Update your font cache with `fc-cache -fv`.

</details>

## Horizontal Rules with Different Styles

---

***

___

<!-- Each creates a horizontal rule -->

## Escaped Characters

Use backslash to escape special characters:

\*Not italic\* \**Not bold\** \`Not code\`

\# Not a heading

\[Not a link\](url)

## Line Breaks and Spacing

Regular line break  
using two spaces at the end.

Hard break with backslash\
works the same way.

Use `<br>` for explicit breaks:<br>Like this.

## Comments

<!-- This is a comment and won't appear in the output -->

<!--
Multi-line comments
can span multiple lines
and are useful for notes
-->

## Emojis with Shortcodes

:smile: :heart: :thumbsup: :rocket: :tada:

:warning: :information_source: :question: :exclamation:

:checkmark: :x: :heavy_check_mark: :cross_mark:

## Links with References

This is a [reference link][1] and another [reference link][ref].

[1]: https://example.com "Example Site"
[ref]: https://github.com "GitHub"

Auto-detection: https://example.com becomes a link.

Email: <user@example.com>

## Combined Advanced Features

Here's a complete example combining multiple features:

> **Important:** Data Processing Pipeline  
> The new pipeline processes ==1 million records/second==.[^perf]
>
> Key improvements:
> - [x] Reduced latency by 50%
> - [x] Increased throughput: ~~10k~~ → **1M** ops/sec
> - [ ] Add real-time monitoring
>
> Performance formula: $T = \frac{N}{R \times E}$ where:
> - T = Total time
> - N = Number of records  
> - R = Records per second
> - E = Efficiency factor (0.8-0.95)
>
> Press <kbd>Ctrl</kbd> + <kbd>R</kbd> to run.

[^perf]: Measured on test environment: Intel Xeon E5-2699 v4, 128GB RAM, NVMe SSD storage. Actual performance may vary.

---

*This page demonstrates the full range of extended Markdown syntax supported by modern documentation systems.*
