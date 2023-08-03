import base64
import json
import urllib.request
from datetime import datetime as dt

from jwcrypto import jwk, jws, jwt

from config import (
    oauth_authorization_server_store_dir,
    private_key_path,
    store_dir,
    url,
)
from helper_log import log

#
# Fetch OpenID Configuration
#


def fetch_openid_configuration(issuer):
    with urllib.request.urlopen(issuer + "/.well-known/openid-configuration") as fp:
        return json.loads(fp.read())


#
# Get an access token using client credentials
#


def client_credentials_token(token_endpoint, client, secret):
    request = urllib.request.Request(
        token_endpoint + "?grant_type=client_credentials",
        headers={
            "Authorization": "Basic "
            + base64.b64encode((client + ":" + secret).encode("utf8")).decode("utf8")
        },
    )
    try:
        with urllib.request.urlopen(request) as fp:
            response = json.loads(fp.read())
            # log(__file__, 'Verified JWT:', verify_jwt(response["access_token"]))
    except urllib.error.HTTPError as e:
        log(__file__, "ERROR:", e.read().decode())
        raise
    return response


#
# Sign
#

with open(private_key_path, "rb") as fp:
    private_key = json.loads(fp.read())

jwt_header = {
    "alg": "RS256",
    "kid": "test",
}


def sign_jwt(client_id, sub, expires_in=600, scopes=None):
    now = int(dt.now().timestamp())
    jwt_claims = {
        "iss": url,
        "sub": sub,
        "aud": client_id,
        "iat": now,
        # 'nbf': now,
        "exp": now + expires_in,
        # 'jti': 'JWT ID'
    }
    if scopes:
        jwt_claims["scope"] = " ".join(scopes)
    jwt_token = jwt.JWT(
        header=jwt_header,
        claims=jwt_claims,
    )
    jwt_token.make_signed_token(jwk.JWK(**private_key))
    signed_jwt = jwt_token.serialize()
    return signed_jwt


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
