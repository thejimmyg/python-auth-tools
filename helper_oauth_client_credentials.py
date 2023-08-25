import base64
import json
import urllib.request

from helper_log import helper_log


def helper_oauth_client_credentials_token(token_endpoint, client, secret, scopes=None):
    if scopes is None:
        scopes = []
    request = urllib.request.Request(
        token_endpoint
        + "?grant_type=client_credentials&scope="
        + urllib.parse.quote(" ".join(scopes)),
        headers={
            "Authorization": "Basic "
            + base64.b64encode((client + ":" + secret).encode("utf8")).decode("utf8")
        },
    )
    try:
        with urllib.request.urlopen(request) as fp:
            response = json.loads(fp.read())
    except urllib.error.HTTPError as e:
        helper_log(__file__, "ERROR:", e.read().decode())
        raise
    return response
