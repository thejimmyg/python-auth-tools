from datetime import datetime, timedelta
from threading import RLock

from cachetools import TTLCache, cached

rlock = RLock()
current_kid_value_cache = TTLCache(
    maxsize=10, ttl=timedelta(seconds=10), timer=datetime.now
)


import kvstore.driver

STORE = "webhook_provider_keys_current"


def store_webhook_provider_keys_current_put(kid: str):
    kvstore.driver.put(STORE, "current", dict(kid=kid))


@cached(cache=current_kid_value_cache, lock=rlock)
def store_webhook_provider_keys_current_get_and_cache():
    values, ttl = driver_key_value_store_get(STORE, "current")
    return values["kid"]
