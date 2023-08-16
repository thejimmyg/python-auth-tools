import os

from config_common import store_dir

webhook_store_dir = os.path.join(store_dir, "webhook")
os.makedirs(webhook_store_dir, exist_ok=True)
webhook_private_keys_dir_path = os.path.join(webhook_store_dir, "private_keys")
os.makedirs(webhook_private_keys_dir_path, exist_ok=True)
webhook_jwks_json_path = os.path.join(webhook_store_dir, "jwks.json")
webhook_store_keys_dbpath = os.path.join(webhook_store_dir, "keys")
