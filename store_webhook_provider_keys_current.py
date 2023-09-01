import os
from datetime import datetime, timedelta
from threading import RLock

from cachetools import TTLCache, cached

rlock = RLock()
current_kid_value_cache = TTLCache(
    maxsize=10, ttl=timedelta(seconds=10), timer=datetime.now
)


if os.environ.get("STORE_MODE", "") != "dbm":
    from driver_key_value_store_sqlite import (
        driver_key_value_store_get,
        driver_key_value_store_put,
    )

    STORE = "webhook_provider_keys_current"

    def store_webhook_provider_keys_current_init():
        pass

    def store_webhook_provider_keys_current_cleanup():
        pass

    def store_webhook_provider_keys_current_put(kid: str):
        driver_key_value_store_put(STORE, "current", dict(kid=kid))

    @cached(cache=current_kid_value_cache, lock=rlock)
    def store_webhook_provider_keys_current_get_and_cache():
        return driver_key_value_store_get(STORE, "current")["kid"]

else:
    import dbm

    from config_webhook_provider import config_webhook_provider_keys_db_path

    _db = None

    def store_webhook_provider_keys_current_init():
        global _db
        _db = dbm.open(config_webhook_provider_keys_db_path, "c")

    def store_webhook_provider_keys_current_cleanup():
        _db.close()

    def store_webhook_provider_keys_current_put(kid: str):
        with rlock:
            _db[b"current"] = kid.encode("utf8")

    @cached(cache=current_kid_value_cache, lock=rlock)
    def store_webhook_provider_keys_current_get_and_cache():
        with rlock:
            return _db[b"current"].decode("utf8")
