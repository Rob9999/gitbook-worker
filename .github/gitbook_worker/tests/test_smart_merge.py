"""Unit tests for smart_merge module.

Tests configuration merging, templating, and CLI functionality.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from gitbook_worker.tools.docker import smart_merge


@pytest.fixture
def temp_repo(tmp_path):
    """Create temporary repository structure with config files."""
    repo_root = tmp_path / "test_repo"
    repo_root.mkdir()

    # Create .github structure
    defaults_dir = repo_root / ".github" / "gitbook_worker" / "defaults"
    defaults_dir.mkdir(parents=True)

    # Create default config
    default_config = {
        "docker_names": {
            "default": {
                "image": "default-image:{branch}",
                "container": "default-container-{publish_name}",
            },
            "test": {
                "image": "test-image:local",
                "container": "test-container-{publish_name}",
            },
        }
    }
    with open(defaults_dir / "docker_config.yml", "w") as f:
        yaml.dump(default_config, f)

    return repo_root


def test_deep_merge():
    """Test deep dictionary merging."""
    base = {"a": 1, "b": {"c": 2, "d": 3}, "e": 5}
    overlay = {"b": {"d": 4, "f": 6}, "g": 7}

    result = smart_merge.deep_merge(base, overlay)

    assert result["a"] == 1
    assert result["b"]["c"] == 2
    assert result["b"]["d"] == 4  # Overridden
    assert result["b"]["f"] == 6  # Added
    assert result["e"] == 5
    assert result["g"] == 7


def test_load_yaml_safe(temp_repo):
    """Test YAML loading with error handling."""
    # Existing file
    config_path = (
        temp_repo / ".github" / "gitbook_worker" / "defaults" / "docker_config.yml"
    )
    result = smart_merge.load_yaml_safe(config_path)
    assert result is not None
    assert "docker_names" in result

    # Non-existent file
    result = smart_merge.load_yaml_safe(temp_repo / "nonexistent.yml")
    assert result is None


def test_merge_configs_defaults_only(temp_repo):
    """Test config merging with only defaults."""
    config = smart_merge.merge_configs(temp_repo)

    assert "docker_names" in config
    assert "default" in config["docker_names"]
    assert "test" in config["docker_names"]


def test_merge_configs_with_overrides(temp_repo):
    """Test config merging with repository overrides."""
    # Add docker_config.yml in repo root
    repo_config = {"docker_names": {"test": {"image": "custom-test-image:latest"}}}
    with open(temp_repo / "docker_config.yml", "w") as f:
        yaml.dump(repo_config, f)

    config = smart_merge.merge_configs(temp_repo)

    # Test override applied
    assert config["docker_names"]["test"]["image"] == "custom-test-image:latest"
    # Container name should still be from defaults
    assert "container" in config["docker_names"]["test"]


def test_merge_configs_with_publish_yml(temp_repo):
    """Test config merging with publish.yml overrides."""
    # Create publish.yml
    publish_config = {
        "docker_config": {
            "docker_names": {
                "prod": {"image": "prod-image:v1.0", "container": "prod-container"}
            }
        },
        "publish": [
            {
                "name": "main-book",
                "output": "main.pdf",
                "docker_config": {
                    "docker_names": {"test": {"image": "main-book-test:local"}}
                },
            },
            {"name": "space-book", "output": "space.pdf"},
        ],
    }
    with open(temp_repo / "publish.yml", "w") as f:
        yaml.dump(publish_config, f)

    # Merge without specific publish name
    config = smart_merge.merge_configs(temp_repo)
    assert config["docker_names"]["prod"]["image"] == "prod-image:v1.0"

    # Merge with specific publish name
    config = smart_merge.merge_configs(temp_repo, publish_name="main-book")
    assert config["docker_names"]["test"]["image"] == "main-book-test:local"


def test_render_template():
    """Test template rendering."""
    template = "image-{context}:{branch}-{version}"
    variables = {"context": "test", "branch": "main", "version": "1.0.0"}

    result = smart_merge.render_template(template, variables)
    assert result == "image-test:main-1.0.0"


def test_render_template_missing_variable():
    """Test template rendering with missing variable."""
    template = "image-{context}:{missing}"
    variables = {"context": "test"}

    with pytest.raises(ValueError, match="Missing template variable"):
        smart_merge.render_template(template, variables)


def test_get_docker_name(temp_repo):
    """Test getting docker name from config."""
    config = smart_merge.merge_configs(temp_repo)

    extra_vars = {"branch": "main", "publish_name": "test-book"}

    # Get image name
    image = smart_merge.get_docker_name(config, "image", "test", extra_vars)
    assert image == "test-image:local"

    # Get container name
    container = smart_merge.get_docker_name(config, "container", "test", extra_vars)
    assert container == "test-container-test-book"


def test_get_docker_name_fallback_to_default(temp_repo):
    """Test fallback to default context when specific context not found."""
    config = smart_merge.merge_configs(temp_repo)

    extra_vars = {"branch": "feature-x", "publish_name": "custom-book"}

    # Get name for non-existent context (should fall back to default)
    image = smart_merge.get_docker_name(config, "image", "custom-context", extra_vars)
    assert image == "default-image:feature-x"


def test_get_all_docker_names(temp_repo):
    """Test getting all docker names at once."""
    extra_vars = {"branch": "main", "publish_name": "my-book"}

    names = smart_merge.get_all_docker_names(
        temp_repo, context="test", extra_vars=extra_vars
    )

    assert "image" in names
    assert "container" in names
    assert names["image"] == "test-image:local"
    assert names["container"] == "test-container-my-book"


def test_get_docker_name_no_config():
    """Test error when docker_names section missing."""
    config = {}

    with pytest.raises(ValueError, match="No docker_names section"):
        smart_merge.get_docker_name(config, "image", "test")


def test_get_docker_name_no_template():
    """Test error when template not found."""
    config = {"docker_names": {"default": {"image": "default-image"}}}

    # Try to get container (which doesn't exist in config)
    with pytest.raises(ValueError, match="No container template found"):
        smart_merge.get_docker_name(config, "container", "test")


def test_complex_layering(temp_repo):
    """Test complex multi-layer configuration merging."""
    # Layer 2: Repository config
    repo_config = {
        "docker_names": {
            "test": {"image": "repo-test-image:{branch}"},
            "staging": {
                "image": "staging-image:latest",
                "container": "staging-container",
            },
        }
    }
    with open(temp_repo / "docker_config.yml", "w") as f:
        yaml.dump(repo_config, f)

    # Layer 3 & 4: publish.yml
    publish_config = {
        "docker_config": {"docker_names": {"prod": {"image": "general-prod:v1"}}},
        "publish": [
            {
                "name": "special-book",
                "docker_config": {
                    "docker_names": {
                        "test": {"container": "special-test-container"},
                        "prod": {"image": "special-prod:v2"},
                    }
                },
            }
        ],
    }
    with open(temp_repo / "publish.yml", "w") as f:
        yaml.dump(publish_config, f)

    # Merge for special-book
    config = smart_merge.merge_configs(temp_repo, publish_name="special-book")

    # Layer 1 default (container for test) should be overridden by layer 4
    extra_vars = {"branch": "main", "publish_name": "special-book"}

    # Image from layer 2
    test_image = smart_merge.get_docker_name(config, "image", "test", extra_vars)
    assert test_image == "repo-test-image:main"

    # Container from layer 4
    test_container = smart_merge.get_docker_name(
        config, "container", "test", extra_vars
    )
    assert test_container == "special-test-container"

    # Prod image from layer 4 (overrides layer 3)
    prod_image = smart_merge.get_docker_name(config, "image", "prod", extra_vars)
    assert prod_image == "special-prod:v2"

    # Staging from layer 2
    staging_image = smart_merge.get_docker_name(config, "image", "staging", extra_vars)
    assert staging_image == "staging-image:latest"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
