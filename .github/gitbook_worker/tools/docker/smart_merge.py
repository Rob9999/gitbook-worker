"""Smart merge module for layered YAML configuration with templating.

Layers (in precedence order, lowest to highest):
1. .github/gitbook_worker/defaults/docker_config.yml
2. docker_config.yml (repo root)
3. publish.yml - general section (repo root)
4. publish.yml - specific publish entry (repo root)

Supports {placeholder} templating with variables from context.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List


def deep_merge(base: Dict[Any, Any], overlay: Dict[Any, Any]) -> Dict[Any, Any]:
    """Deep merge two dictionaries. Overlay values take precedence.

    Args:
        base: Base dictionary
        overlay: Overlay dictionary (higher precedence)

    Returns:
        Merged dictionary
    """
    result = base.copy()

    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def load_yaml_safe(path: Path) -> Optional[Dict[Any, Any]]:
    """Load YAML file safely, return None if not found or invalid.

    Args:
        path: Path to YAML file

    Returns:
        Parsed YAML content or None
    """
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
            return content if isinstance(content, dict) else {}
    except Exception as e:
        print(f"Warning: Could not load {path}: {e}")
        return None


def merge_configs(
    repo_root: Path,
    publish_name: Optional[str] = None,
    extra_vars: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Merge configuration layers in precedence order.

    Args:
        repo_root: Repository root directory
        publish_name: Name of publish entry to use from publish.yml
        extra_vars: Extra variables for templating

    Returns:
        Merged configuration dictionary
    """
    merged = {}

    # Layer 1: defaults/docker_config.yml
    defaults_path = (
        repo_root / ".github" / "gitbook_worker" / "defaults" / "docker_config.yml"
    )
    defaults = load_yaml_safe(defaults_path)
    if defaults:
        merged = deep_merge(merged, defaults)

    # Layer 2: docker_config.yml (repo root)
    docker_config_path = repo_root / "docker_config.yml"
    docker_config = load_yaml_safe(docker_config_path)
    if docker_config:
        merged = deep_merge(merged, docker_config)

    # Layer 3 & 4: publish.yml
    publish_path = repo_root / "publish.yml"
    publish_data = load_yaml_safe(publish_path)

    if publish_data:
        # Layer 3: general section from publish.yml
        if "docker_config" in publish_data:
            merged = deep_merge(merged, publish_data["docker_config"])

        # Layer 4: specific publish entry
        if publish_name and "publish" in publish_data:
            for entry in publish_data.get("publish", []):
                if isinstance(entry, dict) and entry.get("name") == publish_name:
                    if "docker_config" in entry:
                        merged = deep_merge(merged, entry["docker_config"])
                    break

    return merged


def render_template(template: str, variables: Dict[str, Any]) -> str:
    """Render template string with variables using {placeholder} syntax.

    Args:
        template: Template string with {placeholders}
        variables: Dictionary of variable values

    Returns:
        Rendered string
    """
    try:
        return template.format(**variables)
    except KeyError as e:
        raise ValueError(f"Missing template variable: {e}")


def get_docker_name(
    config: Dict[str, Any],
    name_type: str,
    context: str = "test",
    extra_vars: Optional[Dict[str, str]] = None,
) -> str:
    """Get docker image or container name from merged config.

    Args:
        config: Merged configuration dictionary
        name_type: Type of name ('image' or 'container')
        context: Execution context ('github-action', 'prod', 'test', 'docker-test')
        extra_vars: Extra variables for templating

    Returns:
        Rendered docker name
    """
    if "docker_names" not in config:
        raise ValueError("No docker_names section in configuration")

    docker_names = config["docker_names"]

    # Get context-specific or default template
    context_config = docker_names.get(context, {})
    default_config = docker_names.get("default", {})

    template = context_config.get(name_type) or default_config.get(name_type)

    if not template:
        raise ValueError(f"No {name_type} template found for context '{context}'")

    # Prepare variables for templating
    variables = {
        "context": context,
        "repo_name": (
            extra_vars.get("repo_name", "erda-book") if extra_vars else "erda-book"
        ),
        "branch": extra_vars.get("branch", "main") if extra_vars else "main",
        "publish_name": (
            extra_vars.get("publish_name", "default") if extra_vars else "default"
        ),
    }

    # Add all extra vars
    if extra_vars:
        variables.update(extra_vars)

    return render_template(template, variables)


def get_all_docker_names(
    repo_root: Path,
    publish_name: Optional[str] = None,
    context: str = "test",
    extra_vars: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Get all docker names (image and container) for given context.

    Args:
        repo_root: Repository root directory
        publish_name: Name of publish entry
        context: Execution context
        extra_vars: Extra variables for templating

    Returns:
        Dictionary with 'image' and 'container' keys
    """
    config = merge_configs(repo_root, publish_name, extra_vars)

    return {
        "image": get_docker_name(config, "image", context, extra_vars),
        "container": get_docker_name(config, "container", context, extra_vars),
    }
