if __name__ == "__main__":
    import sys

    from helper_plugins import setup_plugins
    from helper_webhook import generate_keys_to_store_dir

    plugin_module_path = sys.argv[1]
    setup_plugins(plugin_module_path)

    generate_keys_to_store_dir(sys.argv[2])
