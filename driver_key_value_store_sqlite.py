"""
% echo 'create table if not exists store (pk text primary key, ttl number, value text);' | sqlite3 store/driver_key_value_store/sqlite.db
% python3 driver_key_value_store_sqlite.py
"""

import kvstore.driver
import math
import time

import os

assert os.environ.get("DRIVER_KEY_VALUE_STORE_TYPE", "sqlite3") == 'sqlite3'
config_store_dir = os.environ["STORE_DIR"]
config_driver_key_value_store_dir = os.path.join(
    config_store_dir, "driver_key_value_store"
)
os.makedirs(config_driver_key_value_store_dir, exist_ok=True)
config_driver_key_value_store_db_path = os.path.join(
    config_driver_key_value_store_dir, "sqlite.db"
)



from store import NotFoundInStoreDriver

def driver_key_value_store_sqlite_init():
    pass

def driver_key_value_store_sqlite_cleanup():
    pass

def driver_key_value_store_sqlite_put(store: str, key: str, value, ttl=None):
    return kvstore.driver.put(store=store, pk=key, data=value, ttl=ttl)

def driver_key_value_store_sqlite_del(store: str, key: str):
    return kvstore.driver.delete(store=store, pk=key)

def driver_key_value_store_sqlite_get(store: str, key: str):
    results, next_ = kvstore.driver.iterate(store=store, pk=key, consistent=True)
    # Maybe 1MB was expired data, let's just try once more
    # if len(results) == 0 and next_ is not None:
    #     results, next_ = kvstore.driver.iterate(store=store, pk=key, consistent=True, sk_start=next_, after=True)
    assert len(results) == 1, results
    assert next_ is None
    sk, result, ttl = results[0]
    assert sk == "/", sk
    return result
