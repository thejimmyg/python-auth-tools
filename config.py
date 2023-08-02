import os
import urllib.parse

store_dir = os.environ.get("STORE_DIR", "./store")
tmpdir = os.environ.get("TMP_DIR", "./tmp")
url = os.environ.get("URL", "http://localhost:16001")
assert not url.endswith("/")

# Config derived from the core variables above

# URL related
_parsed_url = urllib.parse.urlparse(url)
host = _parsed_url.netloc.split(":")[0]
port = int(":".join(_parsed_url.netloc.split(":")[1:]))
scheme = _parsed_url.scheme

# oauth_authorization_server
oauth_authorization_server_store_dir = os.path.join(
    store_dir, "oauth_authorization_server"
)
os.makedirs(oauth_authorization_server_store_dir, exist_ok=True)
private_key_path = os.path.join(oauth_authorization_server_store_dir, "private.key")
clients_json_path = os.path.join(oauth_authorization_server_store_dir, "clients.json")
oauth_authorization_server_store_codes_dbpath = os.path.join(
    oauth_authorization_server_store_dir, "code"
)
oauth_authorization_server_store_session_dbpath = os.path.join(
    oauth_authorization_server_store_dir, "session"
)
oauth_authorization_server_openid_configuration = os.path.join(
    oauth_authorization_server_store_dir, "openid-configuration"
)
oauth_authorization_server_jwks_json = os.path.join(
    oauth_authorization_server_store_dir, "jwks.json"
)


# oauth_client_flow_code_pkce_store_dir
oauth_client_flow_code_pkce_store_dir = os.path.join(
    store_dir, "oauth_client_flow_code_pkce"
)
os.makedirs(oauth_client_flow_code_pkce_store_dir, exist_ok=True)
oauth_authorization_server_store_code_verifier_dbpath = os.path.join(
    oauth_client_flow_code_pkce_store_dir, "code_verifier"
)


# static
gzipped_dir = os.path.join(tmpdir, "gzipped")
