if __name__ == "__main__":
    import json
    import sys

    import config
    from helper_crypto import (
        client_credentials_token,
        fetch_openid_configuration,
        verify_jwt,
    )

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
