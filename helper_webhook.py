import json
import os

from jwcrypto import jwk, jwt

from config_webhook import webhook_jwks_json_path, webhook_private_keys_dir_path
from helper_log import log

#
# Generate Keys
#


def generate_keys_to_store_dir(kid):
    key = jwk.JWK.generate(
        kty="RSA", size=2048, kid=kid, use="sig", e="AQAB", alg="RS256"
    )
    private_key = key.export_private()
    public_key = key.export_public(as_dict=True)
    log(__file__, "Private key:", private_key)
    with open(os.path.join(webhook_private_keys_dir_path, kid), "w") as fp:
        fp.write(private_key)
    if os.path.exists(webhook_jwks_json_path):
        with open(webhook_jwks_json_path, "r") as fp:
            jwks = json.loads(fp.read())
    else:
        jwks = {"keys": []}
    jwks["keys"].append(public_key)
    with open(webhook_jwks_json_path, "w") as fp:
        fp.write(json.dumps(jwks))
    log(__file__, "jwks.json:", jwks)


#
# Sign
#


private_keys = {}


def sign_jwt(body, kid):
    if kid not in private_keys:
        with open(os.path.join(webhook_private_keys_dir_path, kid), "rb") as fp:
            private_keys[kid] = json.loads(fp.read())
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
