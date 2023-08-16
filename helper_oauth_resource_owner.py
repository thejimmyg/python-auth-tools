import base64
import json

from jwcrypto import jwk, jws, jwt

from helper_log import log
from helper_oidc import (
    fetch_and_cache_jwks_for_kid,
    fetch_and_cache_openid_configuration,
)

#
# Verify
#

# with open('jwks.json', 'rb') as fp:
#    public_key = jwk.JWK(**json.loads(fp.read())['keys'][0])

# XXX Implement rate limiting on fetch and a cache
# XXX Verify the issuer


def verify_jwt(signed_jwt):
    if not signed_jwt or not signed_jwt.startswith("e"):
        raise Exception("Not a valid JWT")
    log(__file__, "Signed JWT:", signed_jwt)
    issuer = json.loads(
        base64.b64decode(signed_jwt.split(".")[1] + "==").decode("utf8")
    )["iss"]
    log(__file__, "Issuer:", issuer)
    openid_configuration = fetch_and_cache_openid_configuration(issuer)
    log(__file__, "OpenID Configuration:", openid_configuration)
    jwks_url = openid_configuration["jwks_uri"]
    jwstoken = jws.JWS()
    jwstoken.deserialize(signed_jwt)
    log(__file__, "JOSE Header:", jwstoken.jose_header)
    kid = jwstoken.jose_header["kid"]
    jwks = fetch_and_cache_jwks_for_kid(jwks_url, kid)
    public_key = None
    for key in jwks["keys"]:
        if key["kid"] == kid:
            public_key = jwk.JWK(**key)
            break
    if public_key is None:
        raise Exception(f"No such key '{kid}' found in the JWKS at '{jwks_url}'")
    ja = jwt.JWT(algs=["RS256"])
    ja.deserialize(signed_jwt, public_key)
    claims = ja.token.payload.decode()
    return json.loads(claims)
