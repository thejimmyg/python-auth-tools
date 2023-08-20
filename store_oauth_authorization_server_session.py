import dbm
import json

from pydantic import BaseModel

from config_oauth_authorization_server import (
    oauth_authorization_server_store_session_dbpath,
)


class SessionValue(BaseModel):
    code: str


_db = None


def oauth_authorization_server_session_init():
    global _db
    _db = dbm.open(oauth_authorization_server_store_session_dbpath, "c")


def oauth_authorization_server_session_cleanup():
    _db.close()


def put_session_value(session: str, session_value: SessionValue):
    _db[session.encode("utf8")] = json.dumps(dict(session_value)).encode("utf8")


def get_session_value(session: str):
    return SessionValue(**json.loads(_db[session.encode("utf8")].decode("utf8")))
