import dbm
import json
from threading import RLock

from pydantic import BaseModel

from config_oauth_authorization_server import (
    config_oauth_authorization_server_session_db_path,
)
from helper_pkce import helper_pkce_code_verifier

rlock = RLock()


class Session(BaseModel):
    value: dict
    sub: str | None
    csrf: str | None


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
