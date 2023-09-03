import helper_hooks
from driver_key_value_store_sqlite import (
    driver_key_value_store_sqlite_del,
    driver_key_value_store_sqlite_get,
    driver_key_value_store_sqlite_put,
)


def driver_key_value_store_put(*k, **p):
    return helper_hooks.hooks.get(
        "driver_key_value_store_put", driver_key_value_store_sqlite_put
    )(*k, **p)


def driver_key_value_store_get(*k, **p):
    return helper_hooks.hooks.get(
        "driver_key_value_store_get", driver_key_value_store_sqlite_get
    )(*k, **p)


def driver_key_value_store_del(*k, **p):
    return helper_hooks.hooks.get(
        "driver_key_value_store_del", driver_key_value_store_sqlite_del
    )(*k, **p)
