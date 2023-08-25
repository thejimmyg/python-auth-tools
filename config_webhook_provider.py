import os

from config import config_store_dir

config_webhook_provider_store_dir = os.path.join(config_store_dir, "webhook_provider")
os.makedirs(config_webhook_provider_store_dir, exist_ok=True)
config_webhook_provider_private_keys_dir_path = os.path.join(
    config_webhook_provider_store_dir, "private_keys"
)
os.makedirs(config_webhook_provider_private_keys_dir_path, exist_ok=True)
config_webhook_provider_jwks_json_path = os.path.join(
    config_webhook_provider_store_dir, "jwks.json"
)
config_webhook_provider_keys_db_path = os.path.join(
    config_webhook_provider_store_dir, "keys"
)
