if __name__ == "__main__":
    import sys

    from helper_oauth_authorization_server import generate_keys_to_store_dir
    from helper_hooks import setup_hooks

    hook_module_path = sys.argv[1]
    setup_hooks(hook_module_path)

    generate_keys_to_store_dir(sys.argv[2])
