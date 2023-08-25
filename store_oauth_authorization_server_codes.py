import dbm
import json

from pydantic import BaseModel

from config_oauth_authorization_server import (
    config_oauth_authorization_server_codes_db_path,
)


class CodeValue(BaseModel):
    client_id: str
    code_challenge: str
    scopes: list[str] | None
    state: str | None
    sub: str | None


_db = None


def store_oauth_authorization_server_codes_init():
    global _db
    _db = dbm.open(config_oauth_authorization_server_codes_db_path, "c")


def store_oauth_authorization_server_codes_cleanup():
    _db.close()


def store_oauth_authorization_server_codes_put(code: str, code_value: CodeValue):
    _db[code.encode("utf8")] = json.dumps(dict(code_value)).encode("utf8")


def store_oauth_authorization_server_codes_set_sub(code: str, sub: str):
    code_value = CodeValue(**json.loads(_db[code.encode("utf8")].decode("utf8")))
    code_value.sub = sub
    _db[code.encode("utf8")] = json.dumps(dict(code_value)).encode("utf8")


def store_oauth_authorization_server_codes_get_and_delete(code: str):
    result = CodeValue(**json.loads(_db[code.encode("utf8")].decode("utf8")))
    del _db[code.encode("utf8")]
    return result


def get_code_value(code: str):
    return CodeValue(**json.loads(_db[code.encode("utf8")].decode("utf8")))
