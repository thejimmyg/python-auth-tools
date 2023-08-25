import dbm
import json

from pydantic import BaseModel

from config_oauth_authorization_server import (
    config_oauth_authorization_server_sessions_db_path,
)


class SessionValue(BaseModel):
    code: str


_db = None


def store_oauth_authorization_server_session_init():
    global _db
    _db = dbm.open(config_oauth_authorization_server_sessions_db_path, "c")


def store_oauth_authorization_server_session_cleanup():
    _db.close()


def store_oauth_authorization_server_session_put(
    session: str, session_value: SessionValue
):
    _db[session.encode("utf8")] = json.dumps(dict(session_value)).encode("utf8")


def store_oauth_authorization_server_session_get(session: str):
    return SessionValue(**json.loads(_db[session.encode("utf8")].decode("utf8")))
