if __name__ == "__main__":
    import sys

    from store_oauth_authorization_server_client_credentials import (
        ClientCredentials,
        store_oauth_authorization_server_client_credentials_put,
    )

    store_oauth_authorization_server_client_credentials_put(
        sys.argv[1],
        ClientCredentials(
            client_secret=sys.argv[2],
            scopes=[x.strip() for x in sys.argv[3].split(" ") if x.strip()],
        ),
    )
