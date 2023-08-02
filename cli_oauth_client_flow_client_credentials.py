import base64
import urllib.request
import sys
import json
from cli_oauth_resource_owner_verify_jwt import verify_jwt
import config

issuer = config.url
client = sys.argv[1]
secret = sys.argv[2]

with urllib.request.urlopen(issuer + "/.well-known/openid-configuration") as fp:
    oidc = json.loads(fp.read())

request = urllib.request.Request(
    oidc["token_endpoint"] + "?grant_type=client_credentials",
    headers={
        "Authorization": "Basic "
        + base64.b64encode((client + ":" + secret).encode("utf8")).decode("utf8")
    },
)

try:
    with urllib.request.urlopen(request) as fp:
        response = json.loads(fp.read())
        print(response)
        print(verify_jwt(response["access_token"]))
except urllib.error.HTTPError as e:
    print("ERROR:", e.read().decode())
    raise
