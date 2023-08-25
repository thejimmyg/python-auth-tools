if __name__ == "__main__":
    import sys

    from helper_hooks import setup_hooks
    from helper_webhook import generate_keys_to_store_dir

    hook_module_path = sys.argv[1]
    setup_hooks(hook_module_path)

    generate_keys_to_store_dir(sys.argv[2])
