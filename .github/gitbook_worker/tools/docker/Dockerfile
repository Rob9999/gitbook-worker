# =============================================================================
# ⚠️  DEPRECATED - DO NOT USE FOR NEW PROJECTS
# =============================================================================
# This Dockerfile is deprecated and will be removed in a future release.
# 
# ❌ Problems with this file:
#   - Hardcoded font configurations (not in sync with fonts.yml)
#   - No automatic license compliance checks (AGENTS.md)
#   - No validation or integrity tests
#   - Manual maintenance required for font updates
#   - Risk of inconsistency with local development setup
#
# ✅ Please migrate to:
#   - Dockerfile.dynamic (recommended, smart configuration)
#   - Dockerfile.python (for lightweight Python tests only)
#
# 📚 Migration Guide: 
#   See DOCKERFILE_STRATEGY.md for detailed instructions
#
# 🏷️  Docker Tag (deprecated): erda-workflow-tools:latest
# =============================================================================

# Python testing stage
FROM python:3.12-slim AS python-test

ENV PYTHONUNBUFFERED=1
ENV GITHUB_TOOLS=/workspace/.github/gitbook_worker/tools
VOLUME [ "/workspace" ]

# Install minimal required packages
RUN apt-get update && apt-get install -y \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install test requirements
RUN pip3 install --no-cache-dir pytest pytest-cov black

WORKDIR /workspace

# Publishing stage
FROM ubuntu:22.04 AS publisher

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV GITHUB_TOOLS=/workspace/.github/gitbook_worker/tools
VOLUME [ "/workspace" ]
# Install required packages
RUN apt-get update && apt-get install -y \
    pandoc \
    texlive-full \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-xetex \
    texlive-luatex \
    texlive-lang-german \
    lmodern \
    cm-super \
    texlive-science \
    texlive-lang-all \
    python3 \
    python3-pip \
    python3-venv \
    git \
    make \
    wget \
    curl \
    fonts-dejavu \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure TeX for better nesting and Unicode support
RUN mkdir -p /app/texmf/tex/latex/local && \
    mkdir -p /app/.local/share/pandoc/filters && \
    mkdir -p /app/.pandoc/templates

# Install Twemoji font (CC BY 4.0 - as required by AGENTS.md)
# Download Twemoji font from official GitHub repository since fonts-twemoji package doesn't exist in Ubuntu 22.04
RUN mkdir -p /usr/share/fonts/truetype/twemoji && \
    wget -O /tmp/twemoji-linux.tar.gz \
    https://github.com/13rac1/twemoji-color-font/releases/download/v15.1.0/TwitterColorEmoji-SVGinOT-Linux-15.1.0.tar.gz && \
    echo "c8a5302ee4e4c2188ce785edd84c50c616a07f6e99fe1b91aecba4e1db341295  /tmp/twemoji-linux.tar.gz" | sha256sum -c - && \
    tar -xzf /tmp/twemoji-linux.tar.gz -C /tmp && \
    test -f /tmp/TwitterColorEmoji-SVGinOT-Linux-15.1.0/TwitterColorEmoji-SVGinOT.ttf && \
    cp /tmp/TwitterColorEmoji-SVGinOT-Linux-15.1.0/TwitterColorEmoji-SVGinOT.ttf \
    /usr/share/fonts/truetype/twemoji/ && \
    rm -rf /tmp/twemoji-linux.tar.gz /tmp/TwitterColorEmoji-SVGinOT-Linux-15.1.0

# Install additional fonts for better Unicode support
RUN apt-get update && apt-get install -y \
    fonts-symbola \
    fonts-liberation \
    fonts-freefont-ttf \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Update font cache
RUN fc-cache -f -v

# Set up LaTeX configuration for better Unicode and emoji support
COPY .github/gitbook_worker/tools/publishing/texmf/ /app/texmf

# Set up pandoc template for LuaLaTeX with full document structure
RUN mkdir -p /root/.pandoc/templates && \
    echo '\documentclass[$if(fontsize)$$fontsize$,$endif$$if(lang)$$lang$,$endif$$if(papersize)$$papersize$,$endif$$for(classoption)$$classoption$$sep$,$endfor$]{$documentclass$}' > /root/.pandoc/templates/default.latex && \
    echo '\usepackage{fontspec}' >> /root/.pandoc/templates/default.latex && \
    echo '\usepackage{polyglossia}' >> /root/.pandoc/templates/default.latex && \
    echo '\setmainlanguage{german}' >> /root/.pandoc/templates/default.latex && \
    echo '\setotherlanguage{english}' >> /root/.pandoc/templates/default.latex && \
    echo '\usepackage{xcolor}' >> /root/.pandoc/templates/default.latex && \
    echo '\usepackage{enumitem}' >> /root/.pandoc/templates/default.latex && \
    echo '\usepackage{amssymb}' >> /root/.pandoc/templates/default.latex && \
    echo '\usepackage{hyperref}' >> /root/.pandoc/templates/default.latex && \
    echo '\usepackage{booktabs}' >> /root/.pandoc/templates/default.latex && \
    echo '\usepackage{longtable}' >> /root/.pandoc/templates/default.latex && \
    echo '\usepackage[$for(geometry)$$geometry$$sep$,$endfor$]{geometry}' >> /root/.pandoc/templates/default.latex && \
    echo '$if(mainfont)$\setmainfont{$mainfont$}$endif$' >> /root/.pandoc/templates/default.latex && \
    echo '$if(sansfont)$\setsansfont{$sansfont$}$endif$' >> /root/.pandoc/templates/default.latex && \
    echo '$if(monofont)$\setmonofont{$monofont$}$endif$' >> /root/.pandoc/templates/default.latex && \
    echo '\begin{document}' >> /root/.pandoc/templates/default.latex && \
    echo '$if(title)$\title{$title$}$endif$' >> /root/.pandoc/templates/default.latex && \
    echo '$if(author)$\author{$author$}$endif$' >> /root/.pandoc/templates/default.latex && \
    echo '$if(date)$\date{$date$}$endif$' >> /root/.pandoc/templates/default.latex && \
    echo '$if(title)$\maketitle$endif$' >> /root/.pandoc/templates/default.latex && \
    echo '$if(toc)$\tableofcontents$endif$' >> /root/.pandoc/templates/default.latex && \
    echo '$body$' >> /root/.pandoc/templates/default.latex && \
    echo '\end{document}' >> /root/.pandoc/templates/default.latex

# Setup latex-emoji filter and copy it to the right location during container run
RUN mkdir -p /root/.local/share/pandoc/filters


# Create an entrypoint script to setup paths and filters
RUN echo '#!/bin/bash\n\
    export TEXMFHOME=$GITHUB_TOOLS/publishing/texmf\n\
    export LUA_PATH="$GITHUB_TOOLS/publishing/lua/?.lua;;"\n\
    export PYTHONPATH="/workspace/.github/gitbook_worker:$PYTHONPATH"\n\
    exec "$@"' > /usr/local/bin/docker-entrypoint.sh && \
    chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["sleep", "infinity"]

# Create and activate virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install test requirements
RUN pip3 install --no-cache-dir pytest pytest-cov

# Copy requirements.txt for installation during build
COPY .github/gitbook_worker/tools/requirements.txt /tmp/requirements.txt

# Install project requirements during build
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

WORKDIR /workspace
