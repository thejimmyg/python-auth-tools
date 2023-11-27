"""
% echo 'create table if not exists store (pk text primary key, ttl number, value text);' | sqlite3 store/driver_key_value_store/sqlite.db
% python3 driver_key_value_store_sqlite.py
"""


import kvstore.driver

# assert os.environ.get("DRIVER_KEY_VALUE_STORE_TYPE", "sqlite3") == "sqlite3"
# config_store_dir = os.environ["STORE_DIR"]
# config_driver_key_value_store_dir = os.path.join(
#     config_store_dir, "driver_key_value_store"
# )
# os.makedirs(config_driver_key_value_store_dir, exist_ok=True)
# config_driver_key_value_store_db_path = os.path.join(
#     config_driver_key_value_store_dir, "sqlite.db"
# )


def driver_key_value_store_sqlite_init():
    pass


def driver_key_value_store_sqlite_cleanup():
    pass


def driver_key_value_store_sqlite_put(store: str, key: str, value, ttl=None):
    if type(value) is not dict:
        value = value.dict()
    return kvstore.driver.put(store=store, pk=key, data=value, ttl=ttl)


def driver_key_value_store_sqlite_del(store: str, key: str):
    return kvstore.driver.delete(store=store, pk=key)


def driver_key_value_store_sqlite_get(store: str, key: str):
    result, ttl = kvstore.driver.get(store=store, pk=key, consistent=True)
    return result
