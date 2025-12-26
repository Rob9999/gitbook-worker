import subprocess
import sys

from gitbook_worker.tools.exit_codes.exit_code import (
    get_exit_info,
    iter_exit_codes,
    print_exit_codes_table,
)


def test_registry_contains_core_codes():
    codes = list(iter_exit_codes())
    code_values = {info.code for info in codes}
    assert 43 in code_values
    assert any(info.component.startswith("workflow_orchestrator") for info in codes)


def test_get_exit_info_filters_by_component():
    matches = get_exit_info(2, component="publisher")
    assert matches
    for info in matches:
        assert "publisher" in info.component


def test_cli_exit_codes_table(tmp_path):
    # Run module CLI and ensure it prints a header and at least one known code
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "gitbook_worker.tools.exit_codes.exit_code",
            "--exit-codes",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    output = result.stdout
    assert "Code" in output
    assert "43" in output
    assert "Fonts" in output or "Font" in output


def test_print_exit_codes_table_filters():
    out = print_exit_codes_table(filter_code=43, component="publisher")
    assert "43" in out
    assert "publisher" in out


def test_orchestrator_help_exit_codes():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "gitbook_worker.tools.workflow_orchestrator.orchestrator",
            "--help-exit-codes",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Code" in result.stdout
    assert "43" in result.stdout


def test_pipeline_help_exit_codes():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "gitbook_worker.tools.publishing.pipeline",
            "--help-exit-codes",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Code" in result.stdout
    assert "43" in result.stdout
