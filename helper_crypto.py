from datetime import datetime as dt
import json
from jwcrypto import jwt, jwk, jws
import base64
import urllib.request

from config import (
    store_dir,
    oauth_authorization_server_store_dir,
    private_key_path,
    url,
)

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
            # print(verify_jwt(response["access_token"]))
    except urllib.error.HTTPError as e:
        print("ERROR:", e.read().decode())
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
    print(signed_jwt)
    issuer = json.loads(
        base64.b64decode(signed_jwt.split(".")[1] + "==").decode("utf8")
    )["iss"]
    print(issuer)
    with urllib.request.urlopen(issuer + "/.well-known/openid-configuration") as fp:
        oidc = json.loads(fp.read())
    print(oidc)
    with urllib.request.urlopen(oidc["jwks_uri"]) as fp:
        jwks = json.loads(fp.read())
        public_key = jwk.JWK(**jwks["keys"][0])
    jwstoken = jws.JWS()
    jwstoken.deserialize(signed_jwt)
    print(jwstoken.jose_header)
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
# print(jwstoken.jose_header['kid'])
# jwstoken.verify(key)
# payload = jwstoken.payload
# print(payload.decode())
