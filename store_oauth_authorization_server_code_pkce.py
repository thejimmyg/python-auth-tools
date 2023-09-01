import dbm
import json
from threading import RLock

from pydantic import BaseModel

from config_oauth_authorization_server import (
    config_oauth_authorization_server_code_pkce_db_path,
)

rlock = RLock()


class CodePkce(BaseModel):
    redirect_uri: str
    scopes: list[str]


_db = None


def store_oauth_authorization_server_code_pkce_init():
    global _db
    _db = dbm.open(config_oauth_authorization_server_code_pkce_db_path, "c")


def store_oauth_authorization_server_code_pkce_cleanup():
    _db.close()


def store_oauth_authorization_server_code_pkce_put(client: str, code_pkce: CodePkce):
    with rlock:
        _db[client.encode("utf8")] = json.dumps(dict(code_pkce)).encode("utf8")


def store_oauth_authorization_server_code_pkce_get(client: str):
    with rlock:
        return CodePkce(**json.loads(_db[client.encode("utf8")].decode("utf8")))
