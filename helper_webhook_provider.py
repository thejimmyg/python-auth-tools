from jwcrypto import jwk, jwt


#
# Generate Keys
#


#
# Sign
#

from store_webhook_provider_key import (
    store_webhook_provider_key_get_and_cache,
)

private_keys = {}


def helper_webhook_provider_sign_jwt(body, kid):
    if kid not in private_keys:
        private_keys[kid] = store_webhook_provider_key_get_and_cache(kid)
    jwt_header = {
        "alg": "RS256",
        "kid": kid,
    }
    jwt_token = jwt.JWT(
        header=jwt_header,
        claims=body,
    )
    jwt_token.make_signed_token(jwk.JWK(**private_keys[kid]))
    signed_jwt_parts = jwt_token.serialize().split(".")
    return signed_jwt_parts[0] + ".." + signed_jwt_parts[2]
