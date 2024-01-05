from datetime import datetime, timedelta
from threading import RLock

from cachetools import TTLCache, cached

import kvstore.driver

rlock = RLock()
current_kid_value_cache = TTLCache(
    maxsize=10, ttl=timedelta(seconds=10), timer=datetime.now
)


STORE = "oauth_authorization_server_keys_current"


def store_oauth_authorization_server_keys_current_put(kid: str):
    kvstore.driver.put(STORE, "current", dict(kid=kid))


@cached(cache=current_kid_value_cache, lock=rlock)
def store_oauth_authorization_server_keys_current_get_and_cache():
    values, ttl = kvstore.driver.get(STORE, "current", consistent=True)
    return values["kid"]
