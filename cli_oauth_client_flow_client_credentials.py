if __name__ == "__main__":
    import json
    import sys

    from config_common import url
    from helper_oauth_client import client_credentials_token
    from helper_oidc import fetch_and_cache_openid_configuration

    issuer = url
    client = sys.argv[1]
    secret = sys.argv[2]
    scopes = sys.argv[3].strip().split(" ")

    openid_configuration = fetch_and_cache_openid_configuration(issuer)
    print(
        json.dumps(
            client_credentials_token(
                openid_configuration["token_endpoint"],
                client=client,
                secret=secret,
                scopes=scopes,
            )
        )
    )
