import os

from pydantic import BaseModel

from helper_pkce import helper_pkce_code_verifier


class Session(BaseModel):
    value: dict
    sub: str | None
    csrf: str | None


if os.environ.get("STORE_MODE", "") != "dbm":
    import time

    from driver_key_value_store_sqlite import (
        driver_key_value_store_del,
        driver_key_value_store_get,
        driver_key_value_store_put,
    )

    STORE = "session"

    def store_session_init():
        pass

    def store_session_cleanup():
        pass

    def store_session_put(session_id: str, session: Session):
        assert session_id
        if session.csrf is None:
            session.csrf = helper_pkce_code_verifier()
        # Valid for 16 hours
        driver_key_value_store_put(
            STORE, session_id, session, ttl=time.time() + (16 * 60 * 60)
        )

    def store_session_get(session_id: str):
        assert session_id
        return Session(**driver_key_value_store_get(STORE, session_id))

    def store_session_destroy(session_id: str):
        assert session_id
        driver_key_value_store_del(STORE, session_id)

    def store_session_set_sub(session_id: str, sub: str):
        assert session_id
        session = store_session_get(session_id)
        session.sub = sub
        store_session_put(session_id, session)

else:
    import dbm
    import json
    from threading import RLock

    from config_oauth_authorization_server import (
        config_oauth_authorization_server_session_db_path,
    )

    rlock = RLock()

    _db = None

    def store_session_init():
        global _db
        _db = dbm.open(config_oauth_authorization_server_session_db_path, "c")

    def store_session_cleanup():
        _db.close()

    def store_session_put(session_id: str, session: Session):
        with rlock:
            assert session_id
            if session.csrf is None:
                session.csrf = helper_pkce_code_verifier()
            _db[session_id.encode("utf8")] = json.dumps(dict(session)).encode("utf8")

    def store_session_get(session_id: str):
        with rlock:
            assert session_id
            return Session(**json.loads(_db[session_id.encode("utf8")].decode("utf8")))

    def store_session_destroy(session_id: str):
        with rlock:
            assert session_id
            del _db[session_id.encode("utf8")]

    def store_session_set_sub(session_id: str, sub: str):
        with rlock:
            assert session_id
            session = store_session_get(session_id)
            session.sub = sub
            store_session_put(session_id, session)
