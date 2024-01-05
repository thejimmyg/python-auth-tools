if __name__ == "__main__":
    import sys

    from helper_hooks import helper_hooks_setup
    from helper_log import helper_log

    import json
    from jwcrypto import jwk

    from kvstore.driver import NotFound

    from store_webhook_provider_key import (
        store_webhook_provider_key_put,
    )
    from store_webhook_provider_jwks import (
        store_webhook_provider_jwks_put,
        store_webhook_provider_jwks_get,
    )

    hook_module_path = sys.argv[1]
    helper_hooks_setup(hook_module_path)
    kid = sys.argv[2]
    key = jwk.JWK.generate(
        kty="RSA", size=2048, kid=kid, use="sig", e="AQAB", alg="RS256"
    )
    private_key = key.export_private()
    public_key = key.export_public(as_dict=True)
    helper_log(__file__, "Private key:", private_key)
    store_webhook_provider_key_put(kid, private_key)
    try:
        jwks = json.loads(store_webhook_provider_jwks_get())
    except NotFound:
        jwks = {"keys": []}
    jwks["keys"].append(public_key)
    store_webhook_provider_jwks_put(json.dumps(jwks))
