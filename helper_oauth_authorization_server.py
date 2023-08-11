import json
from datetime import datetime as dt

from jwcrypto import jwk, jwt

from config_common import url
from config_oauth_authorization_server import (
    oauth_authorization_server_jwks_json_path,
    oauth_authorization_server_private_key_path,
)
from helper_log import log

#
# Generate Keys
#


def generate_keys_to_store_dir():
    key = jwk.JWK.generate(
        kty="RSA", size=2048, kid="test", use="sig", e="AQAB", alg="RS256"
    )

    private_key = key.export_private()
    public_key = key.export_public(as_dict=True)

    log(__file__, "Private key:", private_key)
    with open(oauth_authorization_server_private_key_path, "w") as fp:
        fp.write(private_key)
    jwks = json.dumps({"keys": [public_key]})
    with open(oauth_authorization_server_jwks_json_path, "w") as fp:
        fp.write(jwks)
    log(__file__, "jwks.json:", jwks)


#
# Sign
#


jwt_header = {
    "alg": "RS256",
    "kid": "test",
}

private_key = [None]


def sign_jwt(client_id, sub, expires_in=600, scopes=None):
    if private_key[0] is None:
        with open(oauth_authorization_server_private_key_path, "rb") as fp:
            private_key[0] = json.loads(fp.read())
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
    jwt_token.make_signed_token(jwk.JWK(**private_key[0]))
    signed_jwt = jwt_token.serialize()
    return signed_jwt
