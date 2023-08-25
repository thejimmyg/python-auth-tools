import os

from config import config_store_dir

config_oauth_code_pkce_store_dir = os.path.join(config_store_dir, "oauth_code_pkce")
os.makedirs(config_oauth_code_pkce_store_dir, exist_ok=True)
config_oauth_code_pkce_code_verifier_db_path = os.path.join(
    config_oauth_code_pkce_store_dir, "code_verifiers"
)
