from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from tools.workflow_orchestrator import OrchestratorConfig, OrchestratorProfile, run
from tools.workflow_orchestrator.orchestrator import (
    DockerSettings,
    build_config,
    parse_args,
)


@pytest.fixture()
def temp_repo(tmp_path: Path) -> Path:
    manifest = tmp_path / "publish.yml"
    manifest.write_text(
        textwrap.dedent(
            """
            publish:
              - path: ./
                out: dummy.pdf
                build: false
            """
        ),
        encoding="utf-8",
    )
    return tmp_path


def test_build_config_resolves_profile_template(temp_repo: Path) -> None:
    manifest = temp_repo / "publish.yml"
    manifest.write_text(
        textwrap.dedent(
            """
            profiles:
              default:
                steps: [publisher]
                docker:
                  use_registry: true
                  image: "ghcr.io/${repo}/publisher"
            publish: []
            """
        ),
        encoding="utf-8",
    )
    args = parse_args(
        [
            "--root",
            str(temp_repo),
            "--manifest",
            str(manifest),
            "--repository",
            "example/repo",
        ]
    )
    config = build_config(args)
    assert config.profile.steps == ("publisher",)
    assert config.profile.docker.image == "ghcr.io/example/repo/publisher"


def test_build_config_lowercases_repo_for_template(temp_repo: Path) -> None:
    manifest = temp_repo / "publish.yml"
    manifest.write_text(
        textwrap.dedent(
            """
            profiles:
              default:
                steps: [publisher]
                docker:
                  use_registry: true
                  image: "ghcr.io/${repo}/publisher"
            publish: []
            """
        ),
        encoding="utf-8",
    )
    args = parse_args(
        [
            "--root",
            str(temp_repo),
            "--manifest",
            str(manifest),
            "--repository",
            "Example/Repo",
        ]
    )
    config = build_config(args)
    assert config.profile.docker.image == "ghcr.io/example/repo/publisher"


def test_run_creates_missing_readme(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / "publish.yml").write_text("publish: []\n", encoding="utf-8")
    target_dir = repo / "docs" / "chapter"
    target_dir.mkdir(parents=True)
    profile = OrchestratorProfile(
        name="test",
        steps=("ensure_readme",),
        docker=DockerSettings(use_registry=False, image=None, cache=False),
    )
    config = OrchestratorConfig(
        root=repo,
        manifest=repo / "publish.yml",
        profile=profile,
        repo_visibility="public",
        repository="example/repo",
        commit=None,
        base=None,
        reset_others=False,
        publisher_args=(),
        dry_run=False,
    )
    run(config)
    # Case-insensitive check: orchestrator creates README.md (uppercase)
    readme_path = target_dir / "readme.md"
    readme_path_upper = target_dir / "README.md"
    assert (
        readme_path.exists() or readme_path_upper.exists()
    ), f"Neither {readme_path} nor {readme_path_upper} exists"


def test_update_citation_dry_run(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / "publish.yml").write_text("publish: []\n", encoding="utf-8")
    publish_dir = repo / "publish"
    publish_dir.mkdir(parents=True)
    cff = publish_dir / "CITATION.cff"
    cff.write_text("version: old\ndate-released: '2000-01-01'\n", encoding="utf-8")
    profile = OrchestratorProfile(
        name="test",
        steps=("update_citation",),
        docker=DockerSettings(use_registry=False, image=None, cache=False),
    )
    config = OrchestratorConfig(
        root=repo,
        manifest=repo / "publish.yml",
        profile=profile,
        repo_visibility="public",
        repository="example/repo",
        commit=None,
        base=None,
        reset_others=False,
        publisher_args=(),
        dry_run=True,
    )
    run(config)
    content = cff.read_text(encoding="utf-8")
    assert "old" in content
    assert "2000-01-01" in content


def test_update_citation_updates_and_copies_to_root(tmp_path: Path) -> None:
    """Test that update_citation updates the file and copies to root."""
    repo = tmp_path
    (repo / "publish.yml").write_text("publish: []\n", encoding="utf-8")
    publish_dir = repo / "publish"
    publish_dir.mkdir(parents=True)
    cff = publish_dir / "CITATION.cff"
    cff.write_text("version: old\ndate-released: '2000-01-01'\n", encoding="utf-8")

    profile = OrchestratorProfile(
        name="test",
        steps=("update_citation",),
        docker=DockerSettings(use_registry=False, image=None, cache=False),
    )
    config = OrchestratorConfig(
        root=repo,
        manifest=repo / "publish.yml",
        profile=profile,
        repo_visibility="public",
        repository="example/repo",
        commit=None,
        base=None,
        reset_others=False,
        publisher_args=(),
        dry_run=False,
    )
    run(config)

    # Check publish/CITATION.cff was updated
    content = cff.read_text(encoding="utf-8")
    assert "The_zenodo_release_on_" in content
    assert "old" not in content
    assert "2000-01-01" not in content

    # Check CITATION.cff was copied to root
    root_cff = repo / "CITATION.cff"
    assert root_cff.exists()
    root_content = root_cff.read_text(encoding="utf-8")
    assert content == root_content
