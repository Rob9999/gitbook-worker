"""
gitbook_worker package - Workflow automation for GitBook-based projects.

This package provides tools for publishing, conversion, quality assurance,
and workflow orchestration.

Main entry point:
    python -m gitbook_worker.tools.workflow_orchestrator

Package structure:
    - tools.workflow_orchestrator: Main CLI orchestrator
    - tools.publishing: PDF publishing and GitBook utilities
    - tools.converter: CSV to Markdown/diagram conversion
    - tools.quality: Link audits, source extraction, AI reference checks
    - tools.emoji: Emoji scanning and reporting
    - tools.utils: Cross-platform helpers (Docker, Git, subprocess)
    - tools.docker: Dockerfile and container management

For backward compatibility with legacy 'tools.*' imports,
see the shim at repository root: tools/__init__.py
"""

__version__ = "0.1.0"
__all__ = ["tools"]
