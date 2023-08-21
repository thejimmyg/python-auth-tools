if __name__ == "__main__":
    import sys

    from helper_plugins import setup_plugins
    from store_oauth_authorization_server_clients_code import (
        CodeClient,
        put_code_client,
    )

    plugin_module_path = sys.argv[1]
    setup_plugins(plugin_module_path)

    put_code_client(
        sys.argv[2],
        CodeClient(
            redirect_uri=sys.argv[3],
            scopes=[x.strip() for x in sys.argv[4].split(" ") if x.strip()],
        ),
    )
