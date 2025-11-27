# Docker Documentation

Comprehensive documentation for Docker-related tools and workflows in the GitBook Worker package.

## 📑 Overview

This directory contains all Docker-specific documentation, organized by topic:

### Core Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| **[DOCKERFILE_STRATEGY.md](DOCKERFILE_STRATEGY.md)** | Docker image strategy, architecture, and best practices | DevOps, Developers |
| **[LOGGING_STRATEGY.md](LOGGING_STRATEGY.md)** | External log volume architecture and implementation | Developers, Troubleshooters |
| **[DEBUGGING.md](DEBUGGING.md)** | Debugging guide and diagnostics tools usage | Developers, Troubleshooters |
| **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** | Technical implementation summary | Developers |

## 🎯 Quick Start

### New to Docker Workflows?
1. Start with **[DOCKERFILE_STRATEGY.md](DOCKERFILE_STRATEGY.md)** to understand our Docker image approach
2. Learn about logging in **[LOGGING_STRATEGY.md](LOGGING_STRATEGY.md)**
3. Use **[DEBUGGING.md](DEBUGGING.md)** when you encounter issues

### Troubleshooting?
→ Go directly to **[DEBUGGING.md](DEBUGGING.md)**

### Implementing Docker Features?
→ Check **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)**

## 📚 Document Details

### DOCKERFILE_STRATEGY.md
**Purpose:** Explains our multi-Dockerfile approach

**Key Topics:**
- Dockerfile.dynamic (recommended) - Smart configuration
- Dockerfile.python (lightweight) - Fast tests
- Dockerfile (deprecated) - Legacy support
- Decision matrix and migration guide

**When to read:**
- Setting up Docker images
- Choosing between Dockerfile variants
- Understanding font configuration
- CI/CD integration

### LOGGING_STRATEGY.md
**Purpose:** Architecture for external log volumes

**Key Topics:**
- External log directory (`DOCKER_LOG_DIR`)
- Volume mounting strategy
- Environment variables
- Log persistence outside containers

**When to read:**
- Logs disappear in Docker
- Debugging Docker orchestrator runs
- Setting up logging infrastructure

### DEBUGGING.md
**Purpose:** Practical debugging guide

**Key Topics:**
- Docker diagnostics tool usage
- File state tracking
- Git status change detection
- Troubleshooting workflows

**When to read:**
- Files marked as "to be deleted" after Docker runs
- Need to track file changes
- Investigating permission issues
- Debugging orchestrator problems

### IMPLEMENTATION_SUMMARY.md
**Purpose:** Technical implementation details

**Key Topics:**
- Code changes summary
- File structure
- Environment variables
- Commit message templates

**When to read:**
- Understanding implementation details
- Contributing to the project
- Reviewing changes

## 🔧 Related Tools

These documents describe tools located in:
- `../../tools/docker/` - Python modules (docker_diagnostics.py, etc.)
- `../../scripts/` - Wrapper scripts (run-in-docker.ps1, diagnose-docker.ps1)

See `../../tools/docker/readme.md` for tool-specific documentation.

## 🏗️ Architecture Overview

```
GitBook Worker Docker Architecture
│
├─ Docker Images
│  ├─ Dockerfile.dynamic (recommended)
│  ├─ Dockerfile.python (lightweight)
│  └─ Dockerfile (deprecated)
│
├─ Logging System
│  ├─ External volume: .docker-logs/
│  ├─ Environment: DOCKER_LOG_DIR
│  └─ logging_config.py integration
│
└─ Diagnostics
   ├─ docker_diagnostics.py (file tracking)
   └─ diagnose-docker.ps1 (automated workflow)
```

## 📖 Reading Order

For comprehensive understanding, read in this order:

1. **DOCKERFILE_STRATEGY.md** - Understand our Docker approach
2. **LOGGING_STRATEGY.md** - Learn about logging architecture
3. **DEBUGGING.md** - Know how to troubleshoot
4. **IMPLEMENTATION_SUMMARY.md** - Review implementation details

## 🚀 Common Workflows

### Running with Logging
```powershell
cd .github/gitbook_worker/scripts
.\run-in-docker.ps1 orchestrator -Profile local
# Logs available in: .docker-logs/workflow.log
```

### Debugging File Issues
```powershell
cd .github/gitbook_worker/scripts
.\diagnose-docker.ps1 -Profile local
# Creates analysis in: .docker-logs/analysis.json
```

### Building Docker Images
```powershell
# Recommended: Dynamic configuration
docker build -f .github/gitbook_worker/tools/docker/Dockerfile.dynamic \
             -t erda-smart-worker:latest .

# Lightweight: For tests only
docker build -f .github/gitbook_worker/tools/docker/Dockerfile.python \
             -t erda-test-worker:latest .
```

## 🔗 Cross-References

- **Main README**: `../../README.md` - GitBook Worker overview
- **Tools README**: `../../tools/docker/readme.md` - Tool-specific docs
- **Scripts**: `../../scripts/` - Executable wrappers

## 📝 Contributing

When adding Docker documentation:

1. ✅ Place files in this `docs/docker/` directory
2. ✅ Update this README.md with links
3. ✅ Follow naming conventions:
   - UPPERCASE for major strategy docs
   - descriptive-name.md for guides
4. ✅ Include cross-references to related tools/scripts
5. ✅ Sign your documentation with DCO

## 📄 License

- **Documentation**: CC BY-SA 4.0
- **Code examples**: MIT

## 🏷️ Document Index

Quick alphabetical reference:

- **DEBUGGING.md** - Troubleshooting and diagnostics
- **DOCKERFILE_STRATEGY.md** - Image architecture and strategy
- **IMPLEMENTATION_SUMMARY.md** - Technical implementation
- **LOGGING_STRATEGY.md** - External log volumes
- **README.md** - This file (index)

---

**Last Updated:** November 2025  
**Maintainer:** ERDA GitBook Worker Team  
**Status:** Active

Signed-off-by: ERDA GitBook Worker Team <team@erda-project.org>
