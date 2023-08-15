from config_webhook import webhook_jwks_json_path
from route_static import static

webhook_jwks_json = static(
    webhook_jwks_json_path,
    "application/json; charset=UTF8",
)
