import os

from config_common import store_dir

oauth_client_store_dir = os.path.join(store_dir, "oauth_client_store_dir")
os.makedirs(oauth_client_store_dir, exist_ok=True)
oauth_client_store_code_verifier_dbpath = os.path.join(
    oauth_client_store_dir, "code_verifier"
)
