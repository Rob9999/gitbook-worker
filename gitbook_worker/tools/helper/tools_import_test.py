import importlib
import sys
import traceback

try:
    import gitbook_worker.tools as tools  # noqa: F401 - import side-effects

    print("tools.__file__ =", getattr(tools, "__file__", None))
    module = importlib.import_module("gitbook_worker.tools.workflow_orchestrator")
    print(
        "gitbook_worker.tools.workflow_orchestrator ->",
        getattr(module, "__file__", None),
    )
except Exception:
    traceback.print_exc()
    sys.exit(2)
