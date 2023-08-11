import os

from config_common import store_dir

oauth_authorization_server_store_dir = os.path.join(
    store_dir, "oauth_authorization_server"
)
os.makedirs(oauth_authorization_server_store_dir, exist_ok=True)
oauth_authorization_server_private_key_path = os.path.join(
    oauth_authorization_server_store_dir, "private.key"
)
oauth_authorization_server_clients_json_path = os.path.join(
    oauth_authorization_server_store_dir, "clients.json"
)
oauth_authorization_server_store_codes_dbpath = os.path.join(
    oauth_authorization_server_store_dir, "code"
)
oauth_authorization_server_store_session_dbpath = os.path.join(
    oauth_authorization_server_store_dir, "session"
)
oauth_authorization_server_jwks_json_path = os.path.join(
    oauth_authorization_server_store_dir, "jwks.json"
)
