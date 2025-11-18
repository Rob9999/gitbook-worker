import os
import subprocess
from typing import Any, Dict, List, Optional
from tools.logging_config import get_logger

logger = get_logger(__name__)


def run(
    cmd: List[str],
    check: bool = True,
    capture: bool = True,
    env: Optional[Dict[str, str]] = None,
) -> subprocess.CompletedProcess:
    kwargs: Dict[str, Any] = {"text": True, "encoding": "utf-8"}
    if capture:
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.PIPE
    if env:
        kwargs["env"] = {**os.environ, **env}
    print(f"{cmd}")
    logger.info("%s", " ".join(cmd))
    cp: subprocess.CompletedProcess = subprocess.run(cmd, **kwargs)
    if check and cp.returncode != 0:
        if capture:
            logger.info(cp.stdout or "")
            logger.error(cp.stderr or "")
        raise subprocess.CalledProcessError(cp.returncode, cmd)
    return cp
