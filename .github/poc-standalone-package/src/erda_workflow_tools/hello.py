"""
Example module for proof-of-concept.

In the full implementation, this directory would contain:
- workflow_orchestrator/
- publishing/
- converter/
- quality/
- emoji/
- utils/
- docker/
"""


def greet(name: str) -> str:
    """
    Simple greeting function for testing.

    Args:
        name: Name to greet

    Returns:
        Greeting message

    Example:
        >>> from erda_workflow_tools import hello
        >>> hello.greet("World")
        'Hello, World!'
    """
    message = f"Hello, {name}!"
    print(message)
    return message


def get_version() -> str:
    """
    Get package version.

    Returns:
        Version string
    """
    from . import __version__

    return __version__
