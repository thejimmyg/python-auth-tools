import base64

from jwcrypto import jwk, jws, jwt

from helper_log import helper_log
from helper_oidc import helper_oidc_fetch_and_cache_jwks_for_kid

#
# Verify
#


# XXX Implement rate limiting on fetch and a cache


def helper_webhook_consumer_verify_jwt(sig, body, jwks_url):
    if not sig or not sig.startswith("e"):
        raise Exception("Not a valid JWT")
    signed_jwt_parts = sig.split(".")
    assert signed_jwt_parts[1] == "", signed_jwt_parts
    signed_jwt = (
        signed_jwt_parts[0]
        + "."
        + base64.urlsafe_b64encode(body).decode("utf8").strip("=")
        + "."
        + signed_jwt_parts[2]
    )
    helper_log(__file__, "Signed JWT:", signed_jwt)
    jwstoken = jws.JWS()
    jwstoken.deserialize(signed_jwt)
    helper_log(__file__, "JOSE Header:", jwstoken.jose_header)
    kid = jwstoken.jose_header["kid"]
    jwks = helper_oidc_fetch_and_cache_jwks_for_kid(jwks_url, kid)
    public_key = None
    for key in jwks["keys"]:
        if key["kid"] == kid:
            public_key = jwk.JWK(**key)
            break
    if public_key is None:
        raise Exception(f"No such key '{kid}' found in the JWKS at '{jwks_url}'")
    ja = jwt.JWT(algs=["RS256"])
    ja.deserialize(signed_jwt, public_key)
    result = ja.token.payload.decode()
    assert result == body.decode("utf8"), [result, body]
    return result
