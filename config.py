import os
import urllib.parse

config_store_dir = os.environ.get("STORE_DIR", "./store")
config_tmp_dir = os.environ.get("TMP_DIR", "./tmp")
config_url = os.environ.get("URL", "http://localhost:16001")
assert not config_url.endswith("/")

# Config derived from the core variables above

# URL related
_parsed_url = urllib.parse.urlparse(config_url)
config_host = _parsed_url.netloc.split(":")[0]
config_port = int(":".join(_parsed_url.netloc.split(":")[1:]))
config_scheme = _parsed_url.scheme
