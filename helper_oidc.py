import json
import urllib.request


def fetch_openid_configuration(issuer):
    with urllib.request.urlopen(issuer + "/.well-known/openid-configuration") as fp:
        return json.loads(fp.read())
