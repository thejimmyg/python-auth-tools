import base64
import json
import urllib.request

from jwcrypto import jwk, jws, jwt

from helper_log import log

#
# Verify
#


# XXX Implement rate limiting on fetch and a cache


def verify_jwt(sig, body, jwks_url):
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
    log(__file__, "Signed JWT:", signed_jwt)
    with urllib.request.urlopen(jwks_url) as fp:
        jwks = json.loads(fp.read())
        # XXX Match the right kid
        public_key = jwk.JWK(**jwks["keys"][0])
    jwstoken = jws.JWS()
    jwstoken.deserialize(signed_jwt)
    log(__file__, "JOSE Header:", jwstoken.jose_header)
    ja = jwt.JWT(algs=["RS256"])
    ja.deserialize(signed_jwt, public_key)
    result = ja.token.payload.decode()
    assert result == body.decode("utf8"), [result, body]
    return result
