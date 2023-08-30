import dbm
import json

from pydantic import BaseModel

from config_oauth_authorization_server import (
    config_oauth_authorization_server_session_db_path,
)
from helper_pkce import helper_pkce_code_verifier


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
    if session.csrf is None:
        session.csrf = helper_pkce_code_verifier()
    _db[session_id.encode("utf8")] = json.dumps(dict(session)).encode("utf8")


def store_session_get(session_id: str):
    return Session(**json.loads(_db[session_id.encode("utf8")].decode("utf8")))


def store_session_set_sub(session_id: str, sub: str):
    session = store_session_get(session_id)
    session.sub = sub
    store_session_put(session_id, session)
