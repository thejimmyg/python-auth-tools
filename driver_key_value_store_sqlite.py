"""
% echo 'create table if not exists store (pk text primary key, ttl number, value text);' | sqlite3 store/driver_key_value_store/sqlite.db
% python3 driver_key_value_store_sqlite.py
"""

import json
import sqlite3
import time
from threading import RLock

from config_driver_key_value_store import config_driver_key_value_store_db_path

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
        return json.loads(rows[0][0])


if __name__ == "__main__":
    import time

    driver_key_value_store_sqlite_init()
    driver_key_value_store_put(
        store="test",
        key="foo1",
        value=dict(banana=3.14, foo="hello"),
        ttl=time.time() + 0.1,
    )
    print(driver_key_value_store_get(store="test", key="foo1"))

    driver_key_value_store_put(
        store="test",
        key="foo1",
        value=dict(banana=3.15, foo="goodbye"),
        ttl=time.time() + 0.1,
    )
    result = driver_key_value_store_get(store="test", key="foo1")
    assert result == {"banana": 3.15, "foo": "goodbye"}, result
    print("Updated foo1 successfully")
    driver_key_value_store_put(
        store="test",
        key="foo1",
        value=dict(banana=3.16, foo="bye"),
    )
    result = driver_key_value_store_get(store="test", key="foo1")
    assert result == {"banana": 3.16, "foo": "bye"}, result
    print("Updated foo1 successfully without a ttl")

    time.sleep(0.11)
    result = driver_key_value_store_get(store="test", key="foo1")
    assert result == {"banana": 3.16, "foo": "bye"}, result
    print("foo1 is still there after the ttl time")

    driver_key_value_store_put(
        store="test", key="foo2", value=dict(banana=3.14, foo="hello")
    )
    print(driver_key_value_store_get(store="test", key="foo2"))
    driver_key_value_store_put(
        store="test", key="foo3", value=dict(banana=3.14, foo="hello"), ttl=time.time()
    )
    try:
        print(driver_key_value_store_get(store="test", key="foo3"))
    except:
        print("Cannot print foo3 since it has already expired")
    else:
        raise Exception("Showed the foo3 result when it should have expired")

    driver_key_value_store_put(
        store="test", key="foo4", value=dict(banana=3.14, foo="hello")
    )
    driver_key_value_store_del(store="test", key="foo4")

    try:
        print(driver_key_value_store_get(store="test", key="foo4"))
    except:
        print("Cannot print foo4 since it has been successfully deleted")
    else:
        raise Exception("Showed the foo4 result when it should have expired")

    driver_key_value_store_sqlite_cleanup()
