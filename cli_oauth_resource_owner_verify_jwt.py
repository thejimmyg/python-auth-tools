from jwcrypto import jwt, jwk, jws
import json
import base64
import urllib.request

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


if __name__ == "__main__":
    import sys

    print(verify_jwt(sys.argv[1]))

# Failure
# jwstoken = jws.JWS()
# jwstoken.deserialize(signed_jwt+'q')
# print(jwstoken.jose_header['kid'])
# jwstoken.verify(key)
# payload = jwstoken.payload
# print(payload.decode())
