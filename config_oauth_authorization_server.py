import os

from config_common import store_dir

oauth_authorization_server_store_dir = os.path.join(
    store_dir, "oauth_authorization_server"
)
os.makedirs(oauth_authorization_server_store_dir, exist_ok=True)
oauth_authorization_server_private_keys_dir_path = os.path.join(
    oauth_authorization_server_store_dir, "private_keys"
)
os.makedirs(oauth_authorization_server_private_keys_dir_path, exist_ok=True)
oauth_authorization_server_clients_dir_path = os.path.join(
    oauth_authorization_server_store_dir, "clients"
)
os.makedirs(oauth_authorization_server_clients_dir_path, exist_ok=True)
oauth_authorization_server_clients_client_credentials_dbpath = os.path.join(
    oauth_authorization_server_store_dir, "clients", "client_credentials"
)
oauth_authorization_server_clients_code_dbpath = os.path.join(
    oauth_authorization_server_store_dir, "clients", "code"
)
oauth_authorization_server_store_codes_dbpath = os.path.join(
    oauth_authorization_server_store_dir, "code"
)
oauth_authorization_server_store_session_dbpath = os.path.join(
    oauth_authorization_server_store_dir, "session"
)
oauth_authorization_server_store_keys_dbpath = os.path.join(
    oauth_authorization_server_store_dir, "keys"
)
oauth_authorization_server_jwks_json_path = os.path.join(
    oauth_authorization_server_store_dir, "jwks.json"
)
