"""Shared exit code registry and helpers."""

from .exit_code import (
    ExitCodeInfo,
    get_exit_info,
    iter_exit_codes,
    print_exit_codes_table,
)
from .exit_code import (
    add_exit_code_help,
    handle_exit_code_help,
)

__all__ = [
    "ExitCodeInfo",
    "add_exit_code_help",
    "get_exit_info",
    "handle_exit_code_help",
    "iter_exit_codes",
    "print_exit_codes_table",
]
