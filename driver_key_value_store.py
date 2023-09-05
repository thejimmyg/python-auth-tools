import helper_hooks


def driver_key_value_store_put(*k, **p):
    return helper_hooks.hooks["driver_key_value_store_put"](*k, **p)


def driver_key_value_store_get(*k, **p):
    return helper_hooks.hooks["driver_key_value_store_get"](*k, **p)


def driver_key_value_store_del(*k, **p):
    return helper_hooks.hooks["driver_key_value_store_del"](*k, **p)
