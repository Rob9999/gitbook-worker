# #!/usr/bin/env python3

import pathlib

# Absolute Root of the repository
REPO_ROOT = pathlib.Path(__file__).parent.parent
print(f"INFO: Repository Root   :  {REPO_ROOT}")

# Absolute .github Directory
GITHUB_DIR = REPO_ROOT / ".github"
print(f"INFO: Github Directory  :  {GITHUB_DIR}")

# Absolute .github Tools Directory
GH_TOOLS_DIR = GITHUB_DIR / "gitbook_worker" / "tools"
print(f"INFO: Tools Directory   :  {GH_TOOLS_DIR}")

# Absolute .github Tools Docker Directory
GH_DOCKER_DIR = GH_TOOLS_DIR / "docker"
print(f"INFO: Docker Directory  :  {GH_DOCKER_DIR}")

# Absolute .github Logs directory
GH_LOGS_DIR = GITHUB_DIR / "logs"
print(f"INFO: Logs Directory    :  {GH_LOGS_DIR}")
GH_LOGS_DIR.mkdir(exist_ok=True)
