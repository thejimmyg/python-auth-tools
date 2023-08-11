import base64
import json
import urllib.request

from jwcrypto import jwk, jws, jwt

from helper_log import log
from helper_oidc import fetch_openid_configuration

#
# Verify
#

# with open('jwks.json', 'rb') as fp:
#    public_key = jwk.JWK(**json.loads(fp.read())['keys'][0])

# XXX Implement rate limiting on fetch and a cache


def verify_jwt(signed_jwt):
    if not signed_jwt or not signed_jwt.startswith("e"):
        raise Exception("Not a valid JWT")
    log(__file__, "Signed JWT:", signed_jwt)
    issuer = json.loads(
        base64.b64decode(signed_jwt.split(".")[1] + "==").decode("utf8")
    )["iss"]
    log(__file__, "Issuer:", issuer)
    openid_configuration = fetch_openid_configuration(issuer)
    log(__file__, "OpenID Configuration:", openid_configuration)
    with urllib.request.urlopen(openid_configuration["jwks_uri"]) as fp:
        jwks = json.loads(fp.read())
        public_key = jwk.JWK(**jwks["keys"][0])
    jwstoken = jws.JWS()
    jwstoken.deserialize(signed_jwt)
    log(__file__, "JOSE Header:", jwstoken.jose_header)
    ja = jwt.JWT(algs=["RS256"])
    ja.deserialize(signed_jwt, public_key)
    claims = ja.token.payload.decode()

    # jwstoken.verify(public_key)
    # payload = jwstoken.payload
    # # XXX This doesn't check the claims or the encryption type
    # claims = payload.decode()
    # # This does:
    # ET = jwt.JWT(key=public_key, jwt=signed_jwt)
    return json.loads(claims)


# Failure
# jwstoken = jws.JWS()
# jwstoken.deserialize(signed_jwt+'q')
# jwstoken.verify(key)
# payload = jwstoken.payload
# log(__file__, 'Decoded payload:', payload.decode())
