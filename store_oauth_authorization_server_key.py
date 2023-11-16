from datetime import datetime, timedelta
from threading import RLock

from cachetools import TTLCache, cached

from driver_key_value_store import (
    driver_key_value_store_get,
    driver_key_value_store_put,
)

rlock = RLock()
kid_value_cache = TTLCache(maxsize=10, ttl=timedelta(seconds=60), timer=datetime.now)

import json

STORE = "oauth_authorization_server_key"


def store_oauth_authorization_server_key_put(kid: str, key: str):
    driver_key_value_store_put(STORE, kid, dict(key=key))


@cached(cache=kid_value_cache, lock=rlock)
def store_oauth_authorization_server_key_get_and_cache(kid):
    return json.loads(driver_key_value_store_get(STORE, kid)["key"])
