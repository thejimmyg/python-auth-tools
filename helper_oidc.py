import json
import urllib.request
from datetime import datetime, timedelta
from threading import Lock

from cachetools import TTLCache, cached

oidc_cache = TTLCache(maxsize=10, ttl=timedelta(seconds=300), timer=datetime.now)


@cached(cache=oidc_cache, lock=Lock())
def fetch_and_cache_openid_configuration(issuer):
    with urllib.request.urlopen(issuer + "/.well-known/openid-configuration") as fp:
        return json.loads(fp.read())


jwks_cache = TTLCache(maxsize=10, ttl=timedelta(seconds=3600), timer=datetime.now)


@cached(cache=jwks_cache, lock=Lock())
def fetch_and_cache_jwks_for_kid(jwks_url, kid):
    with urllib.request.urlopen(jwks_url) as fp:
        return json.loads(fp.read())
