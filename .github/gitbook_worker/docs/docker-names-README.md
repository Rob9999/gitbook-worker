# GitBook Worker Tools - Smart Merge

Smart merge utility for layered YAML configuration with templating support. Configurable Docker image and container naming without hardcoding.

## Configuration Layers

Configuration is merged from multiple layers (lowest to highest precedence):

1. **`.github/gitbook_worker/defaults/docker_config.yml`** - Default configuration
2. **`docker_config.yml`** (repo root) - Repository-wide overrides
3. **`publish.yml`** - `docker_config` section - General settings
4. **`publish.yml`** - Specific publish entry `docker_config` - Entry-specific overrides

## Configuration Format

```yaml
docker_names:
  default:
    image: "erda-gitbook:{branch}"
    container: "erda-gitbook-{context}-{publish_name}"
  
  github-action:
    image: "ghcr.io/{repo_name}/gitbook:{branch}"
    container: "gitbook-action-{publish_name}"
  
  prod:
    image: "erda-gitbook:latest"
    container: "erda-gitbook-prod"
  
  test:
    image: "erda-gitbook-test:local"
    container: "erda-test-{publish_name}"
  
  docker-test:
    image: "erda-gitbook-dockertest:latest"
    container: "erda-dockertest-{publish_name}"
```

### Template Variables

Available placeholders:
- `{context}` - Execution context (github-action, prod, test, docker-test)
- `{repo_name}` - Repository name
- `{branch}` - Git branch name
- `{publish_name}` - Publish entry name from publish.yml
- Any extra variables passed via `--var KEY=VALUE`

## CLI Usage

### Get Specific Name

```bash
# Get image name for test context
python -m gitbook_worker_tools.cli get-name --type image --context test

# Get container name for production
python -m gitbook_worker_tools.cli get-name --type container --context prod \
  --publish-name main-book --branch main

# Get name with custom variables
python -m gitbook_worker_tools.cli get-name --type image --context github-action \
  --repo-name Rob9999/erda-book --branch release_candidate --var version=1.0.1
```

### Get All Names (JSON)

```bash
# Get both image and container names
python -m gitbook_worker_tools.cli get-all-names --context test --publish-name main-book

# Output example:
# {
#   "image": "erda-gitbook-test:local",
#   "container": "erda-test-main-book"
# }
```

### Dump Merged Config

```bash
# Dump complete merged configuration
python -m gitbook_worker_tools.cli dump-config

# Dump for specific publish entry
python -m gitbook_worker_tools.cli dump-config --publish-name main-book
```

## Integration Examples

### GitHub Actions Workflow

```yaml
- name: Get Docker Names
  id: docker-names
  run: |
    IMAGE=$(python -m gitbook_worker_tools.cli get-name \
      --type image \
      --context github-action \
      --repo-name ${{ github.repository }} \
      --branch ${{ github.ref_name }} \
      --publish-name main-book)
    
    CONTAINER=$(python -m gitbook_worker_tools.cli get-name \
      --type container \
      --context github-action \
      --publish-name main-book)
    
    echo "image=$IMAGE" >> $GITHUB_OUTPUT
    echo "container=$CONTAINER" >> $GITHUB_OUTPUT

- name: Build and Run
  run: |
    docker build -t ${{ steps.docker-names.outputs.image }} .
    docker run --name ${{ steps.docker-names.outputs.container }} \
      ${{ steps.docker-names.outputs.image }}
```

### Local Production Build

```bash
# Get production names
IMAGE=$(python -m gitbook_worker_tools.cli get-name --type image --context prod)
CONTAINER=$(python -m gitbook_worker_tools.cli get-name --type container --context prod)

# Build and run
docker build -t "$IMAGE" .
docker run --name "$CONTAINER" "$IMAGE"
```

### Local Tests (pytest)

```python
# In conftest.py or test file
import subprocess
import json
from pathlib import Path

def get_docker_names(context="test", publish_name=None):
    """Get docker names for tests."""
    cmd = [
        "python", "-m", "gitbook_worker_tools.cli",
        "get-all-names",
        "--context", context
    ]
    if publish_name:
        cmd.extend(["--publish-name", publish_name])
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)

# Use in tests
def test_docker_build():
    names = get_docker_names(context="test", publish_name="test-book")
    image = names["image"]
    container = names["container"]
    
    # Run docker commands with these names
    subprocess.run(["docker", "build", "-t", image, "."], check=True)
    subprocess.run(["docker", "run", "--name", container, image], check=True)
```

### Docker-based Tests

```bash
# In test script
NAMES=$(python -m gitbook_worker_tools.cli get-all-names \
  --context docker-test \
  --publish-name space-tests)

IMAGE=$(echo "$NAMES" | jq -r '.image')
CONTAINER=$(echo "$NAMES" | jq -r '.container')

# Build test image
docker build -f Dockerfile.python -t "$IMAGE" .

# Run tests in container
docker run --name "$CONTAINER" \
  -v "$(pwd):/workspace" \
  "$IMAGE" \
  pytest tests/ -v
```

## Python API

```python
from pathlib import Path
from gitbook_worker_tools import smart_merge

# Get repository root
repo_root = Path("/path/to/repo")

# Merge all configuration layers
config = smart_merge.merge_configs(
    repo_root=repo_root,
    publish_name="main-book",
    extra_vars={"branch": "main", "version": "1.0.0"}
)

# Get specific name
image_name = smart_merge.get_docker_name(
    config=config,
    name_type="image",
    context="test",
    extra_vars={"branch": "main"}
)

# Get all names at once
names = smart_merge.get_all_docker_names(
    repo_root=repo_root,
    publish_name="main-book",
    context="prod",
    extra_vars={"branch": "main"}
)
print(f"Image: {names['image']}")
print(f"Container: {names['container']}")
```

## Default Configuration Example

Create `.github/gitbook_worker/defaults/docker_config.yml`:

```yaml
docker_names:
  default:
    image: "erda-gitbook-{context}:{branch}"
    container: "erda-{context}-{publish_name}"
  
  github-action:
    image: "ghcr.io/{repo_name}/gitbook:{branch}"
    container: "gitbook-ci-{publish_name}"
  
  prod:
    image: "erda-gitbook:latest"
    container: "erda-gitbook-prod"
  
  test:
    image: "erda-gitbook-test:local"
    container: "erda-test-{publish_name}"
  
  docker-test:
    image: "erda-gitbook-dockertest:latest"
    container: "erda-dockertest-{publish_name}"
```

## Override Examples

### Repository-wide Override (`docker_config.yml`)

```yaml
docker_names:
  test:
    # Use different naming scheme for tests
    image: "my-custom-test-image:{branch}"
    container: "my-test-container-{publish_name}"
```

### Publish Entry Override (`publish.yml`)

```yaml
# General docker config (applies to all publish entries)
docker_config:
  docker_names:
    prod:
      image: "erda-production:v{version}"

# Specific publish entry
publish:
  - name: "space-book"
    output: "space.pdf"
    docker_config:
      docker_names:
        test:
          # Override only for this publish entry
          image: "erda-space-test:latest"
          container: "space-tests-{branch}"
```

## License

Part of the ERDA GitBook Worker toolchain.
- Code: MIT License
- Documentation: CC BY-SA 4.0
