from datetime import datetime, timedelta
from threading import RLock

from cachetools import TTLCache, cached

from driver_key_value_store_sqlite import (
    driver_key_value_store_get,
    driver_key_value_store_put,
)

rlock = RLock()
current_kid_value_cache = TTLCache(
    maxsize=10, ttl=timedelta(seconds=10), timer=datetime.now
)


STORE = "oauth_authorization_server_keys_current"


def store_oauth_authorization_server_keys_current_put(kid: str):
    driver_key_value_store_put(STORE, "current", dict(kid=kid))


@cached(cache=current_kid_value_cache, lock=rlock)
def store_oauth_authorization_server_keys_current_get_and_cache():
    return driver_key_value_store_get(STORE, "current")["kid"]
