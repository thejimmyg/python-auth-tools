import importlib
import signal
import sys

from helper_log import helper_log

hooks = None


def helper_hooks_setup(hook_module_path):
    if hook_module_path.endswith(".py"):
        helper_log(
            __file__,
            "WARNING: Module paths do not normally end with .py, are you specifying the path rather than the module?",
        )
    importlib.import_module(hook_module_path)
    # Importing this module should set up helper_hooks.hooks
    assert hooks is not None, "Failed to set up hooks"

    helper_log(__file__, "Initialising ...")
    for init in hooks.get("init", []):
        helper_log(__file__, init)
        init()
    helper_log(__file__, "done.")

    def handler(signum, frame):
        signame = signal.Signals(signum).name
        print(f"Signal handler called with signal {signame} ({signum})")
        print("Cleaning up ...")
        for cleanup in hooks.get("cleanup", []):
            print(cleanup)
            cleanup()
        print("done.")
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
