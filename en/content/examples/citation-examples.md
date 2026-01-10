---
title: Citation & Footnote Examples
date: 2026-01-11
version: 1.0
doc_type: example
category: documentation-features
---

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

See [Chapter 1](../chapters/chapter-01.md) for more on design patterns.

For emoji rendering details, refer to [Appendix B](../appendices/emoji-font-coverage.md).

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
