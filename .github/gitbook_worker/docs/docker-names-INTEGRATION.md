# Integration Examples for Smart Merge Docker Names

This document shows how to integrate the smart merge configuration tool into existing tests, workflows, and scripts.

## Quick Start

### Using the Wrapper Script

```powershell
# Get image name for test context
.\docker-names.ps1 get-name --type image --context test --publish-name space-tests

# Get all names as JSON
.\docker-names.ps1 get-all-names --context docker-test --publish-name space-tests
```

### Direct Python Import

```python
import sys
from pathlib import Path

# Add .github to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / ".github"))

from gitbook_worker_tools import smart_merge

# Get names
repo_root = Path(__file__).parent.parent
names = smart_merge.get_all_docker_names(
    repo_root=repo_root,
    publish_name="space-tests",
    context="test",
    extra_vars={"branch": "main"}
)

print(f"Image: {names['image']}")
print(f"Container: {names['container']}")
```

## Integration into Existing Tests

### Pytest Fixture (conftest.py)

```python
# .github/gitbook_worker/tests/conftest.py
import pytest
import sys
from pathlib import Path

# Ensure gitbook_worker_tools is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".github"))

from gitbook_worker_tools import smart_merge

@pytest.fixture
def docker_names():
    """Provide docker names for tests."""
    def _get_names(context="test", publish_name="test-publish"):
        repo_root = Path(__file__).parent.parent.parent.parent
        return smart_merge.get_all_docker_names(
            repo_root=repo_root,
            publish_name=publish_name,
            context=context,
            extra_vars={
                "branch": "test-branch",
                "repo_name": "erda-book"
            }
        )
    return _get_names

# Usage in tests
def test_docker_build(docker_names):
    names = docker_names(context="docker-test", publish_name="space-tests")
    assert names["image"] == "erda-gitbook-dockertest:latest"
    assert names["container"] == "erda-dockertest-space-tests"
```

### Existing Test Migration

Before (hardcoded):
```python
def test_sphere_space():
    image_name = "sphere-space-tests"
    container_name = "sphere-space-tests-container"
    # ... test code
```

After (configurable):
```python
def test_sphere_space(docker_names):
    names = docker_names(context="docker-test", publish_name="space-tests")
    image_name = names["image"]
    container_name = names["container"]
    # ... test code
```

## Integration into GitHub Actions

### Basic Usage

```yaml
name: Build and Test

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyyaml
      
      - name: Get Docker Names
        id: docker
        run: |
          # Set PYTHONPATH
          export PYTHONPATH="${GITHUB_WORKSPACE}/.github"
          
          # Get image name
          IMAGE=$(python -m gitbook_worker_tools.cli get-name \
            --type image \
            --context github-action \
            --repo-name ${{ github.repository }} \
            --branch ${{ github.ref_name }} \
            --publish-name main-book)
          
          # Get container name
          CONTAINER=$(python -m gitbook_worker_tools.cli get-name \
            --type container \
            --context github-action \
            --publish-name main-book)
          
          # Export to GitHub outputs
          echo "image=$IMAGE" >> $GITHUB_OUTPUT
          echo "container=$CONTAINER" >> $GITHUB_OUTPUT
      
      - name: Build Docker Image
        run: |
          docker build -t ${{ steps.docker.outputs.image }} .
      
      - name: Run Container
        run: |
          docker run --name ${{ steps.docker.outputs.container }} \
            ${{ steps.docker.outputs.image }}
```

### Using JSON Output

```yaml
      - name: Get All Docker Names
        id: docker
        run: |
          export PYTHONPATH="${GITHUB_WORKSPACE}/.github"
          
          # Get all names as JSON
          NAMES=$(python -m gitbook_worker_tools.cli get-all-names \
            --context github-action \
            --repo-name ${{ github.repository }} \
            --branch ${{ github.ref_name }} \
            --publish-name main-book)
          
          # Parse JSON
          IMAGE=$(echo "$NAMES" | jq -r '.image')
          CONTAINER=$(echo "$NAMES" | jq -r '.container')
          
          echo "image=$IMAGE" >> $GITHUB_OUTPUT
          echo "container=$CONTAINER" >> $GITHUB_OUTPUT
```

### Matrix Strategy

```yaml
jobs:
  test:
    strategy:
      matrix:
        publish: [main-book, space-book, civitas-book]
    
    steps:
      - name: Get Docker Names for ${{ matrix.publish }}
        id: docker
        run: |
          export PYTHONPATH="${GITHUB_WORKSPACE}/.github"
          python -m gitbook_worker_tools.cli get-all-names \
            --context github-action \
            --publish-name ${{ matrix.publish }} \
            --repo-name ${{ github.repository }} \
            --branch ${{ github.ref_name }} \
            > names.json
          
          echo "image=$(jq -r '.image' names.json)" >> $GITHUB_OUTPUT
          echo "container=$(jq -r '.container' names.json)" >> $GITHUB_OUTPUT
```

## Integration into Local Scripts

### Bash Script

```bash
#!/bin/bash
# build-and-test.sh

set -e

# Get repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${REPO_ROOT}/.github"

# Get docker names
NAMES=$(python -m gitbook_worker_tools.cli get-all-names \
  --context test \
  --publish-name space-tests \
  --branch "$(git branch --show-current)")

IMAGE=$(echo "$NAMES" | jq -r '.image')
CONTAINER=$(echo "$NAMES" | jq -r '.container')

echo "Building image: $IMAGE"
docker build -t "$IMAGE" .

echo "Running container: $CONTAINER"
docker run --name "$CONTAINER" --rm "$IMAGE" pytest tests/
```

### PowerShell Script

```powershell
# build-and-test.ps1

$ErrorActionPreference = "Stop"

# Get repository root
$REPO_ROOT = Split-Path -Parent $PSCommandPath
$env:PYTHONPATH = Join-Path $REPO_ROOT ".github"

# Get branch name
$BRANCH = git branch --show-current

# Get docker names
$NAMES_JSON = python -m gitbook_worker_tools.cli get-all-names `
  --context test `
  --publish-name space-tests `
  --branch $BRANCH | ConvertFrom-Json

$IMAGE = $NAMES_JSON.image
$CONTAINER = $NAMES_JSON.container

Write-Host "Building image: $IMAGE"
docker build -t $IMAGE .

Write-Host "Running container: $CONTAINER"
docker run --name $CONTAINER --rm $IMAGE pytest tests/
```

## Integration into Python Utilities

### Docker Runner Utility

```python
# .github/gitbook_worker/tools/utils/docker_runner.py
import sys
from pathlib import Path

# Add to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / ".github"))

from gitbook_worker_tools import smart_merge

class DockerRunner:
    def __init__(self, context="test", publish_name=None):
        self.context = context
        self.publish_name = publish_name
        self.repo_root = Path(__file__).parent.parent.parent.parent.parent
    
    def get_names(self, extra_vars=None):
        """Get docker names from configuration."""
        return smart_merge.get_all_docker_names(
            repo_root=self.repo_root,
            publish_name=self.publish_name,
            context=self.context,
            extra_vars=extra_vars or {}
        )
    
    def build_image(self, dockerfile="Dockerfile", build_args=None):
        """Build docker image with configured name."""
        names = self.get_names()
        image = names["image"]
        
        cmd = ["docker", "build", "-t", image, "-f", dockerfile]
        if build_args:
            for key, value in build_args.items():
                cmd.extend(["--build-arg", f"{key}={value}"])
        cmd.append(".")
        
        subprocess.run(cmd, check=True)
        return image
    
    def run_container(self, command=None, volumes=None, remove=True):
        """Run container with configured name."""
        names = self.get_names()
        container = names["container"]
        image = names["image"]
        
        cmd = ["docker", "run", "--name", container]
        if remove:
            cmd.append("--rm")
        if volumes:
            for vol in volumes:
                cmd.extend(["-v", vol])
        cmd.append(image)
        if command:
            cmd.extend(command)
        
        subprocess.run(cmd, check=True)
        return container

# Usage
if __name__ == "__main__":
    runner = DockerRunner(context="test", publish_name="space-tests")
    runner.build_image(dockerfile="Dockerfile.python")
    runner.run_container(command=["pytest", "tests/", "-v"])
```

## Custom Configuration Examples

### Override for Specific Tests

Create `docker_config.yml` in repo root:

```yaml
docker_names:
  # Custom naming for local development
  test:
    image: "my-dev-test:{branch}"
    container: "dev-test-{publish_name}"
  
  # Docker-based tests with specific naming
  docker-test:
    image: "integration-tests:latest"
    container: "integration-{publish_name}-{branch}"
```

### Per-Publish Configuration

In `publish.yml`:

```yaml
# Global docker config
docker_config:
  docker_names:
    prod:
      image: "erda-prod:v{version}"

# Per-publish overrides
publish:
  - name: "space-book"
    output: "space.pdf"
    docker_config:
      docker_names:
        docker-test:
          image: "space-test-image:latest"
          container: "space-tests-{branch}"
  
  - name: "civitas-book"
    output: "civitas.pdf"
    docker_config:
      docker_names:
        docker-test:
          image: "civitas-test-image:latest"
          container: "civitas-tests-{branch}"
```

## Troubleshooting

### PYTHONPATH Issues

If imports fail, ensure PYTHONPATH includes `.github`:

```bash
# Bash
export PYTHONPATH="${REPO_ROOT}/.github"

# PowerShell
$env:PYTHONPATH = "C:\path\to\repo\.github"

# Python
sys.path.insert(0, str(Path(__file__).parent / ".github"))
```

### Missing YAML Dependency

Install PyYAML if not present:

```bash
pip install pyyaml
```

### Template Variable Errors

If you see "Missing template variable", ensure all required variables are provided:

```bash
# Bad - missing branch
python -m gitbook_worker_tools.cli get-name --type image --context default

# Good - all variables provided
python -m gitbook_worker_tools.cli get-name --type image --context default \
  --branch main --publish-name test
```

## License

Part of ERDA GitBook Worker toolchain.
- Code: MIT License
- Documentation: CC BY-SA 4.0
