if __name__ == "__main__":
    import sys

    from store_oauth_authorization_server_code_pkce import (
        CodePkce,
        store_oauth_authorization_server_code_pkce_put,
    )

    store_oauth_authorization_server_code_pkce_put(
        sys.argv[1],
        CodePkce(
            redirect_uri=sys.argv[2],
            scopes=[x.strip() for x in sys.argv[3].split(" ") if x.strip()],
        ),
    )
