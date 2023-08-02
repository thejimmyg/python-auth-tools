from jwcrypto import jwk
import json
import config

key = jwk.JWK.generate(
    kty="RSA", size=2048, kid="test", use="sig", e="AQAB", alg="RS256"
)

private_key = key.export_private()
public_key = key.export_public(as_dict=True)

print("Private key:", private_key)
with open(config.private_key_path, "w") as fp:
    fp.write(private_key)
jwks = json.dumps({"keys": [public_key]})
with open(config.oauth_authorization_server_jwks_json, "w") as fp:
    fp.write(jwks)
print("jwks.json:", jwks)
