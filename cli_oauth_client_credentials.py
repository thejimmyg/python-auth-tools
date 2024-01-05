if __name__ == "__main__":
    import json
    import sys

    from config import config_url
    from helper_oauth_client_credentials import helper_oauth_client_credentials_token
    from helper_oidc import helper_oidc_fetch_and_cache_openid_configuration

    issuer = config_url
    client = sys.argv[1]
    secret = sys.argv[2]
    scopes = sys.argv[3].strip().split(" ")

    openid_configuration = helper_oidc_fetch_and_cache_openid_configuration(issuer)
    print(
        json.dumps(
            helper_oauth_client_credentials_token(
                openid_configuration["token_endpoint"],
                client=client,
                secret=secret,
                scopes=scopes,
            )
        )
    )
