import importlib
import sys
import traceback

try:
    import tools

    print("tools.__file__ =", getattr(tools, "__file__", None))
    m = importlib.import_module("tools.workflow_orchestrator")
    print("tools.workflow_orchestrator ->", getattr(m, "__file__", None))
except Exception:
    traceback.print_exc()
    sys.exit(2)
