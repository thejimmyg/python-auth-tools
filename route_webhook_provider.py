from store_webhook_provider_jwks import (
    store_webhook_provider_jwks_get_and_cache,
)


def route_webhook_provider_jwks_json(http):
    jwks = store_webhook_provider_jwks_get_and_cache()
    http.response.body = jwks.encode("UTF8")
    http.response.headers["Content-Type"] = "application/json; charset=UTF8"
