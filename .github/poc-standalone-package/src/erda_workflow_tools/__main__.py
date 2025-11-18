"""
CLI entry point for erda-workflow-tools package.

In the full implementation, this would invoke the workflow orchestrator.
"""

import sys
from . import __version__


def main():
    """Main entry point for the erda-workflow-tools CLI."""
    print(f"ERDA Workflow Tools v{__version__}")
    print("This is a proof-of-concept package structure.")
    print()
    print("In the full implementation, this would run:")
    print("  python -m erda_workflow_tools.workflow_orchestrator")
    print()
    print(
        "Try: python -c 'from erda_workflow_tools import hello; hello.greet(\"World\")'"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
