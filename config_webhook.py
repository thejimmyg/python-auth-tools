import os

from config_common import store_dir

webhook_store_dir = os.path.join(store_dir, "webhook")
os.makedirs(webhook_store_dir, exist_ok=True)
webhook_private_key_path = os.path.join(webhook_store_dir, "private.key")
# webhook_clients_json_path = os.path.join(
#     webhook_store_dir, "clients.json"
# )
# webhook_store_codes_dbpath = os.path.join(
#     webhook_store_dir, "code"
# )
# webhook_store_session_dbpath = os.path.join(
#     webhook_store_dir, "session"
# )
webhook_jwks_json_path = os.path.join(webhook_store_dir, "jwks.json")
