---
geometry:
- paperwidth=210mm
- paperheight=297mm
- left=15mm
- right=15mm
- top=15mm
- bottom=15mm
header-includes:
- \usepackage{calc}
- \usepackage{enumitem}
- \setlistdepth{20}
- \usepackage{longtable}
- \usepackage{ltablex}
- \usepackage{booktabs}
- \usepackage{array}
- \keepXColumns
- \setlength\LTleft{0pt}
- \setlength\LTright{0pt}
---

<a id="md-readme"></a>

# Documentation Framework

This documentation demonstrates a complete publishing workflow from Markdown source files to professional PDF output.

## Overview

The framework supports:

- **Multi-language content**: Parallel English and German versions
- **Structured navigation**: Hierarchical table of contents with PDF bookmarks
- **Rich formatting**: Tables, code blocks, lists, and images
- **Unicode support**: Extensive language and emoji coverage
- **Metadata management**: YAML frontmatter for document properties

## Document structure

The documentation is organised into:

- **Chapters**: Main content sections
- **Examples**: Demonstration files for various features
- **Appendices**: Supplementary reference material

## Technical features

This framework showcases:

- Reproducible PDF generation
- Font management and fallback chains
- Image asset handling (raster and vector)
- Cross-reference management
- Automated list generation (tables, figures, abbreviations)


\newpage

---
title: Home
description: Overview for the neutral sample book
date: 2024-06-01
version: 1.0
doc_type: cover
authors:
  - SAMPLE Team
---
<a id="md-index"></a>


# Home

![SAMPLE Logo](.gitbook/assets/SAMPLE_Logo_simple.png)

Welcome to this technical documentation framework demonstration.

## About this document

This publication showcases capabilities of modern documentation systems:

- **Multilingual support**: Parallel English and German versions
- **Rich formatting**: Tables, figures, code blocks, and lists
- **Unicode excellence**: 100+ languages, emoji, and complex scripts
- **Professional output**: High-quality PDF generation with proper typography

## Document structure

The content is organized into:

### Core chapters

Main content demonstrating various documentation patterns and structures.

### Examples

Practical demonstrations of:

- Emoji rendering across categories
- Image formats (raster and vector)
- Language samples and scripts

### Appendices

Supplementary material including:

- Technical specifications
- Font coverage analysis
- Reference materials

## Navigation

Use the table of contents (sidebar or PDF bookmarks) to navigate between sections. Each chapter includes:

- Clear heading hierarchy
- Cross-references where relevant
- Practical examples

## Technical foundation

Built with:

- **Markdown**: Source content format
- **YAML frontmatter**: Structured metadata
- **Python pipeline**: Automated build and validation
- **LaTeX/XeLaTeX**: Professional PDF typesetting


\newpage

---
title: Dedication
doc_type: dedication
order: 5
---
<a id="md-dedication"></a>


# Dedication

To all contributors to the open-source community who generously share their knowledge, code, and time.

To the pioneers of digital typography who made beautiful, accessible documents possible for everyone.

To the readers who seek understanding through well-crafted documentation.


\newpage

---
title: Preface
date: 2024-06-01
version: 1.0
doc_type: preface
---
<a id="md-preface"></a>


# Preface

Documentation is the bridge between knowledge and understanding. Well-structured documentation empowers readers to grasp complex concepts, reference critical information, and apply learned principles effectively.

## About this documentation

This document serves multiple purposes:

1. **Demonstration**: Showcasing a complete documentation workflow
2. **Reference**: Providing examples of various documentation patterns
3. **Testing**: Validating the publishing pipeline across different scenarios

## Target audience

This documentation is designed for:

- Technical writers seeking workflow examples
- Developers implementing documentation systems
- Content creators exploring publishing options
- Anyone interested in structured document creation

## How to use this documentation

Readers can approach this document in different ways:

- **Sequential reading**: Follow the chapters in order for a comprehensive understanding
- **Reference use**: Navigate directly to specific sections using the table of contents
- **Example study**: Examine the examples section for practical demonstrations

## Acknowledgements

This documentation framework builds upon established best practices from the technical writing community and leverages modern open-source tools for document processing and PDF generation.


\newpage

---
title: Chapter 1 – Observable patterns
date: 2024-06-01
version: 1.0
doc_type: chapter
chapter_number: 1
---
<a id="md-chapters-chapter-01"></a>


# Chapter 1 – Observable patterns

In software development, we repeatedly encounter similar problems for which proven solutions have been established over time. These recurring structures are referred to as design patterns.

## Historical development

The systematic documentation of design patterns began in the 1990s. Inspired by architecture, where Christopher Alexander described patterns for building construction, software developers transferred this idea to programming.

### Early pioneers

The so-called "Gang of Four" (Gamma, Helm, Johnson, Vlissides) published the seminal work "Design Patterns" in 1994, which categorised and described 23 patterns.

### Modern developments

Today, hundreds of documented patterns exist for a wide variety of application areas – from microservices and reactive programming to cloud architectures.

## Categories of patterns

Design patterns can be divided into three main categories:

### Creational patterns

These patterns deal with object creation and attempt to make object instantiation more flexible:

- **Singleton**: Ensures that only one instance of a class exists
- **Factory**: Encapsulates object creation
- **Builder**: Separates the construction of complex objects from their representation

### Structural patterns

Structural patterns describe how classes and objects can be composed into larger structures:

- **Adapter**: Enables collaboration between incompatible interfaces
- **Composite**: Forms tree structures to represent part-whole hierarchies
- **Decorator**: Dynamically extends objects with additional functionality

### Behavioural patterns

These patterns address the interaction between objects and the distribution of responsibilities:

- **Observer**: Defines a dependency between objects so that changes are automatically propagated
- **Strategy**: Encapsulates interchangeable algorithms
- **Command**: Encapsulates requests as objects

## Advantages of using patterns

Using established design patterns offers several advantages:

1. **Common language**: Teams can communicate complex concepts precisely
2. **Proven solutions**: Patterns have been proven in practice and are well documented
3. **Maintainability**: Code becomes more structured and easier to understand
4. **Flexibility**: Changes can often be implemented with less effort

## Limitations and challenges

Despite their advantages, design patterns are not a panacea:

- **Over-engineering**: Not every problem requires a complex pattern
- **Learning curve**: Understanding and correct application require experience
- **Context dependency**: A pattern must fit the specific situation

## Practical application

When deciding on a design pattern, the following questions should be asked:

1. What problem needs to be solved?
2. Is there an established pattern for this problem?
3. Does the complexity of the pattern justify the expected benefit?
4. Does the pattern fit with the existing architecture?

## Summary

Design patterns are a valuable tool in software development. They provide tested solutions for recurring problems and promote a common technical language. However, their sensible application requires experience and judgement to avoid falling into the trap of over-engineering.


\newpage

---
title: Chapter 2 – Comparative tables
date: 2024-06-01
version: 1.0
doc_type: chapter
chapter_number: 2
---
<a id="md-chapters-chapter-02"></a>


# Chapter 2 – Comparative tables

Tables are an indispensable tool for the structured presentation of information. They enable direct comparison of different options, technologies, or concepts at a glance.

## Fundamentals of tabular presentation

A well-designed table follows clear principles:

### Structure and organisation

| Element | Description | Purpose |
|---------|-------------|---------|
| Header row | Contains column labels | Orientation for the reader |
| Data rows | Contain the actual information | Comparable presentation |
| Summary | Optional: sums or averages | Aggregated insights |

### Design principles

Effective tables are characterised by the following features:

1. **Clarity**: Unambiguous column and row labels
2. **Consistency**: Uniform formatting within columns
3. **Readability**: Appropriate line spacing and font sizes
4. **Relevance**: Display only necessary information

## Comparison of programming paradigms

A practical example of using comparison tables is the juxtaposition of different programming paradigms:

| Paradigm | Main features | Typical languages | Application areas |
|-----------|---------------|-------------------|-------------------|
| Imperative | Step-by-step instructions | C, Pascal, BASIC | Systems programming |
| Object-oriented | Classes and objects | Java, C++, Python | Enterprise applications |
| Functional | Immutable data | Haskell, Erlang, F\# | Data processing |
| Declarative | What instead of How | SQL, HTML, Prolog | Database queries |

### Detailed consideration

Each paradigm has its strengths and weaknesses:

**Imperative programming**
- Direct control over flow
- Efficient at hardware level
- Can become confusing with complexity

**Object-oriented programming**
- Modular structure
- Reusability through inheritance
- Can lead to overhead

**Functional programming**
- No side effects
- Easy to test
- Learning curve for switchers

## Technology comparisons

Comparison tables are particularly suitable for technology decisions:

### Web framework comparison

| Framework | Language | Performance | Learning curve | Community |
|-----------|---------|-------------|----------------|-----------|
| Django | Python | Medium | Medium | Very large |
| Flask | Python | High | Low | Large |
| Spring | Java | Medium | High | Very large |
| Express | JavaScript | High | Low | Very large |
| Rails | Ruby | Medium | Medium | Large |

### Evaluation criteria

Various factors play a role in technology selection:

1. **Performance**: Throughput and response times
2. **Developer productivity**: Speed of development
3. **Maintainability**: Long-term maintenance effort
4. **Scalability**: Growth potential
5. **Ecosystem**: Available libraries and tools

## Database comparison

Another common application area is database comparisons:

| Type | Example | Consistency | Scaling | Use case |
|-----|----------|------------|---------|-----------|
| Relational | PostgreSQL | ACID | Vertical | Transactions |
| Document | MongoDB | Eventual | Horizontal | Flexible schemas |
| Key-value | Redis | Eventual | Horizontal | Caching |
| Graph | Neo4j | ACID | Vertical | Relationships |
| Column | Cassandra | Eventual | Horizontal | Time series |

### CAP theorem

For distributed databases, the CAP theorem is relevant:

- **C**onsistency: All nodes see the same data
- **A**vailability: System always responds
- **P**artition tolerance: System functions despite network failures

According to the CAP theorem, only two of the three properties can be guaranteed simultaneously.

## Best practices for tables

When creating comparison tables, the following points should be considered:

### Content aspects

- Select relevant comparison criteria
- Use objective and verifiable data
- Cite sources where necessary
- Ensure data is current

### Visual design

- Zebra pattern for better readability in long tables
- Highlighting of important rows or columns
- Responsive design for different screen sizes
- Sorting and filtering options for interactive tables

## Summary

Comparison tables are a powerful tool for the structured presentation of complex information. They enable quick comparisons and informed decisions. The key to success lies in carefully selecting relevant criteria and presenting them clearly and consistently.


\newpage

---
doc_type: epilog
title: Epilogue
version: 1.0.0
---
<a id="md-epilogue"></a>


# Epilogue

Documentation is a living artefact. As technologies evolve and understanding deepens, good documentation grows and adapts to serve its readers better.

## The documentation journey

Creating effective documentation is an iterative process:

1. **Initial creation**: Capturing knowledge whilst it's fresh
2. **Review and refinement**: Improving clarity and accuracy
3. **User feedback**: Learning from readers' experiences
4. **Continuous improvement**: Evolving with changing needs

## Looking forward

The principles demonstrated in this documentation – clear structure, comprehensive examples, and attention to technical detail – remain relevant regardless of the specific tools or technologies employed.

## Final thoughts

Good documentation respects the reader's time and intelligence. It provides clear paths to understanding whilst remaining accessible to those encountering the material for the first time.

May your own documentation efforts be similarly rewarding, both in their creation and in the value they provide to your readers.


\newpage

---
title: Citation & Footnote Examples
date: 2026-01-11
version: 1.0
doc_type: example
category: documentation-features
---
<a id="md-examples-citation-examples"></a>


# Citation & Footnote Examples

This page demonstrates various citation styles and footnote usage in Markdown documents.

## Footnotes

Markdown supports footnotes[^1] that appear at the bottom of the page. You can reference the same footnote multiple times[^1].

Here's a longer footnote with multiple paragraphs[^longnote].

Inline footnotes are also possible.^[This is an inline footnote.]

### Named vs Numbered Footnotes

You can use descriptive names for footnotes[^bignote] or just numbers[^2].

## Citation Styles

### APA Style (7th Edition)

**Books:**

Smith, J. A., & Johnson, M. B. (2023). *Research Methods in Documentation*. Academic Press.

**Journal Articles:**

Brown, L. K., Davis, R. T., & Wilson, S. E. (2024). Advanced typesetting techniques for multilingual documents. *Journal of Technical Communication*, 45(3), 234-256. https://doi.org/10.1234/jtc.2024.01

**Online Sources:**

Unicode Consortium. (2023, September 12). *Unicode Standard 15.1.0*. https://www.unicode.org/versions/Unicode15.1.0/

### IEEE Style

**Journal Article:**

[1] L. K. Brown, R. T. Davis, and S. E. Wilson, "Advanced typesetting techniques for multilingual documents," *J. Tech. Commun.*, vol. 45, no. 3, pp. 234-256, 2024, doi: 10.1234/jtc.2024.01.

**Conference Paper:**

[2] J. A. Smith and M. B. Johnson, "Automated documentation pipelines," in *Proc. Int. Conf. Software Engineering*, London, UK, 2023, pp. 123-130.

**Book:**

[3] A. Martinez, *Modern Documentation Frameworks*, 2nd ed. Boston, MA, USA: Tech Publishers, 2024.

### Chicago Style (Author-Date)

**Books:**

Martinez, Ana. 2024. *Modern Documentation Frameworks*. 2nd ed. Boston: Tech Publishers.

**Journal Articles:**

Brown, Laura K., Robert T. Davis, and Sarah E. Wilson. 2024. "Advanced Typesetting Techniques for Multilingual Documents." *Journal of Technical Communication* 45 (3): 234-256. https://doi.org/10.1234/jtc.2024.01.

### Zenodo Standard (DOI-based)

Zenodo provides persistent identifiers (DOIs) for research data and publications[^zenodo].

**Dataset:**

Smith, John A.; Johnson, Mary B. (2023). Sample Documentation Dataset (Version 1.2) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.1234567

**Software:**

Brown, Laura K.; Davis, Robert T. (2024). GitBook Worker: Automated Documentation Pipeline (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.7654321

**Publication:**

Martinez, Ana; Wilson, Sarah E.; Thompson, James R. (2023). Best Practices for Technical Documentation. *Zenodo Preprints*. https://doi.org/10.5281/zenodo.8901234

### BibTeX Format

For LaTeX/academic documents:

```bibtex
@article{brown2024advanced,
  title={Advanced Typesetting Techniques for Multilingual Documents},
  author={Brown, Laura K and Davis, Robert T and Wilson, Sarah E},
  journal={Journal of Technical Communication},
  volume={45},
  number={3},
  pages={234--256},
  year={2024},
  doi={10.1234/jtc.2024.01}
}

@software{brown2024gitbook,
  author={Brown, Laura K and Davis, Robert T},
  title={GitBook Worker: Automated Documentation Pipeline},
  version={1.0.0},
  year={2024},
  publisher={Zenodo},
  doi={10.5281/zenodo.7654321},
  url={https://doi.org/10.5281/zenodo.7654321}
}

@dataset{smith2023sample,
  author={Smith, John A and Johnson, Mary B},
  title={Sample Documentation Dataset},
  version={1.2},
  year={2023},
  publisher={Zenodo},
  doi={10.5281/zenodo.1234567}
}
```

## In-Text Citations

### Narrative Citations

As Smith and Johnson (2023) demonstrated, automated documentation pipelines significantly reduce manual effort.

Brown et al. (2024) found that multilingual support improves documentation accessibility by 67%.

### Parenthetical Citations

Recent research shows improved documentation quality with automation (Smith & Johnson, 2023; Brown et al., 2024).

Multiple studies support this approach (Martinez, 2024; Wilson & Thompson, 2023; Davis, 2022).

## Citation with Footnotes Combined

According to recent research[^research], automated documentation systems show promise[^3]. The study by Brown et al. (2024) provides empirical evidence for these claims[^4].

## Licence Attribution (Zenodo/CC Standard)

**Font Attribution:**

Twemoji Mozilla (2023). Twitter Emoji (Twemoji) COLRv1 Font. Licensed under CC BY 4.0. Available at: https://github.com/mozilla/twemoji-colr. DOI: 10.5281/zenodo.3234567 (example DOI).

**Data Attribution:**

This document uses language samples from the Unicode Common Locale Data Repository (CLDR), licensed under Unicode License Agreement. Unicode Consortium (2023). https://www.unicode.org/copyright.html

## Cross-References

See [Chapter 1](#md-chapters-chapter-01) for more on design patterns.

For emoji rendering details, refer to [Appendix B](#md-appendices-emoji-font-coverage).

---

[^1]: This is a simple footnote with a reference back to the text.

[^2]: Footnotes can be numbered sequentially.

[^longnote]: This is a longer footnote with multiple paragraphs.

    You can include additional paragraphs by indenting them.
    
    Even code blocks can appear in footnotes:
    
    ```python
    def example():
        return "footnote code"
    ```

[^bignote]: Descriptive names make footnotes easier to manage in large documents.

    They're especially useful when you need to reorganise content.

[^zenodo]: Zenodo is an open-access repository operated by CERN, providing DOIs for research outputs including data, software, publications, and more. See https://zenodo.org for details.

[^research]: Martinez, A. (2024). *Modern Documentation Frameworks*, pp. 45-67.

[^3]: Specifically, build automation and validation pipelines reduce errors by approximately 80% (Smith & Johnson, 2023).

[^4]: The study included 150 documentation projects across 12 organisations over a 2-year period.


\newpage

---
title: Emoji examples – Activities & travel
description: Common sport, leisure and transport emojis for functional and rendering tests.
date: 2024-06-05
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2024-06-05
    changes: Initial version for activity and transport groups.
---
<a id="md-examples-emoji-activities-and-travel"></a>


# Emoji examples – Activities & travel

This page tests emojis for sports, hobbies, vehicles, and travel.

## Special features

Emojis in this category contain:

- **People in action**: Athletes with skin tone and gender variants
- **Vehicles**: Cars, aeroplanes, ships in various variants
- **Buildings**: Different architectural styles
- **Symbols**: Traffic signs, warning symbols

## Emoji test

### Sample set

This page contains a broad emoji set for rendering/font/bookmark tests.

#### Travel & navigation

🧭 🗺️ 📍 📌 🧳 🎒 🧷 🧾 🕒 ⏱️ ⏳

#### Vehicles

🚗 🚕 🚙 🚌 🚎 🚐 🚑 🚒 🚓 🚚 🚛 🚜 🛻 🚲 🛴 🛵 🏍️
🚂 🚆 🚇 🚊 🚉 🚝 🚄
✈️ 🛫 🛬 🛩️ 🚁 🚀 🛰️
⛵ 🛶 🚤 🛳️ ⛴️ ⚓

#### Places

🏁 🗿 🗽 🗼 🏰 🏯 🏟️ 🏖️ 🏜️ 🏕️ 🏔️ 🏙️ 🌉 🌆 🛣️ 🛤️

#### Activities & sports

⚽ 🏀 🏈 ⚾ 🥎 🎾 🏐 🏉 🎱 🏓 🏸 🥊 🥋 🏹 🎣 🤿
🏃‍♀️ 🏃‍♂️ 🚴‍♀️ 🚴‍♂️ 🏊‍♀️ 🏊‍♂️ 🧗‍♀️ 🧗‍♂️ ⛷️ 🏂 🏄‍♀️ 🏄‍♂️

#### Weather (as travel context)

☀️ 🌤️ ⛅ 🌥️ ☁️ 🌦️ 🌧️ ⛈️ 🌩️ ❄️ 🌨️ 💨 🌫️


\newpage

---
title: Emoji examples – Nature & food
description: Collection of common nature, animal and food emojis for layout tests.
date: 2024-06-05
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2024-06-05
    changes: First release for nature and nutrition groups.
---
<a id="md-examples-emoji-nature-and-food"></a>


# Emoji examples – Nature & food

This page tests emojis from the categories of animals, plants, and food.

## Test scope

Emojis in this category are usually simpler than people emojis:

- **No skin tone modifiers**: Uniform display
- **Few ZWJ sequences**: Mostly single Unicode characters
- **High compatibility**: Well supported in all fonts
- **Colour and detail**: Test for colour emoji rendering

## Emoji test

### Sample set

This page contains a broad emoji set for rendering/font/bookmark tests.

#### Plants & nature

🌱 🌿 🍀 🍃 🌾 🌵 🌳 🌲 🌴 🍁 🍂 🍄 🌸 🌼 🌻 🌺 🌷 🪴

#### Animals (selection)

🐶 🐱 🐭 🐹 🐰 🦊 🐻 🐼 🐨 🐯 🦁 🐮 🐷 🐸 🐵 🐔 🐧 🐦 🦉 🦇
🐺 🐗 🐴 🦄 🐝 🦋 🐞 🪲 🐢 🐍 🦎 🐙 🦀 🦐 🐟 🐠 🐡 🦈 🐳 🐬

#### Weather & elements

🌈 🌙 ⭐ 🌟 ☀️ 🌧️ ❄️ 🌪️ 🌊 💧 🔥

#### Food (neutral, broad)

🍞 🥖 🥨 🧀 🥚 🥗 🥦 🥑 🍅 🥕 🌽 🥔 🍄
🍎 🍐 🍊 🍋 🍌 🍉 🍇 🍓 🫐 🍒 🥝

#### Drinks

☕ 🍵 🧃 🥛 🧊


\newpage

---
title: Emoji examples – Objects, symbols & flags
description: Reference lists for tools, technology, symbols and flags with full emoji coverage.
date: 2024-06-05
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2024-06-05
    changes: Newly created page for objects, symbols and flags.
---
<a id="md-examples-emoji-objects-symbols-flags"></a>


# Emoji examples – Objects, symbols & flags

This page tests emojis for objects, symbols, and country flags.

## Technical challenges

### Flag emojis

Country flags are particularly complex:

- **Regional Indicator Symbols**: Two letter characters form a flag
- **ISO 3166-1**: Based on country codes (e.g. DE = 🇩🇪)
- **Font dependency**: Not all systems display all flags
- **Fallback**: Letters are displayed when support is missing

### Symbol emojis

Symbols include:

- **Mathematical symbols**: ➕ ➖ ➗ × ÷
- **Geometric shapes**: ■ ● ▲ ⭐
- **Pictograms**: ♿ ⚠️ ☢️ ☣️
- **Keycaps**: 0️⃣ 1️⃣ 2️⃣ #️⃣

## Emoji test

### Sample set

This page contains a broad emoji set for rendering/font/bookmark tests.

#### Tech & tools

💻 🖥️ ⌨️ 🖱️ 🖨️ 📱 📷 🎥 🎛️ 🎚️ 🔋 🔌 💾 💿 📀
⚙️ 🔧 🔩 🛠️ ⛏️ 🔨 🪛 🪚 🧰 🧲
🔬 🧪 🧬 📡 🛰️ 🧯

#### Symbols & UI

✅ ☑️ ❌ ⚠️ ℹ️ 🔔 🔕 🔒 🔓 🔑 🗝️ ♻️ 🧾 🏷️
➕ ➖ ✖️ ➗ 🟰
⬆️ ⬇️ ⬅️ ➡️ ↗️ ↘️ ↙️ ↖️
0️⃣ 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣ 9️⃣ 🔟 #️⃣ *️⃣

#### Documents & organization

📄 📃 📑 🧷 📌 📍 🗂️ 📁 📂 🗃️ 🗄️ 🧮 📊 📈 📉

#### Flags (selection)

🇩🇪 🇦🇹 🇨🇭 🇪🇺 🇬🇧 🇺🇸 🇨🇦 🇧🇷 🇯🇵 🇰🇷 🇮🇳 🇦🇺 🇿🇦 🇺🇳


\newpage

---
title: Emoji examples – Smileys & people
description: Overview of classic face and person emojis for test coverage.
date: 2024-06-05
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2024-06-05
    changes: First collection for faces, gestures and role profiles.
---
<a id="md-examples-emoji-smileys-and-people"></a>


# Emoji examples – Smileys & people

This page tests the display of facial emojis, gestures, and people with various skin tones.

## Why these tests are important

Emojis representing people are particularly complex:

- **Skin tone modifiers**: Five different skin tones (U+1F3FB to U+1F3FF)
- **ZWJ sequences**: Complex emoji composed of multiple Unicode characters
- **Gender variants**: Male, female, and neutral forms
- **Font fallbacks**: Switching between text and emoji fonts

## Emoji test

### Sample set

This page contains a broad emoji set for rendering/font/bookmark tests.

#### Faces (selection)

😀 😃 😄 😁 😆 😊 🙂 😉 😌 😇 🤔 😐 🙄 😎 🥳 🤓 😴

#### Hands & gestures (with skin tones)

👍 👍🏻 👍🏼 👍🏽 👍🏾 👍🏿
👋 👋🏻 👋🏼 👋🏽 👋🏾 👋🏿
🙌 🙌🏻 🙌🏼 🙌🏽 🙌🏾 🙌🏿
👏 👏🏻 👏🏼 👏🏽 👏🏾 👏🏿

#### People & roles (ZWJ/sequences)

🧑‍💻 👩‍💻 👨‍💻
🧑‍🔬 👩‍🔬 👨‍🔬
🧑‍🚀 👩‍🚀 👨‍🚀
🧑‍🍳 👩‍🍳 👨‍🍳
🧑‍🏫 👩‍🏫 👨‍🏫

#### Families & relationships (ZWJ)

👨‍👩‍👧‍👦 👩‍👩‍👧 👨‍👨‍👦 👩‍👦


\newpage

---
title: Examples
date: 2024-06-05
version: 1.0
doc_type: example
---
<a id="md-examples-readme"></a>


# Examples

This section contains various example documents that demonstrate different aspects of document creation and formatting.

## Overview of example categories

### Emoji tests

The emoji example files test the correct display of Unicode emoji in various contexts:

- **Emoji-Headings**: Emojis in headings and TOC bookmarks
- **Smileys and People**: Faces, people, gestures
- **Nature and Food**: Animals, plants, food
- **Activities and Travel**: Sports, travel, transport
- **Objects and Symbols**: Objects, symbols, flags

### Image tests

The image examples demonstrate various aspects of image integration:

- **Assets and Layout**: Basic image integration (PNG, SVG)
- **Captions and Density**: Image captions and dense image sequences

### Language tests

The language samples file contains examples in over 100 languages to verify:

- Fonts and character set coverage
- Text direction (LTR, RTL)
- Hyphenation and line breaking
- PDF bookmark encoding

## Purpose of the examples

These example files serve as:

1. **Regression tests** for the publishing pipeline
2. **Reference implementations** for document formats
3. **Quality assurance** for font and layout rendering
4. **Documentation** of supported features


\newpage

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
<a id="md-examples-image-assets-and-layout"></a>


# Image examples – Assets & layout

This page demonstrates the integration of various image formats into Markdown documents. All assets used are located in the `content/.gitbook/assets/` directory and are legally safe.

## Image formats compared

### Raster images (PNG)

Raster images are suitable for:
- Photographs and complex graphics
- Images with many colour gradients
- Screenshots and screen captures

**Disadvantage**: Enlargement can lead to quality loss.

![SAMPLE Logo (PNG)](.gitbook/assets/SAMPLE_Logo_simple.png){fig-alt="SAMPLE Logo"}

### Vector images (SVG)

Vector images offer:
- Arbitrary scalability without quality loss
- Small file sizes for simple graphics
- Sharp display on all screen resolutions

**Ideal for**: Diagrams, icons, technical drawings

![Neutral grid (SVG)](.gitbook/assets/neutral-grid.pdf)

### Diagrams and workflows

Structured representations such as flowcharts particularly benefit from vector graphics:

![Neutral workflow (SVG)](.gitbook/assets/neutral-flow.pdf)

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


\newpage

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
<a id="md-examples-image-captions-and-density"></a>


# Image examples – Captions & density

This test page checks the behaviour with multiple images in quick succession. Particularly relevant for:

- **Page breaks**: How does the layout behave with many images?
- **Image captions**: Are captions positioned correctly?
- **Spacing**: Sufficient space between images?
- **Numbering**: Sequential image numbers in lists of figures?

## Gallery (SVG)

Multiple similar images in sequence test the layout:

![Neutral shapes – A](.gitbook/assets/neutral-shapes.pdf)

_Figure 1: First instance of shape representation_

![Neutral shapes – B](.gitbook/assets/neutral-shapes.pdf)

_Figure 2: Second instance to check for repetitions_

## Mixed (SVG + PNG)

Combination of different image formats in one section:

![Neutral grid](.gitbook/assets/neutral-grid.pdf)

_Figure 3: Vector graphic with grid pattern_

![SAMPLE Logo](.gitbook/assets/SAMPLE_Logo_simple.png)

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


\newpage

---
title: Language Samples – 100 Languages
description: Neutral short and long sample sentences in many languages for font/rendering tests.
date: 2026-01-10
version: 1.2.0
doc_type: example
category: "language-test"
show_in_summary: true
history:
  - version: 1.2.0
    date: 2026-05-07
    description: Expanded CJK, Devanagari, and Ethiopic test blocks to at least 3000 script characters per language.
  - version: 1.1.2
    date: 2026-05-06
    description: Labeled Indic and Ethiopic long lines with flag, language code, and language name.
  - version: 1.1.1
    date: 2026-05-06
    description: Labeled CJK long lines with flag, language code, and language name.
  - version: 1.1.0
    date: 2026-05-06
    description: Added long ERDA font visual-inspection samples for CJK, Indic, and Ethiopic.
  - version: 1.0.0
---
<a id="md-examples-language-samples-100"></a>


# Language Samples – 100 Languages

This page contains short, neutral sample sentences in many languages.
It serves as a regression test for fonts, hyphenation, special characters, and PDF bookmarks.

## 🇩🇪 DE - Germany (Deutschland)
### Deutsch
In der Ruhe liegt die Kraft.

## 🇦🇹 AT - Austria (Österreich)
### Deutsch
In der Ruhe liegt die Kraft.

## 🇨🇭 CH - Switzerland (Schweiz)
### Deutsch
In der Ruhe liegt die Kraft.

### Français
Dans le calme réside la force.

### Italiano
Nella calma risiede la forza.

### Rumantsch
En la quietezza è forza.

## 🇬🇧 GB - United Kingdom (United Kingdom)
### English
In calm lies strength.

## 🇺🇸 US - United States (United States)
### English
In calm lies strength.

## 🇪🇸 ES - Spain (España)
### Español
En la calma está la fuerza.

### Català
En la calma hi ha força.

### Euskara
Lasaitasunean indarra dago.

### Galego
Na calma hai forza.

## 🇲🇽 MX - Mexico (México)
### Español
En la calma está la fuerza.

## 🇧🇷 BR - Brazil (Brasil)
### Português
Na calma está a força.

## 🇵🇹 PT - Portugal (Portugal)
### Português
Na calma está a força.

## 🇫🇷 FR - France (France)
### Français
Dans le calme réside la force.

## 🇮🇹 IT - Italy (Italia)
### Italiano
Nella calma risiede la forza.

## 🇳🇱 NL - Netherlands (Nederland)
### Nederlands
In de rust schuilt kracht.

## 🇧🇪 BE - Belgium (België / Belgique)
### Nederlands
In de rust schuilt kracht.
### Français
Dans le calme réside la force.
### Deutsch
In der Ruhe liegt die Kraft.

## 🇵🇱 PL - Poland (Polska)
### Polski
W spokoju tkwi siła.

## 🇨🇿 CZ - Czechia (Česko)
### Čeština
Ve klidu je síla.

## 🇸🇰 SK - Slovakia (Slovensko)
### Slovenčina
V pokoji je sila.

## 🇭🇺 HU - Hungary (Magyarország)
### Magyar
A nyugalomban rejlik az erő.

## 🇷🇴 RO - Romania (România)
### Română
În liniște stă puterea.

## 🇸🇪 SE - Sweden (Sverige)
### Svenska
I lugnet finns styrka.

## 🇳🇴 NO - Norway (Norge)
### Norsk
I roen ligger styrken.

## 🇩🇰 DK - Denmark (Danmark)
### Dansk
I roen ligger styrken.

## 🇫🇮 FI - Finland (Suomi)
### Suomi
Rauhallisuudessa on voimaa.

## 🇪🇪 EE - Estonia (Eesti)
### Eesti
Rahus peitub jõud.

## 🇱🇻 LV - Latvia (Latvija)
### Latviešu
Mierā ir spēks.

## 🇱🇹 LT - Lithuania (Lietuva)
### Lietuvių
Ramybėje slypi jėga.

## 🇬🇷 GR - Greece (Ελλάδα)
### Ελληνικά
Στη γαλήνη βρίσκεται η δύναμη.

## 🇹🇷 TR - Turkey (Türkiye)
### Türkçe
Sakinlikte güç vardır.

## 🇮🇱 IL - Israel (ישראל)
### עברית
בשקט יש כוח.

## 🇸🇦 SA - Saudi Arabia (المملكة العربية السعودية)
### العربية
في الهدوء تكمن القوة.

## 🇪🇬 EG - Egypt (مصر)
### العربية
في الهدوء تكمن القوة.

## 🇮🇷 IR - Iran (ایران)
### فارسی
در آرامش قدرت نهفته است.

## 🇦🇫 AF - Afghanistan (افغانستان)
### دری
در آرامش قدرت نهفته است.

## 🇵🇰 PK - Pakistan (پاکستان)
### اردو
سکون میں طاقت ہے۔

## 🇧🇩 BD - Bangladesh (বাংলাদেশ)
### বাংলা
শান্তিতে শক্তি আছে।

## 🇮🇳 IN - India (भारत)
### हिन्दी
शांति में शक्ति है।

### বাংলা
শান্তিতে শক্তি আছে।

### తెలుగు
నిశ్శబ్దంలో బలం ఉంటుంది.

### मराठी
शांततेत शक्ती आहे.

### ગુજરાતી
શાંતિમાં શક્તિ છે.

### ಕನ್ನಡ
ಶಾಂತಿಯಲ್ಲಿ ಶಕ್ತಿ ಇದೆ.

### മലയാളം
ശാന്തിയിൽ ശക്തിയുണ്ട്.

### ଓଡ଼ିଆ
ଶାନ୍ତିରେ ଶକ୍ତି ଅଛି।

### ਪੰਜਾਬੀ
ਸ਼ਾਂਤੀ ਵਿੱਚ ਤਾਕਤ ਹੈ।

### অসমীয়া
শান্তিত শক্তি আছে।

## 🇱🇰 LK - Sri Lanka (ශ්‍රී ලංකාව)
### සිංහල
නිශ්ශබ්දතාවයේ ශක්තිය ඇත.
### தமிழ்
அமைதியில் வலிமை உள்ளது.

## 🇳🇵 NP - Nepal (नेपाल)
### नेपाली
शान्तिमा शक्ति छ।

## 🇹🇭 TH - Thailand (ประเทศไทย)
### ไทย
ความสงบมีพลัง

## 🇱🇦 LA - Laos (ລາວ)
### ລາວ
ຄວາມສະຫງົບມີພະລັງງານ

## 🇰🇭 KH - Cambodia (កម្ពុជា)
### ខ្មែរ
ក្នុងភាពស្ងប់ស្ងាត់មានកម្លាំង។

## 🇻🇳 VN - Vietnam (Việt Nam)
### Tiếng Việt
Trong bình yên có sức mạnh.

## 🇮🇩 ID - Indonesia (Indonesia)
### Bahasa Indonesia
Dalam ketenangan ada kekuatan.

## 🇲🇾 MY - Malaysia (Malaysia)
### Bahasa Melayu
Dalam ketenangan ada kekuatan.

## 🇵🇭 PH - Philippines (Pilipinas)
### Tagalog
Sa katahimikan may lakas.

## 🇨🇳 CN - China (中国)
### 中文（简体）
宁静中有力量。

## 🇹🇼 TW - Taiwan (臺灣)
### 中文（繁體）
寧靜中有力量。

## 🇯🇵 JP - Japan (日本)
### 日本語
静けさの中に力がある。

## 🇰🇷 KR - South Korea (대한민국)
### 한국어
고요함 속에 힘이 있다.

## 🇲🇳 MN - Mongolia (Монгол Улс)
### Монгол хэл
Тайван байдалд хүч бий.

## 🇬🇪 GE - Georgia (საქართველო)
### ქართული
სიმშვიდეში ძალაა.

## 🇦🇲 AM - Armenia (Հայաստան)
### Հայերեն
Խաղաղության մեջ ուժ կա։

## 🇦🇿 AZ - Azerbaijan (Azərbaycan)
### Azərbaycan dili
Sakitlikdə güc var.

## 🇺🇿 UZ - Uzbekistan (Oʻzbekiston)
### Oʻzbek
Sokinlikda kuch bor.

## 🇹🇲 TM - Turkmenistan (Türkmenistan)
### Türkmen
Asudalykda güýç bar.

## 🇰🇬 KG - Kyrgyzstan (Кыргызстан)
### Кыргызча
Тынчтыкта күч бар.

## 🇹🇯 TJ - Tajikistan (Тоҷикистон)
### тоҷикӣ
Дар оромӣ қувват ҳаст.

## 🇰🇿 KZ - Kazakhstan (Қазақстан)
### Қазақша
Тыныштықта күш бар.

### Qazaq (Latin)
Tynyqtyqta küş bar.

## 🇺🇦 UA - Ukraine (Україна)
### Українська
У спокої є сила.

## 🇧🇬 BG - Bulgaria (България)
### Български
В спокойствието има сила.

## 🇷🇸 RS - Serbia (Србија)
### Српски
У миру је снага.

## 🇭🇷 HR - Croatia (Hrvatska)
### Hrvatski
U miru je snaga.

## 🇸🇮 SI - Slovenia (Slovenija)
### Slovenščina
V miru je moč.

## 🇦🇱 AL - Albania (Shqipëria)
### Shqip
Në qetësi ka forcë.

## 🇮🇸 IS - Iceland (Ísland)
### Íslenska
Í kyrrð er styrkur.

## 🇮🇪 IE - Ireland (Éire)
### Gaeilge
Tá neart sa chiúnas.

## 🇲🇹 MT - Malta (Malta)
### Malti
Fil-kwiet hemm saħħa.

## 🇪🇹 ET - Ethiopia (ኢትዮጵያ)
### አማርኛ
በሰላም ውስጥ ኃይል አለ።

## 🇪🇷 ER - Eritrea (ኤርትራ)
### ትግርኛ
ብህልውነት ሓይሊ ኣለ።

## 🇸🇴 SO - Somalia (Soomaaliya)
### Soomaali
Degganaansho waxaa ku jira xoog.

## 🇰🇪 KE - Kenya (Kenya)
### Kiswahili
Katika utulivu kuna nguvu.

## 🇹🇿 TZ - Tanzania (Tanzania)
### Kiswahili
Katika utulivu kuna nguvu.

## 🇺🇬 UG - Uganda (Uganda)
### English
In calm lies strength.

## 🇳🇬 NG - Nigeria (Nigeria)
### Yoruba
Nínú ìdákẹ́jẹ̀ ni agbára wà.
### Igbo
N’udo dị ike.
### Hausa
A cikin natsuwa akwai ƙarfi.

## 🇬🇭 GH - Ghana (Ghana)
### English
In calm lies strength.

## 🇸🇳 SN - Senegal (Sénégal)
### Wolof
Ci dalal am na doole.

## 🇨🇲 CM - Cameroon (Cameroun)
### Français
Dans le calme réside la force.
### English
In calm lies strength.

## 🇨🇩 CD - DR Congo (République démocratique du Congo)
### Lingála
Na kimia, ezali na makasi.

## 🇦🇴 AO - Angola (Angola)
### Português
Na calma está a força.

## 🇲🇿 MZ - Mozambique (Moçambique)
### Português
Na calma está a força.

## 🇿🇦 ZA - South Africa (South Africa)
### English
In calm lies strength.
### Afrikaans
In kalmte lê krag.
### isiZulu
Ekuthuleni kukhona amandla.

## 🇲🇦 MA - Morocco (المغرب)
### العربية
في الهدوء تكمن القوة.
### Tamazight
Deg wazal tella tazmert.

## 🇩🇿 DZ - Algeria (الجزائر)
### العربية
في الهدوء تكمن القوة.

## 🇹🇳 TN - Tunisia (تونس)
### العربية
في الهدوء تكمن القوة.

## 🇯🇴 JO - Jordan (الأردن)
### العربية
في الهدوء تكمن القوة.

## 🇦🇪 AE - United Arab Emirates (الإمارات العربية المتحدة)
### العربية
في الهدوء تكمن القوة.

## 🇮🇶 IQ - Iraq (العراق)
### العربية
في الهدوء تكمن القوة.
### کوردی
لە ئارامییدا هێز هەیە.

## 🇬🇹 GT - Guatemala (Guatemala)
### Español
En la calma está la fuerza.

## 🇨🇱 CL - Chile (Chile)
### Español
En la calma está la fuerza.

## 🇵🇪 PE - Peru (Perú)
### Español
En la calma está la fuerza.
### Quechua
Ch’iniypi kallpa kan.

## 🇧🇴 BO - Bolivia (Bolivia)
### Español
En la calma está la fuerza.
### Aymara
Sumankañan ch’amawa.

## 🇵🇾 PY - Paraguay (Paraguay)
### Español
En la calma está la fuerza.
### Guaraní
Py’aguýpe oĩ mbarete.

## 🇭🇹 HT - Haiti (Haïti)
### Kreyòl ayisyen
Nan kalm gen fòs.

## 🇨🇦 CA - Canada (Canada)
### English
In calm lies strength.
### Français
Dans le calme réside la force.

## 🇦🇺 AU - Australia (Australia)
### English
In calm lies strength.

## 🇳🇿 NZ - New Zealand (Aotearoa)
### English
In calm lies strength.
### Māori
I te mārie ka kitea te kaha.

## 🇫🇯 FJ - Fiji (Fiji)
### English
In calm lies strength.
### iTaukei
E tiko ena vakacegu na kaukauwa.

## 🇼🇸 WS - Samoa (Sāmoa)
### Gagana Samoa
I le filemu e iai le malosi.

## 🇹🇴 TO - Tonga (Tonga)
### lea faka-Tonga
‘I he melino ‘oku ‘i ai ‘a e mālohi.

## 🇪🇸 ES - Spain (España)
### Català
En la calma hi ha força.

## 🇪🇸 ES - Spain (España) – Euskara
### Euskara
Lasaitasunean indarra dago.

## 🇪🇸 ES - Spain (España) – Galego
### Galego
Na calma hai forza.

## 🇬 SG - Singapore (Singapore)
### English
In calm lies strength.

### 中文（简体）
宁静中有力量。

### Bahasa Melayu
Dalam ketenangan ada kekuatan.

### தமிழ்
அமைதியில் வலிமை உள்ளது.

## 🇲🇲 MM - Myanmar (မြန်မာ)
### မြန်မာစာ
တိတ်ဆိတ်မှုထဲမှာ အားရှိတယ်။

## 🇸 PS - Palestine (فلسطين)
### العربية
في الهدوء تكمن القوة.

### English
In calm lies strength.

## 🇱🇧 LB - Lebanon (لبنان)
### العربية
في الهدوء تكمن القوة.

## 🇸🇾 SY - Syria (سوريا)
### العربية
في الهدوء تكمن القوة.

## 🇨🇾 CY - Cyprus (Κύπρος)
### Ελληνικά
Στη γαλήνη βρίσκεται η δύναμη.
### Türkçe
Sakinlikte güç vardır.

## 🇧🇦 BA - Bosnia and Herzegovina (Bosna i Hercegovina)
### Bosanski
U miru je snaga.

## 🇲🇰 MK - North Macedonia (Северна Македонија)
### Македонски
Во мирот има сила.

## 🇲🇪 ME - Montenegro (Crna Gora)
### Crnogorski
U miru je snaga.

## Very Long Texts - at Least 3000 Characters per Language

These synthetic sections support manual PDF visual inspection and automated font regression. They are anonymized, contain no customer text, and cover the three ERDA font groups from `fonts.yml`. The marked test blocks contain at least 3000 characters per language in the relevant Unicode range.

### ERDA CC-BY CJK

Mapping of the ten long lines and 3000-character test blocks: 🇹🇼 ZH-Hant - Traditional Chinese, 🇯🇵 JA - Japanese, 🇰🇷 KO - Korean.

1. 🇹🇼 ZH-Hant - Traditional Chinese (繁體中文): 繁體中文排版測試段落一在同一行保留很長的連續文字並加入 AI、PDF、ERDA 2.4.0 與 CC BY-SA 4.0 作為拉丁字母片段以觀察換行。
2. 🇹🇼 ZH-Hant - Traditional Chinese (繁體中文): 繁體中文排版測試段落二描述中立的文件流程、版本記錄、授權資訊、審核標記與公開知識管理，句子刻意延長以觸發 CJK 斷行。
3. 🇹🇼 ZH-Hant - Traditional Chinese (繁體中文): 繁體中文排版測試段落三把資料來源、摘要、註解、表格、腳註、索引與圖像說明放在同一視覺區域中檢查字距與行距。
4. 🇹🇼 ZH-Hant - Traditional Chinese (繁體中文): 繁體中文排版測試段落四包含 English terms like workflow, release, checksum, font cache and fallback chain，確認拉丁文字夾雜時仍能自然換行。
5. 🇯🇵 JA - Japanese (日本語): 日本語の長い確認文では公開資料、版管理、校正記録、PDF 出力、AI 参照確認、ERDA フォントという語を並べて折り返しを観察します。
6. 🇯🇵 JA - Japanese (日本語): 日本語の追加確認文では句読点と漢字かな交じり文を続け、長い見出し風の内容が本文幅を越えずに収まるかを確認します。
7. 🇰🇷 KO - Korean (한국어): 한국어 긴 확인 문장은 문서 흐름, 공개 라이선스, PDF 빌드, AI 검토, 글꼴 대체, 표지와 목차를 함께 다루며 줄바꿈을 확인합니다.
8. 🇰🇷 KO - Korean (한국어): 한국어 추가 확인 문장은 공백이 있는 음절 조합과 라틴 조각 ERDA, CJK, PDF, QA 를 섞어 글꼴 전환과 행간을 살펴봅니다.
9. 🇹🇼 ZH-Hant - Traditional Chinese (繁體中文): 繁體中文排版測試段落九使用多個標點符號、括號（測試）、冒號：說明、分號；延伸內容，檢查標點前後的間距與折行。
10. 🇹🇼 ZH-Hant - Traditional Chinese (繁體中文): 繁體中文排版測試段落十結束此組樣本，目標是讓人工檢視者在單頁中看到足夠長度的 CJK 文字與拉丁片段混排效果。

#### 🇹🇼 ZH-Hant - 3000-Character Test Block

<!-- ERDA-LONG-SAMPLE: ZH-HANT START -->
01. 繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。
02. 繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。
03. 繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。
04. 繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。
05. 繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。
06. 繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。
07. 繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。繁體中文公開文件排版檢查文字描述版本記錄授權資訊摘要表格註解索引封面目錄審核流程可重現建置字型回退頁面邊界與安全換行。
<!-- ERDA-LONG-SAMPLE: ZH-HANT END -->

#### 🇯🇵 JA - 3000-Character Test Block

<!-- ERDA-LONG-SAMPLE: JA START -->
01. 日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。
02. 日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。
03. 日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。
04. 日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。
05. 日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。
06. 日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。
07. 日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。日本語公開資料組版確認文は版管理校正記録要約表索引目次注記画像説明字型回退ページ境界安全な改行を中立的に検査します。
<!-- ERDA-LONG-SAMPLE: JA END -->

#### 🇰🇷 KO - 3000-Character Test Block

<!-- ERDA-LONG-SAMPLE: KO START -->
01. 한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.
02. 한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.
03. 한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.
04. 한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.
05. 한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.
06. 한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.
07. 한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.한국어공개문서조판확인문은버전기록라이선스요약표주석색인표지목차검토흐름글꼴대체페이지경계안전한줄바꿈을중립적으로점검합니다.
<!-- ERDA-LONG-SAMPLE: KO END -->

### ERDA CC-BY Indic

Mapping of the ten long lines: 🇮🇳 HI-Deva - Hindi in Devanagari (lines 1-10). The current ERDA CC-BY Indic test intentionally uses Devanagari because that script is covered by the available font.

1. 🇮🇳 HI-Deva - Hindi / Devanagari (हिन्दी): हिन्दी परीक्षण पंक्ति एक बहुत लंबी है और इसमें PDF, ERDA, AI तथा संस्करण 2.4.0 जैसे लैटिन अंश हैं ताकि देवनागरी आकार और पंक्ति-विराम देखे जा सकें।
2. 🇮🇳 HI-Deva - Hindi / Devanagari (हिन्दी): हिन्दी परीक्षण पंक्ति दो दस्तावेज़, स्रोत, तालिका, टिप्पणी, अनुक्रमणिका, प्रकाशन और समीक्षा जैसे तटस्थ शब्दों को जोड़ती है ताकि पाठ पर्याप्त लंबा रहे।
3. 🇮🇳 HI-Deva - Hindi / Devanagari (हिन्दी): देवनागरी परीक्षण पंक्ति तीन में प्रकाशन मार्ग, फ़ॉन्ट कैश, लाइसेंस फ़ाइल, सामग्री सूची, संदर्भ जाँच और दृश्य निरीक्षण जैसे तटस्थ शब्द रखे गए हैं।
4. 🇮🇳 HI-Deva - Hindi / Devanagari (हिन्दी): देवनागरी परीक्षण पंक्ति चार लंबे संयुक्ताक्षरों, मात्रा चिह्नों, पूर्ण विराम, अंकों 12345 और ERDA PDF QA जैसे छोटे लैटिन समूहों को साथ दिखाती है।
5. 🇮🇳 HI-Deva - Hindi / Devanagari (हिन्दी): देवनागरी परीक्षण पंक्ति पाँच यह देखती है कि अनुच्छेद लंबा होने पर भी अक्षर स्पष्ट रहें, चिह्न अलग न टूटें और पंक्ति की ऊँचाई संतुलित दिखे।
6. 🇮🇳 HI-Deva - Hindi / Devanagari (हिन्दी): देवनागरी परीक्षण पंक्ति छह में समीक्षा, सुधार, प्रकाशन, संग्रह, मानचित्र, तालिका, अनुक्रमणिका और टिप्पणी जैसे शब्द एक विस्तृत वाक्य बनाते हैं।
7. 🇮🇳 HI-Deva - Hindi / Devanagari (हिन्दी): देवनागरी परीक्षण पंक्ति सात फ़ॉलबैक शृंखला, मुख्य फ़ॉन्ट, सहायक फ़ॉन्ट, PDF निर्यात और हस्तचालित दृष्टि परीक्षण को एक साथ जाँचती है।
8. 🇮🇳 HI-Deva - Hindi / Devanagari (हिन्दी): देवनागरी परीक्षण पंक्ति आठ में शांत, सार्वजनिक, निरपेक्ष और पुनरुत्पाद्य सामग्री है, ताकि किसी वास्तविक ग्राहक पाठ का प्रयोग न हो।
9. 🇮🇳 HI-Deva - Hindi / Devanagari (हिन्दी): देवनागरी परीक्षण पंक्ति नौ लम्बे पाठ, छोटे शब्द, विराम चिह्न, कोष्ठक (परीक्षण), द्विबिंदु: विवरण और अर्धविराम; विस्तार को मिलाती है।
10. 🇮🇳 HI-Deva - Hindi / Devanagari (हिन्दी): देवनागरी परीक्षण पंक्ति दस इस समूह को समाप्त करती है और ERDA CC-BY Indic फ़ॉन्ट के दृश्य उपयोग को पर्याप्त लंबाई में दिखाती है।

#### 🇮🇳 HI-Deva - 3000-Character Test Block

<!-- ERDA-LONG-SAMPLE: HI-DEVA START -->
01. हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है।
02. हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है।
03. हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है।
04. हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है।
05. हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है।
06. हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है।
07. हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है।
08. हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है।
09. हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है।
10. हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है। हिन्दी देवनागरी परीक्षण पाठ दस्तावेज़ संस्करण स्रोत तालिका टिप्पणी अनुक्रमणिका प्रकाशन समीक्षा फ़ॉन्ट कैश पृष्ठ सीमा सुरक्षित पंक्ति विराम को तटस्थ रूप से जाँचता है।
<!-- ERDA-LONG-SAMPLE: HI-DEVA END -->

### ERDA CC-BY Ethiopic

Mapping of the ten long lines: 🇪🇹 AM - Amharic (lines 1-4, 7-8, 10), 🇪🇷 TI - Tigrinya (lines 5-6, 9).

1. 🇪🇹 AM - Amharic (አማርኛ): አማርኛ የረጅም ጽሑፍ ሙከራ መስመር አንድ ሰነድ፣ ስሪት፣ ምንጭ፣ ሰንጠረዥ፣ PDF፣ ERDA እና AI ቃላትን በአንድ ረጅም አረፍተ ነገር ያቀርባል።
2. 🇪🇹 AM - Amharic (አማርኛ): አማርኛ የረጅም ጽሑፍ ሙከራ መስመር ሁለት የፊደል መተካት፣ የመስመር ስብራት፣ የገጽ አቀማመጥ እና የምልክት ርቀት ለማየት ይረዳል።
3. 🇪🇹 AM - Amharic (አማርኛ): አማርኛ መስመር ሶስት የህትመት ሂደትን፣ የፈቃድ መረጃን፣ የምርመራ ማስታወሻን እና የማውጫ አገናኝን በተራ ያሳያል።
4. 🇪🇹 AM - Amharic (አማርኛ): አማርኛ መስመር አራት በጽሑፍ መካከል Latin terms like workflow, release, QA and checksum በመጨመር የፊደል መቀያየርን ይፈትሻል።
5. 🇪🇷 TI - Tigrinya (ትግርኛ): ትግርኛ የረጅም ጽሑፍ መስመር ሓሙሽተ ሰነድ፣ ምንጪ፣ ፍቓድ፣ PDF፣ ERDA እና AI ቃላት ብሓደ ነዊሕ ሓሳብ ይምልከት።
6. 🇪🇷 TI - Tigrinya (ትግርኛ): ትግርኛ መስመር ሽዱሽተ ፊደላት፣ ምልክታት፣ ክፍተት፣ መስመር ምቁራጽን የገጽ ኣቀማመጥን ንምርኣይ ዝተዳለወ እዩ።
7. 🇪🇹 AM - Amharic (አማርኛ): አማርኛ መስመር ሰባት በረጅም ገጽታ ውስጥ የተመሳሳይ ፊደሎች እንዳይጠበቁ እና የቃላት ክፍተት እንዲታይ ተዘጋጅቷል።
8. 🇪🇹 AM - Amharic (አማርኛ): አማርኛ መስመር ስምንት የተለያዩ ምልክቶችን፣ ቁጥሮችን 12345፣ ስሪት 2.4.0 እና ቀላል የሰነድ ቃላትን ያጣምራል።
9. 🇪🇷 TI - Tigrinya (ትግርኛ): ትግርኛ መስመር ትሽዓተ ነዊሕ ዓረፍተ ነገር ብምጥቃም ቅርጺ ፊደል፣ ክብደት ፊደልን ርቀት መስመርን ንምርመራ ይጠቅም።
10. 🇪🇹 AM - Amharic (አማርኛ): አማርኛ መስመር አስር የዚህን ክፍል ይዘጋል እና በPDF ውስጥ የERDA Ethiopic ፊደል መታየትን በቂ ርዝመት ላይ ያረጋግጣል።

#### 🇪🇹 AM - 3000-Character Test Block

<!-- ERDA-LONG-SAMPLE: AM START -->
01. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
02. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
03. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
04. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
05. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
06. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
07. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
08. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
09. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
10. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
11. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
12. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
13. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
14. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
15. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
16. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
17. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
18. አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል። አማርኛ የህትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጭ ሰንጠረዥ ማስታወሻ ማውጫ ፈቃድ ግምገማ ፊደል መተካት የገጽ ድንበር እና የመስመር ስብራትን በገለልተኛ መንገድ ይፈትሻል።
<!-- ERDA-LONG-SAMPLE: AM END -->

#### 🇪🇷 TI - 3000-Character Test Block

<!-- ERDA-LONG-SAMPLE: TI START -->
01. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
02. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
03. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
04. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
05. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
06. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
07. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
08. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
09. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
10. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
11. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
12. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
13. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
14. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
15. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
16. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
17. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
18. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
19. ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ። ትግርኛ ናይ ሕትመት ሙከራ ጽሑፍ ሰነድ ስሪት ምንጪ ሰንጠረዥ መዘኻኸሪ ማውጫ ፍቓድ ግምገማ ፊደል ምትካእ የገጽ ዶብ እና መስመር ምቁራጽ ብገለልተኛ መንገዲ ይፈትሽ።
<!-- ERDA-LONG-SAMPLE: TI END -->


\newpage

---
title: Markdown Advanced Features
date: 2026-01-11
version: 1.0
doc_type: example
category: documentation-features
---
<a id="md-examples-markdown-advanced-features"></a>


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

```{.python title="example.py"}
# example.py
def greet(name):
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("World"))
```

### Long Code Fence Wrapping

```yaml
description: >-
  State: {{country-code}}, date: {{YYYY-MM-dd}}, responsible editorial desk:
  {{author}}, legally accountable office: {{official}}, publication channel:
  {{distribution-channel}}, review state: {{quality-gate-status}}
```

```text
UNWRAPPED-CODE-FENCE-STRESS: state={{country-code}}; date={{YYYY-MM-dd}}; responsible-editorial-desk={{author}}; legally-accountable-office={{official}}; publication-channel={{distribution-channel}}; review-state={{quality-gate-status}}; checksum={{content-package-sha256}}; distribution-target={{long-form-customer-publication-profile}}
```

```text
URL-CODE-FENCE-STRESS: https://www.example.org/reports/world-energy-outlook-2024/downloads/long-code-fence-url?scenario=stated-policies&region=european-union&format=pdf&checksum={{content-package-sha256}}#executive-summary
```

## Tables with Alignment

### Complex Table

| Feature | Basic | Professional | Enterprise |
|:--------|:-----:|:------------:|-----------:|
| Users   | 5     | 50           | Unlimited  |
| Storage | 10GB  | 100GB        | 1TB        |
| Support | Email | Priority     | 24/7       |
| Price   | Free  | £50/month    | £200/month |

\newpage
\newgeometry{paperwidth=594mm, paperheight=420mm, left=18mm, right=18mm, top=18mm, bottom=18mm}


\pagewidth=594mm
\pageheight=420mm
### Wide Decision Table (Anonymized)

\begin{longtable}{@{}>{\raggedright\arraybackslash}p{27.50mm}@{\hspace{4.50mm}}>{\raggedright\arraybackslash}p{34.00mm}@{\hspace{4.50mm}}>{\raggedright\arraybackslash}p{26.23mm}@{\hspace{4.50mm}}>{\raggedright\arraybackslash}p{60.63mm}@{\hspace{4.50mm}}>{\raggedright\arraybackslash}p{113.98mm}@{\hspace{4.50mm}}>{\raggedright\arraybackslash}p{67.92mm}@{\hspace{4.50mm}}>{\raggedright\arraybackslash}p{40.48mm}@{\hspace{4.50mm}}>{\raggedright\arraybackslash}p{42.27mm}@{\hspace{4.50mm}}>{\raggedright\arraybackslash}p{104.48mm}@{}}\toprule Area & Code & Governance grade & Charter status & Entry conditions & Cooperation & Partnership level & Core-group potential & Comment \\\midrule \endhead Area Alpha Network & A-A1 & high stable & charter frame reviewed, control path documented & Entry conditions with audit path, privacy impact review, and aligned safeguard clause & Professional cooperation, data room, crisis exercise & Associated with expansion path & plausible in the medium term & Anonymized long note with rationale, risk marker, and open review task \\Area Beta Corridor & A-B2 & moderately stable & transition status with external quality assurance & Integration only after evidence of reliable operating processes and consistent reporting duties & Pilot cooperation, training, shared situation report & Observing partnership & depends on follow-up review & Anonymized assessment with intentionally long text width for PDF table stress \\Area Gamma Mesh & A-C3 & uneven & charter comparison started, decision open & Preconditions: clarify responsibilities, finish data classification, confirm audit window & Expert dialogue and technical inventory & Preparatory cooperation & not currently robust & Neutral sample row without customer names, original places, or political classification \\\bottomrule \end{longtable}
\restoregeometry
\pagewidth=210mm
\pageheight=297mm
\newpage

### Table With Long Script Runs

| Language | Signal | Editorial purpose |
|---|---|---|
| CJK | 生命共同体治理结构连续性评估生命共同体治理结构连续性评估生命共同体治理结构连续性评估 | Long character runs without spaces are a general layout risk, not a German-only issue. |
| Hangul | 민주적회복력전환거버넌스연속성평가민주적회복력전환거버넌스연속성평가 | Table paper selection must account for script runs and wide glyphs. |

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


\newpage

---
title: "🧪 Emoji in headings – Header samples"
description: "Regression test page for emojis in headings (bookmarks/ToC) and in the front matter title."
date: 2026-01-08
version: 1.0
doc_type: example
category: "emoji-test"
show_in_summary: true
history:
  - version: 1.0
    date: 2026-01-08
    changes: New test page for emojis in headings.
---
<a id="md-examples-emoji-headings"></a>


# 🧪 Emoji in headings – Header samples

This page tests the correct display of emojis in headings at different levels. Particularly relevant is the encoding in PDF bookmarks and the table of contents.

## 🎯 Test scenarios

Emojis in headings place special demands on document processing:

- **PDF bookmarks**: Correct Unicode encoding in PDF table of contents
- **TOC generation**: Table of contents with emoji characters
- **Font fallbacks**: Switching between text and emoji fonts
- **Hierarchy**: Emojis at all heading levels (H1-H6)

## 📋 Emoji test

### Sample set

This page places emojis in headings to test bookmarks/TOC and PDF strings.

#### 🧪 Heading with emoji

Inline: ✅ ⚠️ ℹ️ 🔒 🔑 ♻️

#### 🧩 ZWJ sequences (complex)

👩‍💻 👨‍💻 🧑‍🚀 👨‍👩‍👧‍👦

#### 🏁 Flags in text

🇩🇪 🇪🇺 🇬🇧 🇺🇸 🇺🇳

#### 🔢 Keycaps & variants

0️⃣ 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣ 9️⃣ 🔟 #️⃣ *️⃣


\newpage

---
title: Template for multilingual neutral text
date: 2024-06-02
version: 1.1
doc_type: template
show_in_summary: false
---
<a id="md-templates-multilingual-neutral-text"></a>


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


\newpage

---
title: Templates
date: 2024-06-02
version: 1.1
doc_type: template
---
<a id="md-templates-readme"></a>


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

See [multilingual-neutral-text.md](#md-templates-multilingual-neutral-text) for details.

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


\newpage

---
title: Translator's Note
doc_type: translators-note
order: 6
---
<a id="md-translators-note"></a>


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


\newpage

---
title: List of Tables
date: 2025-12-29
version: 1.0
doc_type: list-of-tables
auto_generate: true
include_chapter_tables: true
numbering_style: "decimal"
---
<a id="md-list-of-tables"></a>


# List of Tables

This section provides a comprehensive index of all tables appearing throughout the document. Tables are numbered sequentially and referenced by their location in the text.

## Purpose

The list of tables serves multiple functions:

- **Quick reference**: Locate specific tables without scanning the entire document
- **Content overview**: Understand the range of comparative and structured information presented
- **Navigation aid**: Jump directly to tables of interest

## Organization

Tables are listed in order of appearance with:

- Table number
- Descriptive caption
- Page reference (in PDF output)

_Note: The complete list is automatically generated during the build process and includes all captioned tables from the chapters and appendices._


\newpage

---
title: List of Figures
date: 2025-12-29
version: 1.0
doc_type: list-of-figures
auto_generate: true
include_formats: [png, jpg, svg, pdf]
numbering_style: "decimal"
---
<a id="md-list-of-figures"></a>


# List of Figures

This section catalogues all figures, diagrams, and illustrations used throughout the document. Each figure is numbered and captioned for easy reference.

## Purpose

The list of figures provides:

- **Visual content index**: Overview of all graphical elements
- **Quick access**: Direct navigation to specific illustrations
- **Content audit**: Verification that all images are properly captioned

## Supported formats

The document includes figures in various formats:

- **Raster images**: PNG, JPEG for photographs and screenshots
- **Vector graphics**: SVG for scalable diagrams and icons
- **Mixed content**: Combination of different formats as needed

## Organization

Figures are listed sequentially with:

- Figure number
- Descriptive caption
- Page location (in PDF output)
- Format type where relevant

_Note: The complete list is automatically generated during the build process and includes all captioned figures from all document sections._


\newpage

---
title: List of Abbreviations
doc_type: list-of-abbreviations
order: 7
---
<a id="md-list-of-abbreviations"></a>


# List of Abbreviations

This section defines abbreviations and acronyms used throughout the document.

## Technical abbreviations

**API**  
Application Programming Interface

**CAP**  
Consistency, Availability, Partition tolerance (theorem)

**CLI**  
Command-Line Interface

**CPU**  
Central Processing Unit

**CSS**  
Cascading Style Sheets

**DPI**  
Dots Per Inch

**HTML**  
HyperText Markup Language

**HTTP**  
HyperText Transfer Protocol

**IDE**  
Integrated Development Environment

**ISO**  
International Organization for Standardization

**JSON**  
JavaScript Object Notation

**LTR**  
Left-to-Right (text direction)

**PDF**  
Portable Document Format

**PNG**  
Portable Network Graphics

**RTL**  
Right-to-Left (text direction)

**SQL**  
Structured Query Language

**SVG**  
Scalable Vector Graphics

**TOC**  
Table of Contents

**UI**  
User Interface

**URL**  
Uniform Resource Locator

**UTF**  
Unicode Transformation Format

**XML**  
Extensible Markup Language

**YAML**  
YAML Ain't Markup Language

**ZWJ**  
Zero Width Joiner (Unicode)


\newpage

---
title: Appendices
date: 2024-06-01
version: 1.0
doc_type: appendix-overview
---
<a id="md-appendices-readme"></a>


# Appendices

Supplementary materials, technical specifications, and reference information.

## Purpose

Appendices provide:

- **Supplementary detail**: In-depth technical information
- **Reference material**: Tables, specifications, and data
- **Technical documentation**: Implementation details and configurations
- **Supporting evidence**: Font coverage, testing results, methodologies

## Organisation

Appendices are labelled alphabetically:

- **Appendix A**: Data sources and table layout
- **Appendix B**: Emoji and font coverage

Each appendix includes:

- Unique identifier (A, B, C...)
- Descriptive title
- Category classification (technical, reference, etc.)
- Version history

## Structure

### Frontmatter

Each appendix uses consistent metadata:

```yaml
---
title: Appendix X – Title
date: YYYY-MM-DD
version: X.Y
doc_type: appendix
appendix_id: "X"
category: "technical" | "reference" | "legal"
---
```

### Content patterns

Appendices typically include:

- Technical specifications
- Data tables and matrices
- Testing methodologies
- Configuration examples
- Detailed calculations
- Reference implementations

## Navigation

Appendices appear:

- After main content chapters
- Before indices (table of contents, figures, etc.)
- In alphabetical order by identifier

They are accessible via:

- Table of contents links
- PDF bookmarks
- Cross-references from main text

## Cross-referencing

Reference appendices from main text:

```markdown
See [Appendix A](../appendices/appendix-a.md) for data sources.
Font coverage is detailed in [Appendix B](../appendices/emoji-font-coverage.md).
```

## Types of appendices

### Technical appendices

- Implementation details
- Algorithm specifications
- Configuration references
- Testing procedures

### Reference appendices

- Data tables
- Glossaries
- Bibliography
- Standards references

### Legal appendices

- Licence texts
- Compliance documentation
- Attribution details
- Legal notices


\newpage

---
title: Appendix A – Data sources and table layout
date: 2024-06-01
version: 1.0
doc_type: appendix
appendix_id: "A"
category: "technical"
---
<a id="md-appendices-appendix-a"></a>


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


\newpage

---
title: Appendix B – Emoji & font coverage
description: Evidence of suitable fonts for all scripts and coloured emojis used in the sample content.
date: 2024-06-05
version: 1.0
doc_type: appendix
appendix_id: "B"
category: "technical"
history:
  - version: 1.0
    date: 2024-06-05
    changes: Initial version with font matrix and testing notes.
---
<a id="md-appendices-emoji-font-coverage"></a>


# Appendix B – Emoji & font coverage

This appendix documents font coverage for the diverse Unicode content used throughout this document, including emoji rendering and multilingual text support.

## Font stack

The document uses a carefully configured font stack:

### Primary text fonts

**DejaVu Serif / DejaVu Sans**

- **Coverage**: Latin, Cyrillic, Greek, basic IPA
- **Purpose**: Main body text and headings
- **Licence**: Free (Bitstream Vera derivative)
- **Unicode blocks**: ∼3,000 glyphs covering common scripts

### Emoji fonts

**Twemoji Mozilla (COLRv1)**

- **Coverage**: Full Emoji 13.0+ support
- **Format**: COLRv1 (colour font format)
- **Purpose**: Primary emoji rendering
- **Licence**: CC BY 4.0
- **Rendering**: Native colour in modern systems

**Twitter Color Emoji (Fallback)**

- **Coverage**: Emoji 12.0
- **Format**: CBDT/CBLC (bitmap colour)
- **Purpose**: Fallback for older systems
- **Licence**: CC BY 4.0 / MIT

## Emoji categories tested

Comprehensive testing across all Unicode emoji categories:

### 😀 People & Emotions

- Faces: 😀 😃 😄 😁 😅
- Hands: 👋 🤚 🖐 ✋ 🖖
- People: 👶 👧 🧒 👦 👨
- Skin tones: 👋🏻 👋🏼 👋🏽 👋🏾 👋🏿

### 🐕 Animals & Nature

- Mammals: 🐕 🐈 🐎 🐄 🐖
- Birds: 🐓 🐔 🐤 🐣 🐥
- Plants: 🌲 🌳 🌴 🌵 🌾
- Weather: ☀️ ⛅ ☁️ ⛈️ 🌧️

### 🍕 Food & Drink

- Prepared food: 🍕 🍔 🍟 🌭 🥪
- Fruit: 🍎 🍊 🍋 🍌 🍉
- Drinks: ☕ 🍵 🥤 🍺 🍷

### ⚽ Activities & Sports

- Sports: ⚽ 🏀 🏈 ⚾ 🥎
- Games: 🎮 🎯 🎲 🎰 🎳
- Arts: 🎨 🎭 🎪 🎬 🎤

### 🚗 Travel & Places

- Vehicles: 🚗 🚕 🚙 🚌 🚎
- Buildings: 🏠 🏡 🏢 🏣 🏤
- Geography: 🏔 ⛰️ 🏕 🏖 🏜

### 💡 Objects

- Tech: 💻 ⌨ 🖥 🖨 🖱
- Tools: 🔨 ⛏️ 🛠 ⚒️ 🔧
- Office: 📝 ✏ ✏️ 🖊 🖋

### 🔣 Symbols

- Math: ➕ ➖ ✖ ➗ 🟰
- Arrows: ⬆ ⬇ ⬅ ➡ ↔️
- Shapes: ◼️ ◻️ 🔲 🔳 ⬛

### 🏁 Flags

- Country flags: 🇬🇧 🇩🇪 🇫🇷 🇪🇸 🇮🇹
- Regional flags: 🏴‍☠️ (requires ZWJ support)
- Special flags: 🏳 🏴 🏳️‍🌈

## Complex emoji sequences

### Zero-Width Joiner (ZWJ) sequences

Testing compound emoji:

- **Family**: 👨‍👩‍👧‍👦 (requires ZWJ support)
- **Professions**: 👨‍⚕️ 👩‍🏫 👨‍🌾
- **Combinations**: 🏴‍☠️ 🏳️‍🌈

### Skin tone modifiers

Fitzpatrick scale support:

- Type 1-2 (light): 👋🏻
- Type 3 (medium-light): 👋🏼
- Type 4 (medium): 👋🏽
- Type 5 (medium-dark): 👋🏾
- Type 6 (dark): 👋🏿

### Flag sequences

Regional indicator symbols:

- 🇬 + 🇧 = 🇬🇧 (UK flag)
- 🇩 + 🇪 = 🇩🇪 (German flag)

## Script coverage

Multilingual text support across 100+ languages:

### Latin-based scripts

- Western European: English, German, French, Spanish
- Eastern European: Polish, Czech, Hungarian
- Special characters: Ā Ē Ī Ō Ū (macrons)

### Cyrillic

- Russian: Привет мир
- Ukrainian: Привіт світ
- Bulgarian: Здравей свят

### Greek

- Modern Greek: Γεια σου κόσμε
- Polytonic Greek: ἀρχή (archaic)

### Asian scripts

- Chinese (Simplified): 你好世界
- Japanese: こんにちは世界 (Hiragana)
- Korean: 안녕하세요 세계 (Hangul)

### Arabic & RTL scripts

- Arabic: مرحبا بالعالم (RTL)
- Hebrew: שלום עולם (RTL)
- Persian: سلام دنیا (RTL)

### South Asian scripts

- Devanagari: नमस्ते दुनिया (Hindi)
- Tamil: வணக்கம் உலகம்
- Bengali: হ্যালো বিশ্ব

### Other scripts

- Thai: สวัสดีชาวโลก
- Amharic: ሰላም ልዑል
- Georgian: გამარჯობა მსოფლიო

## Testing methodology

### Visual verification

All emoji and scripts:

1. Rendered in PDF output
2. Visually inspected for correctness
3. Checked for proper colour rendering (emoji)
4. Verified in both screen and print modes

### Font fallback chain

The system tests fallback behaviour:

```
Primary → Secondary → System fallback
```

- If primary font lacks a glyph, system tries secondary
- Final fallback to system fonts if needed
- Missing glyphs indicated by □ (replacement character)

### Known limitations

1. **ZWJ sequences**: Complex emoji may render as separate glyphs on older systems
2. **COLRv1 support**: Requires modern font rendering (Cairo 1.18+, FreeType 2.13+)
3. **RTL layout**: Simplified handling; complex bidirectional text may need adjustment
4. **Rare scripts**: Some scripts require additional font installation

## Font configuration

See [`fonts-storage/fonts.conf`](../../fonts-storage/fonts.conf) for the complete fontconfig configuration.

Key settings:

- Emoji font priority ordering
- Script-specific font mappings
- Fallback chains
- Hinting and antialiasing preferences- YAML frontmatter (document metadata)
- Heading hierarchy (TOC / PDF bookmarks)
- Lists, code blocks, blockquotes
- Tables and references
- Stable navigation (SUMMARY.md)

### Example table

| Item | Purpose |
|---|---|
| Heading | TOC/bookmarks |
| Table | list of tables |

### Example code block

```
python -m gitbook_worker.tools.workflow_orchestrator --help
```


\newpage

---
doc_type: legal-notice
title: Legal Notice
version: 1.0.0
---
<a id="md-legal-notice"></a>


# Legal Notice

This document serves as a demonstration of legal notice formatting in technical publications.

## Publisher information

In a production document, this section would include:

- Publisher name and address
- Responsible parties
- Editorial team contact information
- ISBN/ISSN numbers where applicable

## Copyright notice

Typical copyright statements include:

- Copyright year and holder
- Rights reserved statement
- Permitted use conditions
- Trademark acknowledgements

## Licence terms

For open-source documentation:

- **Content licence**: Creative Commons or similar
- **Code licence**: MIT, Apache, GPL, or other open-source licence
- **Asset licences**: Individual licences for fonts, images, and third-party content

See [LICENSE-CODE](../../LICENSE-CODE) and [LICENSE-FONTS](../../LICENSE-FONTS) for specific terms.

## Liability disclaimer

Standard disclaimers typically cover:

- Accuracy of information
- Fitness for particular purpose
- Third-party content responsibility
- External link liability

## Data protection

For digital publications:

- Data collection practices
- Privacy policy references
- Cookie usage (web versions)
- Analytics and tracking disclosure

## Contact

In production, include:

- Technical support contact
- Editorial feedback address
- Legal enquiries contact


\newpage

---
doc_type: glossary
title: Glossary
version: 1.0.0
---
<a id="md-glossary"></a>


# Glossary

Definitions of technical terms used throughout this document.

## A

**API** (Application Programming Interface)  
Interface that enables software components to communicate with each other.

**Accessibility**  
Design of content that is usable by people with disabilities.

## B

**Bibliography**  
List of sources cited or referenced in a document.

**Build Pipeline**  
Automated process for converting source files into output formats.

## C

**CI/CD** (Continuous Integration / Continuous Deployment)  
Practice of frequently integrating code and automatically deploying it.

**COLRv1**  
Modern colour font format for vector graphics in fonts.

## D

**Documentation Framework**  
Structured system for creating and managing documentation.

## E

**Emoji**  
Pictographic characters from the Unicode Standard representing emotions and objects.

## F

**Fontconfig**  
Library for configuring and customising font access.

**Frontmatter**  
Metadata block at the beginning of a Markdown file (YAML format).

## G

**Git**  
Distributed version control system for tracking code changes.

**Glyph**  
Visual character representing one or more Unicode code points.

## I

**ISO 8601**  
International standard for date and time formats.

## L

**LaTeX**  
Typesetting system for high-quality typographic output.

**Licence**  
Legal agreement regarding the use of software or content.

## M

**Markdown**  
Lightweight markup language for formatting text.

**Metadata**  
Information about documents (title, author, date, etc.).

## O

**Open Source**  
Software with freely available source code.

**OpenType**  
Modern font format with advanced typographic capabilities.

## P

**Pandoc**  
Universal document conversion tool.

**PDF** (Portable Document Format)  
Platform-independent file format for documents.

## R

**Rendering**  
Process of visually displaying code or markup.

**RTL** (Right-to-Left)  
Text direction from right to left (Arabic, Hebrew).

## S

**Semantic Versioning**  
Version numbering using the MAJOR.MINOR.PATCH scheme.

**SVG** (Scalable Vector Graphics)  
Vector graphics format for scalable images.

## U

**Unicode**  
Universal character encoding standard for all writing systems.

## V

**Version Control**  
System for tracking and managing changes to files.

## X

**XeLaTeX**  
LaTeX engine with native Unicode and OpenType support.

## Y

**YAML** (YAML Ain't Markup Language)  
Human-readable data serialisation format.

## Z

**ZWJ** (Zero Width Joiner)  
Invisible Unicode character for combining emojis.

---

_Note: This glossary contains terms relevant to this documentation framework. For complete definitions, please consult official specifications and standards._


\newpage

---
title: Citations & further reading
date: 2024-06-01
version: 1.0
doc_type: bibliography
citation_style: "APA"
---
<a id="md-references"></a>


# Citations & further reading

Bibliography and additional resources for further reading.

## Purpose

This bibliography:

- **Documents sources**: All cited references
- **Enables verification**: Readers can check original sources
- **Provides context**: Background information on topics
- **Extends knowledge**: Further reading materials

## Citation style

This document uses **APA style** (7th edition):

```
Author, A. A. (Year). Title of work. Publisher.
```

For online resources:

```
Author, A. A. (Year). Title. Website Name. URL
```

## Categories

### Technical standards

Official specifications and standards:

- ISO, RFC, W3C specifications
- Unicode Consortium documents
- OpenType specifications

### Documentation

Official tool and software documentation:

- Pandoc manual
- LaTeX/XeLaTeX references
- Git documentation
- Python libraries

### Articles and tutorials

Best practices and guides:

- Technical blog posts
- Tutorial websites
- Community resources

### Books

Technical books on relevant topics:

- Documentation methodology
- Typography and typesetting
- Software development

## Example entries

### Standards

**Unicode Consortium.** (2023). *The Unicode Standard, Version 15.0*. Unicode Consortium. https://www.unicode.org/versions/Unicode15.0.0/

**Internet Engineering Task Force.** (2018). *RFC 8259: The JavaScript Object Notation (JSON) Data Interchange Format*. IETF. https://tools.ietf.org/html/rfc8259

### Software documentation

**Pandoc.** (2023). *Pandoc User's Guide*. https://pandoc.org/MANUAL.html

**LaTeX Project.** (2023). *LaTeX2e: An unofficial reference manual*. https://latexref.xyz/

### Articles

**Semantic Versioning.** (2023). *Semantic Versioning 2.0.0*. https://semver.org/

**Markdown Guide.** (2023). *Basic Syntax*. https://www.markdownguide.org/basic-syntax/

## Further resources

### Online communities

- **Stack Overflow**: Questions and answers on technical problems
- **GitHub**: Open-source projects and discussions
- **Reddit**: r/LaTeX, r/Markdown, r/technicalwriting

### Learning platforms

- **Write the Docs**: Community for technical writers
- **Overleaf**: Online LaTeX editor with tutorials
- **GitHub Learning Lab**: Git and GitHub courses

### Tools

- **Zotero**: Reference management
- **Grammarly**: Language checking
- **draw.io**: Diagram creation

## Source verification

When using sources:

1. **Check currency**: Is the information still current?
2. **Assess authority**: Is the source trustworthy?
3. **Multiple sources**: Confirm information
4. **Primary sources**: Prefer official documentation

## Contribution guidelines

When adding new references:

- Consistent citation style (APA)
- Complete bibliographic information
- Access date for online resources
- Categorisation for easy navigation

---

_Note: This bibliography is continuously updated. Contributions and corrections are welcome._


\newpage

---
doc_type: index
title: Index
version: 1.0.0
---
<a id="md-book-index"></a>


# Index

Alphabetical subject index for quick access to topics.

## Purpose

The index enables:

- **Quick lookup**: Immediate access to specific terms
- **Cross-references**: Linking related concepts
- **Completeness**: Overview of covered topics
- **Navigation**: Alternative access pattern to table of contents

## Structure

The index is organised:

- **Alphabetically**: Sorted by initial letter
- **Hierarchically**: Main and sub-terms
- **With page references**: Direct links to sections
- **Cross-referenced**: "See also" notes

## Usage

### In printed versions

The index appears:

- At the end of the document
- After appendices and lists
- With page numbers for each reference

### In digital versions

The index provides:

- Clickable links to sections
- Search functionality within the index
- Integration with PDF bookmarks

## Indexing

### Entries

Typical index entries:

```
Term, Page
  Sub-term, Page
  Sub-term, Page
Another Term, Page
  see also: Related Term
```

### Conventions

- **Bold**: Primary definition or main discussion
- *Italic*: Passing mention
- (Figure): Visual representation
- (Table): Tabular information

## Automatic generation

This index can be automatically generated from:

- Explicit index markers in Markdown
- Headings and subsections
- Glossary entries
- Code example titles

## Best practices

For effective indexing:

1. **Consistent terms**: Use uniform terminology
2. **Multiple entries**: Index concepts under different search terms
3. **Cross-references**: Connect related terms
4. **Avoid over-indexing**: Include only significant references

## Maintenance

The index should be:

- Updated with each major version
- Include new terms from added chapters
- Remove obsolete references
- Check consistency with glossary

---

_Note: A complete index is generated during the final build process and includes all indexed terms with precise page references._


\newpage

---
title: Acknowledgments & Attributions
date: 2025-12-29
version: 1.0
doc_type: attributions
include_font_licenses: true
include_contributors: true
categories:
  - fonts
  - libraries
  - contributors
---
<a id="md-attributions"></a>


# Acknowledgments & Attributions

This document acknowledges the contributors, tools, and resources that made this publication possible.

## Font attributions

This document uses the following open-source fonts:

### Twemoji Mozilla

- **Licence**: CC BY 4.0
- **Source**: Mozilla's Twemoji COLRv1 implementation
- **Purpose**: Emoji rendering in text
- **Licence URL**: https://creativecommons.org/licenses/by/4.0/

### DejaVu Fonts

- **Licence**: Bitstream Vera Licence / Arev Licence
- **Purpose**: Base text rendering
- **Coverage**: Latin, Cyrillic, Greek, and extensive Unicode blocks

### Twitter Color Emoji

- **Licence**: CC BY 4.0 (artwork) / MIT (code)
- **Source**: Twitter's open-source emoji set
- **Purpose**: Fallback emoji rendering

## Software tools

Built with open-source software:

- **Python**: Core automation and orchestration
- **Pandoc**: Markdown to LaTeX conversion
- **XeLaTeX/LuaLaTeX**: PDF typesetting
- **GitBook**: Content structure and metadata

## Python libraries

Key dependencies:

- **PyYAML**: Configuration and frontmatter parsing
- **GitPython**: Git repository management
- **Jinja2**: Template processing
- **svglib**: SVG handling and conversion

## Content and methodology

Special acknowledgements:

- **Unicode Consortium**: For comprehensive character encoding standards
- **OpenType specification**: For modern font rendering capabilities
- **Markdown community**: For lightweight, readable markup language

## Contributors

Gratitude to all who contributed:

- Content authors and editors
- Technical reviewers
- Translation teams
- Testing and quality assurance
- Documentation framework developers

## Licence compliance

All third-party assets are used in accordance with their respective licences. See:

- [LICENSE-CODE](../../LICENSE-CODE) for code licencing
- [LICENSE-FONTS](../../LICENSE-FONTS) for font licencing
- Individual attribution files in `fonts-storage/` for detailed font information

---

_This acknowledgements section demonstrates proper attribution practices for open-source documentation projects._


\newpage

---
doc_type: errata
title: Errata
version: 1.0.0
---
<a id="md-errata"></a>


# Errata

This section documents corrections and updates to the published document.

## Purpose

The errata page serves to:

- Document errors discovered after publication
- Provide corrections for known issues
- Track version-specific changes
- Maintain document accuracy over time

## How to report issues

If you discover an error:

1. Check this page to see if it's already documented
2. Note the version number, page/section, and nature of the issue
3. Report via the appropriate channel (issue tracker, email, etc.)

## Errata format

Each entry includes:

- **Version**: Which version contains the error
- **Location**: Page number or section reference
- **Type**: Typographical, technical, factual, or formatting error
- **Description**: What is incorrect
- **Correction**: The correct information
- **Status**: Fixed in version X.X.X or pending

## Version 1.0.0

_No errata reported for this version._

---

## Continuous improvement

This document is maintained as a living record. Regular reviews ensure:

- Technical accuracy
- Up-to-date references
- Correction of typographical errors
- Improvement of clarity

Check the release notes for the current version status.


\newpage

---
doc_type: release-notes
title: Release Notes
version: 1.0.0
---
<a id="md-release-notes"></a>


# Release Notes

This document tracks changes, improvements, and fixes across versions.

## Version 1.0.0 (2024-06-01)

### Initial release

First public version of the documentation framework.

**Features:**

- Multilingual support (English and German)
- Comprehensive emoji rendering across all Unicode categories
- 100+ language samples demonstrating font coverage
- Professional PDF generation with proper typography
- Structured navigation with table of contents
- Code examples and technical documentation patterns

**Content structure:**

- Core chapters demonstrating documentation patterns
- Examples section (emoji tests, image formats, language samples)
- Appendices (technical specifications, font coverage)
- Complete metadata framework (YAML frontmatter)

**Technical foundation:**

- Python-based build orchestration
- Markdown source format
- LaTeX/XeLaTeX PDF generation
- Unicode and OpenType font support
- Automated table of contents generation

### Known limitations

- Some complex emoji sequences may render differently depending on font support
- RTL (right-to-left) text layout uses simplified handling
- Large SVG images may require optimization for faster rendering

### Requirements

- Python 3.8+
- XeLaTeX or LuaLaTeX
- Required fonts: DejaVu, Twemoji Mozilla
- Git for version control

---

## Version history format

Future releases will follow this structure:

### Version X.Y.Z (YYYY-MM-DD)

**Added:**

- New features and capabilities

**Changed:**

- Modifications to existing functionality

**Fixed:**

- Bug fixes and corrections

**Deprecated:**

- Features marked for future removal

**Removed:**

- Discontinued features

**Security:**

- Security-related changes

---

## Semantic versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Incompatible changes
- **MINOR** (0.X.0): Backwards-compatible new features
- **PATCH** (0.0.X): Backwards-compatible bug fixes


\newpage

---
title: Colophon
date: 2025-12-29
version: 1.0
doc_type: colophon
position: "back"
include_technical_details: true
---
<a id="md-colophon"></a>


# Colophon

This document was created using a modern publishing workflow that transforms Markdown source files into professional PDF output.

## Production details

### Typography

- **Body text**: Professional serif typeface
- **Headings**: Sans-serif for clear hierarchy
- **Code**: Monospace font for technical content
- **Emoji**: Colour emoji font with extensive Unicode coverage

### Software and tools

This document was produced using:

- **Python**: Workflow orchestration and document processing
- **Markdown**: Lightweight markup for source content
- **LaTeX**: Professional typesetting engine
- **Git**: Version control for source management

### Document format

- **PDF/A compliance**: Archival-quality output
- **Embedded fonts**: Complete font embedding for consistency
- **Bookmarks**: Hierarchical navigation structure
- **Metadata**: Comprehensive document properties

### Design principles

The visual design follows established principles:

- Clear typographic hierarchy
- Generous whitespace for readability
- Consistent formatting throughout
- Accessible colour contrasts

### Licensing

See the licensing sections for details on content, code, and font licenses.

### Revision

Version 1.0, January 2026
