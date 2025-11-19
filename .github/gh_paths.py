# #!/usr/bin/env python3

import pathlib

# Absolute Root of the repository
REPO_ROOT = pathlib.Path(__file__).parent.parent
print(f"INFO: Repository Root   :  {REPO_ROOT}")

# Absolute .github Directory
GITHUB_DIR = REPO_ROOT / ".github"
print(f"INFO: Github Directory  :  {GITHUB_DIR}")

# Absolute repository Tools Directory
GH_TOOLS_DIR = REPO_ROOT / "tools"
print(f"INFO: Tools Directory   :  {GH_TOOLS_DIR}")

# Absolute repository Docker Directory
GH_DOCKER_DIR = REPO_ROOT / "docker"
print(f"INFO: Docker Directory  :  {GH_DOCKER_DIR}")

# Absolute repository Logs directory
GH_LOGS_DIR = REPO_ROOT / "logs"
print(f"INFO: Logs Directory    :  {GH_LOGS_DIR}")
GH_LOGS_DIR.mkdir(exist_ok=True)
