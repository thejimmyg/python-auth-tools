import importlib
import signal
import sys

import plugins
import render


def setup_plugins(plugin_module_path):
    if plugin_module_path.endswith(".py"):
        print(
            "WARNING: Module paths do not normally end with .py, are you specifying the path rather than the module?"
        )
        print()
    plugin_module = importlib.import_module(plugin_module_path)
    plugins.main_markup = getattr(plugin_module, "main_markup", render.main_markup)
    plugins.routes = getattr(plugin_module, "routes")
    plugins.init = getattr(plugin_module, "init", [])
    plugins.cleanup = getattr(plugin_module, "cleanup", [])

    for extension_point_name in getattr(plugin_module, "extension_points", []):
        print(f"Setting extension point implementation for '{extension_point_name}'")
        setattr(
            plugins, extension_point_name, getattr(plugin_module, extension_point_name)
        )

    print("Initialising ...")
    for init in plugins.init:
        print(init)
        init()
    print("done.")

    def handler(signum, frame):
        signame = signal.Signals(signum).name
        print(f"Signal handler called with signal {signame} ({signum})")
        print("Cleaning up ...")
        for cleanup in plugins.cleanup:
            print(cleanup)
            cleanup()
        print("done.")
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
