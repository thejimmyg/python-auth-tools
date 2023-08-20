import dbm
from datetime import datetime, timedelta
from threading import Lock

from cachetools import TTLCache, cached

from config_oauth_authorization_server import (
    oauth_authorization_server_store_keys_dbpath,
)

_db = None


def oauth_authorization_server_keys_init():
    global _db
    _db = dbm.open(oauth_authorization_server_store_keys_dbpath, "c")


def oauth_authorization_server_keys_cleanup():
    _db.close()


def put_current_kid_value(kid: str):
    _db[b"current"] = kid.encode("utf8")


current_kid_value_cache = TTLCache(
    maxsize=10, ttl=timedelta(seconds=10), timer=datetime.now
)


@cached(cache=current_kid_value_cache, lock=Lock())
def get_and_cache_current_kid_value():
    return _db[b"current"].decode("utf8")
