import json

from jwcrypto import jwk

import config
from helper_log import log

key = jwk.JWK.generate(
    kty="RSA", size=2048, kid="test", use="sig", e="AQAB", alg="RS256"
)

private_key = key.export_private()
public_key = key.export_public(as_dict=True)

log(__file__, "Private key:", private_key)
with open(config.private_key_path, "w") as fp:
    fp.write(private_key)
jwks = json.dumps({"keys": [public_key]})
with open(config.oauth_authorization_server_jwks_json, "w") as fp:
    fp.write(jwks)
log(__file__, "jwks.json:", jwks)
