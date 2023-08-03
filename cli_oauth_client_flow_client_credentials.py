if __name__ == "__main__":
    import sys
    from helper_crypto import (
        verify_jwt,
        fetch_openid_configuration,
        client_credentials_token,
    )
    import config
    import json

    issuer = config.url
    client = sys.argv[1]
    secret = sys.argv[2]

    openid_configuration = fetch_openid_configuration(issuer)
    print(
        json.dumps(
            client_credentials_token(
                openid_configuration["token_endpoint"], client=client, secret=secret
            )
        )
    )
