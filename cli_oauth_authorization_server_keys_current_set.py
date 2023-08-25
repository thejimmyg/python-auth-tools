if __name__ == "__main__":
    import sys

    from helper_hooks import helper_hooks_setup
    from store_oauth_authorization_server_keys_current import (
        store_oauth_authorization_server_keys_current_put,
    )

    hook_module_path = sys.argv[1]
    helper_hooks_setup(hook_module_path)

    store_oauth_authorization_server_keys_current_put(sys.argv[2])
