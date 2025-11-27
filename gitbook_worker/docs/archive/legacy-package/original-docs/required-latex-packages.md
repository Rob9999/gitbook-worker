# Required LaTeX Packages for Pandoc PDF Generation

## Context
Docker uses TeX Live 2025 `scheme-basic` (minimal installation ~132 packages).  
Local environment has full TeX Live 2025 with all packages.

This document lists **additional packages** required beyond `scheme-basic` for Pandoc→LuaLaTeX PDF generation with:
- German language support
- Unicode math and fonts
- Tables (booktabs, longtable)
- Code blocks (fancyvrb)
- Hyperlinks (hyperref)
- Emoji fonts (Twemoji Mozilla)

## Package List (Dockerfile.dynamic Line 102-119)

### Core Engines
- `xetex` - XeTeX engine (backup)
- `luatex` - LuaTeX engine (primary)
- `lualatex-math` - Math support for LuaLaTeX

### Font & Unicode
- `fontspec` - Font selection for XeLaTeX/LuaLaTeX
- `polyglossia` - Multi-language support (alternative to babel)
- `unicode-math` - Unicode math symbols

### German Language
- `babel-german` - German language support for babel
- `hyphen-german` - German hyphenation patterns

### Verbatim & Code
- `fancyvrb` - Enhanced verbatim environments (code blocks)
- `mdwtools` - Markdown tools (includes `footnote.sty` for enhanced footnote support)

### Layout
- `enumitem` - Customizable lists
- `geometry` - Page geometry (margins, paper size)
- `setspace` - Line spacing control

### Color
- `xcolor` - Color support

### Tables
- `booktabs` - Professional table formatting
- `longtable` - Multi-page tables
- `caption` - Customizable captions

### Headers/Footers
- `fancyhdr` - Custom headers and footers

### Hyperlinks
- `hyperref` - Hyperlinks and PDF metadata
- `url` - URL formatting

### Graphics
- `graphicx` - Enhanced graphics inclusion
- `graphics` - Base graphics support

### Math
- `amsmath` - AMS math environments
- `amsfonts` - AMS math fonts

### Text Formatting
- `ulem` - Underlining and strike-through

### Utility Packages (Dependencies)
- `etoolbox` - Programming utilities (required by many packages)
- `iftex` - Engine detection (required by fontspec, hyperref)
- `infwarerr` - Error handling (hyperref dependency)
- `kvoptions` - Key-value options (hyperref dependency)
- `kvsetkeys` - Key-value parsing (hyperref dependency)
- `ltxcmds` - LaTeX commands (hyperref dependency)
- `pdftexcmds` - pdfTeX primitives (hyperref dependency)

## Installation Method
```dockerfile
RUN cd /tmp \
    && wget -q https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz \
    && tar -xzf install-tl-unx.tar.gz \
    && cd install-tl-* \
    && echo "selected_scheme scheme-basic" > texlive.profile \
    && echo "instopt_adjustpath 0" >> texlive.profile \
    && echo "tlpdbopt_autobackup 0" >> texlive.profile \
    && echo "tlpdbopt_install_docfiles 0" >> texlive.profile \
    && echo "tlpdbopt_install_srcfiles 0" >> texlive.profile \
    && ./install-tl --profile=texlive.profile \
    && ln -sf /usr/local/texlive/2025/bin/x86_64-linux/* /usr/local/bin/ \
    && tlmgr update --self \
    && (tlmgr install \
        xetex luatex lualatex-math \
        fontspec polyglossia unicode-math \
        babel-german hyphen-german \
        fancyvrb \
        enumitem geometry \
        xcolor \
        booktabs longtable \
        caption fancyhdr \
        hyperref url \
        graphicx graphics \
        amsmath amsfonts \
        ulem \
        setspace \
        etoolbox \
        iftex \
        infwarerr kvoptions kvsetkeys ltxcmds pdftexcmds || true)
```

## Verification
After installation, verify:
```bash
lualatex --version   # LuaHBTeX 1.22.0
xelatex --version    # XeTeX 3.141592653-2.6-0.999997
kpsewhich fancyvrb.sty   # Check package is findable
```

## Maintenance
**When adding new Pandoc features**, check if they require additional packages:
- **Syntax highlighting**: `listings`, `minted`
- **Bibliography**: `biblatex`, `biber`
- **More languages**: `babel-*`, `hyphen-*`
- **Advanced math**: `mathtools`, `amsthm`

**Update this document** when adding packages to Dockerfile.dynamic.

## Related Files
- `Dockerfile.dynamic` (Line 89-119): TeX Live installation
- `AGENTS.md`: Licensing policy for fonts/packages
- `ATTRIBUTION.md`: Font and asset attribution
- `content/anhang-l-kolophon.md`: PDF Kolophon with font details

## Build Time Impact
- `scheme-basic`: ~1-2 minutes download + install
- Additional packages (25 packages): ~2-3 minutes
- **Total TeX Live setup**: ~3-5 minutes per Docker build

## Why Not scheme-full?
- **scheme-full**: ~7 GB, 3000+ packages, 20-30 minutes download
- **scheme-basic + selective**: ~500 MB, <200 packages, 5 minutes
- **Trade-off**: Faster builds, smaller images, explicit dependencies

## License Compliance
All TeX Live packages use **LaTeX Project Public License (LPPL)** or compatible.  
No GPL, OFL, or proprietary packages required for ERDA PDF generation.

---
**Last Updated**: 2025-01-01 (after fancyvrb, hyperref, longtable additions)
