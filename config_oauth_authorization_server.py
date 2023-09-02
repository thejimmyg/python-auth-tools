import os

from config import config_store_dir

config_oauth_authorization_server_store_dir = os.path.join(
    config_store_dir, "oauth_authorization_server"
)
os.makedirs(config_oauth_authorization_server_store_dir, exist_ok=True)
config_oauth_authorization_server_private_keys_dir_path = os.path.join(
    config_oauth_authorization_server_store_dir, "private_keys"
)
os.makedirs(config_oauth_authorization_server_private_keys_dir_path, exist_ok=True)
config_oauth_authorization_server_jwks_json_path = os.path.join(
    config_oauth_authorization_server_store_dir, "jwks.json"
)
