"""
% echo 'create table if not exists store (pk text primary key, ttl number, value text);' | sqlite3 store/driver_key_value_store/sqlite.db
% python3 driver_key_value_store_sqlite.py
"""

import json
import sqlite3
import time
from threading import RLock

from config_driver_key_value_store import config_driver_key_value_store_db_path
from store import NotFoundInStoreDriver

# This might not be needed if we create a cursor within each function, but I don't know enough about the underlying implementation to be sure.
rlock = RLock()


def get_sqlite3_thread_safety():
    # Mape value from SQLite's THREADSAFE to Python's DBAPI 2.0
    # threadsafety attribute.
    sqlite_threadsafe2python_dbapi = {0: 0, 2: 1, 1: 3}
    conn = sqlite3.connect(":memory:")
    threadsafety = conn.execute(
        """
select * from pragma_compile_options
where compile_options like 'THREADSAFE=%'
"""
    ).fetchone()[0]
    conn.close()
    threadsafety_value = int(threadsafety.split("=")[1])
    return sqlite_threadsafe2python_dbapi[threadsafety_value]


if get_sqlite3_thread_safety() == 3:
    check_same_thread = False
else:
    check_same_thread = True


_conn = None
_cur = None


def driver_key_value_store_sqlite_init():
    global _conn
    global _cur
    with rlock:
        if not _conn or not _cur:
            # See https://ricardoanderegg.com/posts/python-sqlite-thread-safety/
            _conn = sqlite3.connect(
                config_driver_key_value_store_db_path,
                check_same_thread=check_same_thread,
            )
            _cur = _conn.cursor()
            _cur.execute(
                "create table if not exists store (pk text primary key, ttl number, value text NOT NULL);"
            )
            _cur.execute(
                "create index if not exists store_ttl on store (ttl) where ttl is not NULL;"
            )


def driver_key_value_store_sqlite_cleanup():
    with rlock:
        if _conn:
            _conn.close()


def _make_key(store, key):
    return store + " " + key


def driver_key_value_store_sqlite_put(store: str, key: str, value, ttl=None):
    cols = ["pk", "ttl", "value"]
    pk = _make_key(store, key)
    values = [pk, ttl, json.dumps(dict(value))]

    with rlock:
        sql = (
            "INSERT OR REPLACE INTO "
            + "store"
            + "("
            + (", ".join(cols))
            + ") VALUES ("
            + (", ".join(["?" for v in values]))
            + ")"
        )
        # helper_log(__file__, sql, values)
        _cur.execute(sql, values)
        # Since we need to make a commit anyway, cleanup exired items
        _cur.execute(
            "delete from store where ttl is not NULL AND ttl <= ?", (time.time(),)
        )
        _conn.commit()


def driver_key_value_store_sqlite_del(store: str, key: str):
    pk = _make_key(store, key)

    with rlock:
        sql = "DELETE FROM " + "store" + " WHERE pk=?"
        # helper_log(__file__, sql, pk)
        _cur.execute(sql, (pk,))
        # Since we need to make a commit anyway, cleanup exired items
        _cur.execute(
            "delete from store where ttl is not NULL AND ttl <= ?", (time.time(),)
        )
        _conn.commit()


def driver_key_value_store_sqlite_get(store: str, key: str):
    with rlock:
        pk = _make_key(store, key)
        # Only return unexpired items
        _cur.execute(
            "select value from store where pk = ? AND (ttl is NULL OR ttl > ?)",
            (pk, time.time()),
        )
        rows = _cur.fetchall()
        # helper_log(__file__, len(rows), rows)
        if len(rows) == 0:
            raise NotFoundInStoreDriver(f"No such key '{key}' in the store")
        return json.loads(rows[0][0])
