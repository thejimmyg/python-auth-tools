import dbm
import json

from pydantic import BaseModel

from config_oauth_authorization_server import (
    config_oauth_authorization_server_session_db_path,
)


class Session(BaseModel):
    value: dict
    sub: str | None


_db = None


def store_session_init():
    global _db
    _db = dbm.open(config_oauth_authorization_server_session_db_path, "c")


def store_session_cleanup():
    _db.close()


def store_session_put(session_id: str, session_value: Session):
    _db[session_id.encode("utf8")] = json.dumps(dict(session_value)).encode("utf8")


def store_session_get(session_id: str):
    return Session(**json.loads(_db[session_id.encode("utf8")].decode("utf8")))


def store_session_set_sub(session_id: str, sub: str):
    session_value = store_session_get(session_id)
    session_value.sub = sub
    store_session_put(session_id, session_value)
