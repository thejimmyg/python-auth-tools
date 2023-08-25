import json
import os

from jwcrypto import jwk, jwt

from config_webhook_provider import (
    config_webhook_provider_jwks_json_path,
    config_webhook_provider_private_keys_dir_path,
)
from helper_log import helper_log

#
# Generate Keys
#


def helper_webhook_provider_generate_keys_to_store_dir(kid):
    key = jwk.JWK.generate(
        kty="RSA", size=2048, kid=kid, use="sig", e="AQAB", alg="RS256"
    )
    private_key = key.export_private()
    public_key = key.export_public(as_dict=True)
    helper_log(__file__, "Private key:", private_key)
    with open(
        os.path.join(config_webhook_provider_private_keys_dir_path, kid), "w"
    ) as fp:
        fp.write(private_key)
    if os.path.exists(config_webhook_provider_jwks_json_path):
        with open(config_webhook_provider_jwks_json_path, "r") as fp:
            jwks = json.loads(fp.read())
    else:
        jwks = {"keys": []}
    jwks["keys"].append(public_key)
    with open(config_webhook_provider_jwks_json_path, "w") as fp:
        fp.write(json.dumps(jwks))
    helper_log(__file__, "jwks.json:", jwks)


#
# Sign
#


private_keys = {}


def helper_webhook_provider_sign_jwt(body, kid):
    if kid not in private_keys:
        with open(
            os.path.join(config_webhook_provider_private_keys_dir_path, kid), "rb"
        ) as fp:
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
