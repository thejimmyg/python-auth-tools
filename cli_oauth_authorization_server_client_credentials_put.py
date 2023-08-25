if __name__ == "__main__":
    import sys

    from helper_hooks import helper_hooks_setup
    from store_oauth_authorization_server_client_credentials import (
        ClientCredentials,
        store_oauth_authorization_server_client_credentials_put,
    )

    hook_module_path = sys.argv[1]
    helper_hooks_setup(hook_module_path)

    store_oauth_authorization_server_client_credentials_put(
        sys.argv[2],
        ClientCredentials(
            client_secret=sys.argv[3],
            scopes=[x.strip() for x in sys.argv[4].split(" ") if x.strip()],
        ),
    )
