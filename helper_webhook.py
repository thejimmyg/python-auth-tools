import json

from jwcrypto import jwk, jwt

from config_webhook import webhook_jwks_json_path, webhook_private_key_path
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
    with open(webhook_private_key_path, "w") as fp:
        fp.write(private_key)
    jwks = json.dumps({"keys": [public_key]})
    with open(webhook_jwks_json_path, "w") as fp:
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


def sign_jwt(body):
    if private_key[0] is None:
        with open(webhook_private_key_path, "rb") as fp:
            private_key[0] = json.loads(fp.read())
    jwt_token = jwt.JWT(
        header=jwt_header,
        claims=body,
    )
    jwt_token.make_signed_token(jwk.JWK(**private_key[0]))
    signed_jwt_parts = jwt_token.serialize().split(".")
    return signed_jwt_parts[0] + ".." + signed_jwt_parts[2]
