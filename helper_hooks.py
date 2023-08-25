import importlib
import signal
import sys

hooks = None


def setup_hooks(hook_module_path):
    if hook_module_path.endswith(".py"):
        print(
            "WARNING: Module paths do not normally end with .py, are you specifying the path rather than the module?"
        )
        print()
    importlib.import_module(hook_module_path)
    # Importing this module should set up helper_hooks.hooks
    assert hooks is not None, "Failed to set up hooks"

    print("Initialising ...")
    for init in hooks["init"]:
        print(init)
        init()
    print("done.")

    def handler(signum, frame):
        signame = signal.Signals(signum).name
        print(f"Signal handler called with signal {signame} ({signum})")
        print("Cleaning up ...")
        for cleanup in hooks["cleanup"]:
            print(cleanup)
            cleanup()
        print("done.")
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
