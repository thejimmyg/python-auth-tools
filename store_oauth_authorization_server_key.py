from datetime import datetime, timedelta
from threading import RLock
from cachetools import TTLCache, cached
import json
import kvstore.driver

rlock = RLock()
kid_value_cache = TTLCache(maxsize=10, ttl=timedelta(seconds=60), timer=datetime.now)


STORE = "oauth_authorization_server_key"


def store_oauth_authorization_server_key_put(kid: str, key: str):
    kvstore.driver.put(STORE, kid, {"key": key})


@cached(cache=kid_value_cache, lock=rlock)
def store_oauth_authorization_server_key_get_and_cache(kid):
    result, ttl = kvstore.driver.get(STORE, kid, consistent=True)
    return json.loads(result["key"])
