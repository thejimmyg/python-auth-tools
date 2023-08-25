if __name__ == "__main__":
    import sys

    from helper_hooks import setup_hooks
    from store_oauth_authorization_server_clients_client_credentials import (
        ClientCredentialsClient,
        put_client_credentials_client,
    )

    hook_module_path = sys.argv[1]
    setup_hooks(hook_module_path)

    put_client_credentials_client(
        sys.argv[2],
        ClientCredentialsClient(
            client_secret=sys.argv[3],
            scopes=[x.strip() for x in sys.argv[4].split(" ") if x.strip()],
        ),
    )
