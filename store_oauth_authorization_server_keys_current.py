import dbm
from datetime import datetime, timedelta
from threading import Lock

from cachetools import TTLCache, cached

from config_oauth_authorization_server import (
    config_oauth_authorization_server_keys_db_path,
)

_db = None


def store_oauth_authorization_server_keys_current_init():
    global _db
    _db = dbm.open(config_oauth_authorization_server_keys_db_path, "c")


def store_oauth_authorization_server_keys_current_cleanup():
    _db.close()


def store_oauth_authorization_server_keys_current_put(kid: str):
    _db[b"current"] = kid.encode("utf8")


current_kid_value_cache = TTLCache(
    maxsize=10, ttl=timedelta(seconds=10), timer=datetime.now
)


@cached(cache=current_kid_value_cache, lock=Lock())
def store_oauth_authorization_server_keys_current_get_and_cache():
    return _db[b"current"].decode("utf8")
