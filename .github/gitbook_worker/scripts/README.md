# Build Scripts

This directory contains build and utility scripts for the ERDA publishing pipeline.

## PDF Build Scripts

### `build-pdf.ps1` (PowerShell)

Modern PowerShell script for building ERDA PDF with full control over the workflow orchestrator.

**Usage:**

```powershell
# Default build (local profile)
.\build-pdf.ps1

# Specify profile
.\build-pdf.ps1 -WorkflowProfile default

# Dry-run
.\build-pdf.ps1 -DryRun

# Custom manifest
.\build-pdf.ps1 -Manifest custom-publish.yml

# Combine options
.\build-pdf.ps1 -WorkflowProfile publisher -DryRun
```

**Parameters:**

- `-WorkflowProfile <string>` - Workflow profile to use
  - `local` (default): Converter + Publisher only
  - `default`: Full pipeline with quality checks
  - `publisher`: Publisher step only
- `-Manifest <string>` - Path to publish.yml manifest (default: `publish.yml`)
- `-DryRun` - Show what would be executed without running

**Features:**

- ✅ Colored output (Cyan/Green/Red/Yellow)
- ✅ Shows PDF file size and creation time
- ✅ Automatic PYTHONPATH configuration
- ✅ Detailed error messages with log hints
- ✅ Exit codes match build status

---

### `build-pdf.sh` (Bash)

Equivalent Bash script for Linux/macOS with same functionality as PowerShell version.

**Usage:**

```bash
# Default build (local profile)
./build-pdf.sh

# Specify profile
./build-pdf.sh --profile default

# Dry-run
./build-pdf.sh --dry-run

# Custom manifest
./build-pdf.sh --manifest custom-publish.yml

# Combine options
./build-pdf.sh --profile publisher --dry-run

# Show help
./build-pdf.sh --help
```

**Options:**

- `-p, --profile <profile>` - Workflow profile (default, local, publisher)
- `-m, --manifest <file>` - Path to publish.yml manifest
- `-d, --dry-run` - Perform dry-run
- `-h, --help` - Show help message

**Features:**

- ✅ POSIX-compliant (works on Linux/macOS/WSL)
- ✅ Colored output with ANSI codes
- ✅ Cross-platform file size detection
- ✅ Same user experience as PowerShell version

---

## Workflow Profiles

### `local` (Default)

Minimal profile for local development:
- ✅ Converter (Markdown preprocessing)
- ✅ Publisher (PDF generation)
- ❌ No Docker registry
- ❌ No quality checks

**Use when:**
- Local development and testing
- Quick iteration on content changes
- No Docker/network access needed

### `default`

Full production pipeline:
- ✅ Check if to publish
- ✅ Ensure README
- ✅ Update citation
- ✅ Converter
- ✅ Engineering document formatter
- ✅ Publisher
- ✅ Docker registry enabled
- ✅ Full quality checks

**Use when:**
- Production builds
- CI/CD pipelines
- Final release preparation

### `publisher`

Publisher-only profile:
- ✅ Publisher step only
- ✅ Docker registry enabled
- ❌ No preprocessing steps

**Use when:**
- Re-running PDF generation
- Content already preprocessed
- Debugging PDF output issues

---

## Backward Compatibility

Root-level wrapper scripts are provided for backward compatibility:

- **`../../build-pdf.ps1`** → Forwards to `.github/gitbook_worker/scripts/build-pdf.ps1`
- **`../../build-pdf.sh`** → Forwards to `.github/gitbook_worker/scripts/build-pdf.sh`

Old command still works:
```bash
./build-pdf.ps1  # Still works, calls new script
```

---

## Examples

### Quick Local Build

```bash
# PowerShell
.\build-pdf.ps1

# Bash
./build-pdf.sh
```

### Production Build with Full Pipeline

```bash
# PowerShell
.\build-pdf.ps1 -WorkflowProfile default

# Bash
./build-pdf.sh --profile default
```

### Test What Would Happen

```bash
# PowerShell
.\build-pdf.ps1 -DryRun

# Bash
./build-pdf.sh --dry-run
```

### Custom Manifest File

```bash
# PowerShell
.\build-pdf.ps1 -Manifest experimental-publish.yml

# Bash
./build-pdf.sh --manifest experimental-publish.yml
```

---

## Output

### Successful Build

```
================================================================
ERDA PDF Build
================================================================
Repository Root: C:\RAMProjects\ERDA
PYTHONPATH:      C:\RAMProjects\ERDA\.github
Profile:         local
Manifest:        publish.yml

Executing: python -m tools.workflow_orchestrator --root ... --profile local

[... build output ...]

================================================================
SUCCESS: PDF Build erfolgreich!
================================================================
PDF:     C:\RAMProjects\ERDA\publish\das-erda-buch.pdf
Groesse: 12.34 MB
Erstellt: 2025-11-07 14:23:45
```

### Failed Build

```
================================================================
FEHLER: PDF Build fehlgeschlagen (Exit Code: 1)
================================================================
Pruefe die Logs in: .github\logs\
```

---

## Troubleshooting

### Script Not Found

**Problem:**
```
Error: Build script not found
```

**Solution:**
Ensure you're running from repository root or `.github/gitbook_worker/scripts/` directory.

### Python Module Not Found

**Problem:**
```
ModuleNotFoundError: No module named 'tools'
```

**Solution:**
Scripts automatically set PYTHONPATH. If error persists:
```bash
export PYTHONPATH="${PWD}/.github"  # Bash
$env:PYTHONPATH = "$PWD\.github"    # PowerShell
```

### Permission Denied (Bash)

**Problem:**
```
bash: ./build-pdf.sh: Permission denied
```

**Solution:**
```bash
chmod +x .github/gitbook_worker/scripts/build-pdf.sh
./build-pdf.sh
```

---

## Environment Variables

The scripts set these automatically:

- **`PYTHONPATH`** - Set to `.github` directory
- **Working Directory** - Changed to repository root

You can override by setting before running:
```bash
export PYTHONPATH="/custom/path"
./build-pdf.sh
```

---

## See Also

- **Workflow Orchestrator:** `../tools/workflow_orchestrator/README.md`
- **Publisher:** `../tools/publishing/README.md`
- **Profiles:** `../tools/workflow_orchestrator/profiles.py`
- **Manifest Format:** `../../../publish.yml`
