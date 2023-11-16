from datetime import datetime, timedelta
from threading import RLock
from driver_key_value_store import (
    driver_key_value_store_get,
    driver_key_value_store_put,
)


from cachetools import TTLCache, cached

from driver_key_value_store import (
    driver_key_value_store_get,
    driver_key_value_store_put,
)

rlock = RLock()
current_kid_value_cache = TTLCache(
    maxsize=10, ttl=timedelta(seconds=10), timer=datetime.now
)


STORE = "oauth_authorization_server_jwks"


def store_oauth_authorization_server_jwks_put(jwks: str):
    driver_key_value_store_put(STORE, "current", dict(jwks=jwks))


@cached(cache=current_kid_value_cache, lock=rlock)
def store_oauth_authorization_server_jwks_get_and_cache():
    return driver_key_value_store_get(STORE, "current")["jwks"]


def store_oauth_authorization_server_jwks_get():
    return driver_key_value_store_get(STORE, "current")["jwks"]
