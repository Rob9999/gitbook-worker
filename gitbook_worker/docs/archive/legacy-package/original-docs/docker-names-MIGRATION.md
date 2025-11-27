# Migration Guide: From Hardcoded to Configurable Docker Names

This guide shows how to migrate from hardcoded Docker image and container names to the new configurable smart merge system.

## Overview

**Before:** Docker names were hardcoded in tests, scripts, and workflows
**After:** Docker names are configured in YAML files with template support

## Benefits of Migration

1. **Consistency**: All Docker names follow the same convention
2. **Flexibility**: Easy to override names per environment or publish entry
3. **No conflicts**: Different contexts use different naming patterns
4. **Maintainability**: Change naming scheme in one place

## Step-by-Step Migration

### 1. Identify Hardcoded Names

Search for hardcoded Docker names in your codebase:

```bash
# Find hardcoded image names
grep -r "sphere-space-tests" .
grep -r "docker run --name" .
grep -r "docker build -t" .
```

Common locations:
- Test files (`tests/*.py`)
- GitHub Actions (`.github/workflows/*.yml`)
- Build scripts (`build*.sh`, `build*.ps1`)
- Python utilities (`.github/gitbook_worker/tools/**/*.py`)

### 2. Review Default Configuration

Check the default naming scheme in `.github/gitbook_worker/defaults/docker_config.yml`:

```yaml
docker_names:
  test:
    image: "erda-gitbook-test:local"
    container: "erda-test-{publish_name}"
  
  docker-test:
    image: "erda-gitbook-dockertest:latest"
    container: "erda-dockertest-{publish_name}"
```

### 3. Decide on Naming Strategy

Option A: **Use Defaults** (recommended for most cases)
- No changes needed to config files
- Just update code to use CLI/API

Option B: **Custom Naming** (if you need specific names)
- Create `docker_config.yml` in repo root
- Override specific contexts

Example custom config (`docker_config.yml`):

```yaml
docker_names:
  docker-test:
    # Keep your existing naming for compatibility
    image: "sphere-space-tests"
    container: "sphere-space-tests-container"
```

### 4. Update Test Files

#### Before (Hardcoded)

```python
# tests/test_space.py
import subprocess

def test_sphere_space_build():
    # Hardcoded names
    image = "sphere-space-tests"
    container = "sphere-space-tests-container"
    
    subprocess.run(["docker", "build", "-t", image, "."], check=True)
    subprocess.run(["docker", "run", "--name", container, image], check=True)
```

#### After (Configurable)

```python
# tests/test_space.py
import subprocess
import sys
from pathlib import Path

# Add .github to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".github"))

from gitbook_worker_tools import smart_merge

def test_sphere_space_build():
    # Get names from configuration
    repo_root = Path(__file__).parent.parent
    names = smart_merge.get_all_docker_names(
        repo_root=repo_root,
        publish_name="space-tests",
        context="docker-test"
    )
    
    image = names["image"]
    container = names["container"]
    
    subprocess.run(["docker", "build", "-t", image, "."], check=True)
    subprocess.run(["docker", "run", "--name", container, image], check=True)
```

#### Alternative: Using CLI in Shell Commands

```python
def test_sphere_space_build():
    """Test using CLI to get names."""
    import json
    
    # Get names via CLI
    result = subprocess.run(
        ["python", "-m", "gitbook_worker_tools.cli", "get-all-names",
         "--context", "docker-test", "--publish-name", "space-tests"],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "PYTHONPATH": str(Path(__file__).parent.parent / ".github")}
    )
    
    names = json.loads(result.stdout)
    image = names["image"]
    container = names["container"]
    
    # ... rest of test
```

### 5. Update Pytest Fixtures

Create a shared fixture in `conftest.py`:

```python
# tests/conftest.py
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / ".github"))

from gitbook_worker_tools import smart_merge

@pytest.fixture
def docker_names():
    """Get docker names for any context and publish name."""
    def _get_names(context="test", publish_name="test"):
        repo_root = Path(__file__).parent.parent
        return smart_merge.get_all_docker_names(
            repo_root=repo_root,
            publish_name=publish_name,
            context=context,
            extra_vars={}
        )
    return _get_names

# Use in tests
def test_example(docker_names):
    names = docker_names(context="docker-test", publish_name="space-tests")
    assert names["image"] == "erda-gitbook-dockertest:latest"
```

### 6. Update GitHub Actions Workflows

#### Before (Hardcoded)

```yaml
- name: Build Test Image
  run: docker build -t sphere-space-tests .

- name: Run Tests
  run: docker run --name sphere-space-tests-container sphere-space-tests
```

#### After (Configurable)

```yaml
- name: Install Dependencies
  run: pip install pyyaml

- name: Get Docker Names
  id: docker
  run: |
    export PYTHONPATH="${GITHUB_WORKSPACE}/.github"
    NAMES=$(python -m gitbook_worker_tools.cli get-all-names \
      --context github-action \
      --publish-name space-tests \
      --repo-name ${{ github.repository }} \
      --branch ${{ github.ref_name }})
    
    echo "image=$(echo "$NAMES" | jq -r '.image')" >> $GITHUB_OUTPUT
    echo "container=$(echo "$NAMES" | jq -r '.container')" >> $GITHUB_OUTPUT

- name: Build Test Image
  run: docker build -t ${{ steps.docker.outputs.image }} .

- name: Run Tests
  run: docker run --name ${{ steps.docker.outputs.container }} \
    ${{ steps.docker.outputs.image }}
```

### 7. Update Build Scripts

#### Bash Script (before)

```bash
#!/bin/bash
IMAGE="sphere-space-tests"
CONTAINER="sphere-space-tests-container"

docker build -t "$IMAGE" .
docker run --name "$CONTAINER" "$IMAGE"
```

#### Bash Script (after)

```bash
#!/bin/bash
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${REPO_ROOT}/.github"

# Get names from config
NAMES=$(python -m gitbook_worker_tools.cli get-all-names \
  --context docker-test \
  --publish-name space-tests)

IMAGE=$(echo "$NAMES" | jq -r '.image')
CONTAINER=$(echo "$NAMES" | jq -r '.container')

docker build -t "$IMAGE" .
docker run --name "$CONTAINER" "$IMAGE"
```

Or use the wrapper script:

```bash
#!/bin/bash
NAMES=$(./docker-names.sh get-all-names \
  --context docker-test \
  --publish-name space-tests)

IMAGE=$(echo "$NAMES" | jq -r '.image')
CONTAINER=$(echo "$NAMES" | jq -r '.container')

docker build -t "$IMAGE" .
docker run --name "$CONTAINER" "$IMAGE"
```

### 8. Update Python Utilities

#### Before (Hardcoded in docker_runner.py)

```python
class DockerRunner:
    def __init__(self):
        self.image = "sphere-space-tests"
        self.container = "sphere-space-tests-container"
```

#### After (Configurable)

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / ".github"))

from gitbook_worker_tools import smart_merge

class DockerRunner:
    def __init__(self, context="test", publish_name=None):
        self.context = context
        self.publish_name = publish_name
        self.repo_root = self._find_repo_root()
        self._names = None
    
    def _find_repo_root(self):
        current = Path(__file__).parent
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    @property
    def names(self):
        if self._names is None:
            self._names = smart_merge.get_all_docker_names(
                repo_root=self.repo_root,
                publish_name=self.publish_name,
                context=self.context
            )
        return self._names
    
    @property
    def image(self):
        return self.names["image"]
    
    @property
    def container(self):
        return self.names["container"]
```

## Common Migration Patterns

### Pattern 1: Test with Multiple Publish Entries

```python
@pytest.mark.parametrize("publish_name", ["space-tests", "civitas-tests", "main-tests"])
def test_build_for_publish(docker_names, publish_name):
    names = docker_names(context="docker-test", publish_name=publish_name)
    # ... test with names["image"] and names["container"]
```

### Pattern 2: Context-Specific Testing

```python
def test_local_build(docker_names):
    """Test with local development names."""
    names = docker_names(context="test", publish_name="dev")
    # ... local test

def test_ci_build(docker_names):
    """Test with CI/CD names."""
    names = docker_names(context="github-action", publish_name="ci-test")
    # ... CI test
```

### Pattern 3: Temporary Compatibility Layer

If you need to maintain backward compatibility:

```yaml
# docker_config.yml - Temporary compatibility
docker_names:
  docker-test:
    # Use old names temporarily
    image: "sphere-space-tests"
    container: "sphere-space-tests-container"
```

Then gradually migrate to new naming:

```yaml
# docker_config.yml - New naming
docker_names:
  docker-test:
    image: "erda-space-tests:{branch}"
    container: "space-tests-{publish_name}"
```

## Verification Checklist

After migration, verify:

- [ ] All tests pass with new naming
- [ ] GitHub Actions workflows use CLI/API
- [ ] Build scripts are updated
- [ ] No hardcoded names remain (search for old names)
- [ ] Configuration files are in place
- [ ] Documentation is updated

## Rollback Plan

If issues occur:

1. **Immediate**: Override with old names in `docker_config.yml`
2. **Revert**: Git revert migration commits
3. **Debug**: Check CLI output with `dump-config`

## Testing Migration

Test the migration step-by-step:

```bash
# 1. Verify CLI works
./docker-names.sh get-all-names --context docker-test --publish-name space-tests

# 2. Test with one file
pytest tests/test_space.py -v

# 3. Test all
pytest tests/ -v

# 4. Test workflows locally (act or manual)
act -j test
```

## Support

For issues:
1. Check `.github/gitbook_worker_tools/README.md`
2. Review `INTEGRATION.md` for examples
3. Run `dump-config` to see merged configuration
4. Check PYTHONPATH is set correctly

## License

Part of ERDA GitBook Worker toolchain.
- Code: MIT License
- Documentation: CC BY-SA 4.0
