import importlib

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
