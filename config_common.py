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


# static
gzipped_dir = os.path.join(tmpdir, "gzipped")
