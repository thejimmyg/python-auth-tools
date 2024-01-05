from datetime import datetime, timedelta
from threading import RLock
from cachetools import TTLCache, cached
import kvstore.driver


rlock = RLock()
current_kid_value_cache = TTLCache(
    maxsize=10, ttl=timedelta(seconds=10), timer=datetime.now
)


STORE = "webhook_provider_jwks"


def store_webhook_provider_jwks_put(jwks: str):
    kvstore.driver.put(STORE, "current", dict(jwks=jwks))


@cached(cache=current_kid_value_cache, lock=rlock)
def store_webhook_provider_jwks_get_and_cache():
    return store_webhook_provider_jwks_get()


def store_webhook_provider_jwks_get():
    values, ttl = kvstore.driver.get(STORE, "current", consistent=True)
    return values["jwks"]
