from jwcrypto import jwt, jwk
from datetime import datetime as dt
import json

from config import (
    store_dir,
    oauth_authorization_server_store_dir,
    private_key_path,
    url,
)


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


if __name__ == "__main__":
    print(sign_jwt(client_id="client_id", sub="sub", scopes=["read"]))
