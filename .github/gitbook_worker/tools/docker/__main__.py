#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entry point for running setup_docker_environment as a module.

Usage:
    python3 -m tools.docker.setup_docker_environment --mode install
"""

from .setup_docker_environment import main

if __name__ == "__main__":
    import sys

    sys.exit(main())
