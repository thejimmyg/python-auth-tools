import os
import urllib.parse

config_store_dir = os.environ.get("STORE_DIR", "/tmp/store")
config_tmp_dir = os.environ.get("TMP_DIR", "/tmp/tmp")
config_url = os.environ.get("URL", "http://localhost:16001")
assert not config_url.endswith("/")

# Config derived from the core variables above

# URL related
_parsed_url = urllib.parse.urlparse(config_url)
config_host = _parsed_url.netloc.split(":")[0]
config_scheme = _parsed_url.scheme
if ':' in _parsed_url.netloc:
    config_port = int(":".join(_parsed_url.netloc.split(":")[1:]))
else:
    if config_scheme == 'https':
        config_port = 443
    elif config_scheme == 'http':
        config_port = 80
    else:
        raise Exception('Unknown scheme:' + str(config_scheme))
