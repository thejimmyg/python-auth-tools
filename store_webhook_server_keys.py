import dbm

from config_webhook import webhook_store_keys_dbpath


def put_current_kid_value(kid: str):
    with dbm.open(webhook_store_keys_dbpath, "c") as db:
        db[b"current"] = kid.encode("utf8")


def get_current_kid_value():
    with dbm.open(webhook_store_keys_dbpath, "c") as db:
        return db[b"current"].decode("utf8")
