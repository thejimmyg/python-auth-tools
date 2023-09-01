import dbm
import json
from threading import RLock

from pydantic import BaseModel

from config_oauth_authorization_server import (
    config_oauth_authorization_server_code_pkce_request_db_path,
)

rlock = RLock()


class CodePkceRequest(BaseModel):
    client_id: str
    code_challenge: str
    scopes: list[str] | None
    state: str | None
    sub: str | None


_db = None


def store_oauth_authorization_server_code_pkce_request_init():
    global _db
    _db = dbm.open(config_oauth_authorization_server_code_pkce_request_db_path, "c")


def store_oauth_authorization_server_code_pkce_request_cleanup():
    _db.close()


def store_oauth_authorization_server_code_pkce_request_put(
    code: str, code_pkce_request: CodePkceRequest
):
    with rlock:
        _db[code.encode("utf8")] = json.dumps(dict(code_pkce_request)).encode("utf8")


def store_oauth_authorization_server_code_pkce_request_get_and_delete(code: str):
    with rlock:
        result = CodePkceRequest(**json.loads(_db[code.encode("utf8")].decode("utf8")))
        del _db[code.encode("utf8")]
        return result


def store_oauth_authorization_code_pkce_request_get(code: str):
    with rlock:
        return CodePkceRequest(**json.loads(_db[code.encode("utf8")].decode("utf8")))


def store_oauth_authorization_server_code_pkce_request_set_sub(code: str, sub: str):
    with rlock:
        code_pkce_request = store_oauth_authorization_code_pkce_request_get(code)
        code_pkce_request.sub = sub
        store_oauth_authorization_server_code_pkce_request_put(code, code_pkce_request)
