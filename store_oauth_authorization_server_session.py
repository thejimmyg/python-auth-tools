import dbm
import json

from pydantic import BaseModel

from config_oauth_authorization_server import (
    oauth_authorization_server_store_session_dbpath,
)


class SessionValue(BaseModel):
    code: str


def put_session_value(session: str, session_value: SessionValue):
    with dbm.open(oauth_authorization_server_store_session_dbpath, "c") as db:
        db[session.encode("utf8")] = json.dumps(dict(session_value)).encode("utf8")


def get_session_value(session: str):
    with dbm.open(oauth_authorization_server_store_session_dbpath, "c") as db:
        result = SessionValue(**json.loads(db[session.encode("utf8")].decode("utf8")))
    return result
