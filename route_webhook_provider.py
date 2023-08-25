from config_webhook_provider import config_webhook_provider_jwks_json_path
from route_static import route_static

route_webhook_provider_jwks_json = route_static(
    config_webhook_provider_jwks_json_path,
    "application/json; charset=UTF8",
)
