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
config_oauth_authorization_server_client_credentials_db_path = os.path.join(
    config_oauth_authorization_server_store_dir, "client_credentials"
)
config_oauth_authorization_server_code_pkce_db_path = os.path.join(
    config_oauth_authorization_server_store_dir, "code_pkce"
)
config_oauth_authorization_server_codes_db_path = os.path.join(
    config_oauth_authorization_server_store_dir, "codes"
)
config_oauth_authorization_server_sessions_db_path = os.path.join(
    config_oauth_authorization_server_store_dir, "sessions"
)
config_oauth_authorization_server_keys_db_path = os.path.join(
    config_oauth_authorization_server_store_dir, "keys"
)
config_oauth_authorization_server_jwks_json_path = os.path.join(
    config_oauth_authorization_server_store_dir, "jwks.json"
)
