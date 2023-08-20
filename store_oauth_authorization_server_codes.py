import dbm
import json

from pydantic import BaseModel

from config_oauth_authorization_server import (
    oauth_authorization_server_store_codes_dbpath,
)


class CodeValue(BaseModel):
    client_id: str
    code_challenge: str
    scopes: list[str] | None
    state: str | None
    sub: str | None


_db = None


def oauth_authorization_server_codes_init():
    global _db
    _db = dbm.open(oauth_authorization_server_store_codes_dbpath, "c")


def oauth_authorization_server_codes_cleanup():
    _db.close()


def put_code_value(code: str, code_value: CodeValue):
    _db[code.encode("utf8")] = json.dumps(dict(code_value)).encode("utf8")


def set_code_sub(code: str, sub: str):
    code_value = CodeValue(**json.loads(_db[code.encode("utf8")].decode("utf8")))
    code_value.sub = sub
    _db[code.encode("utf8")] = json.dumps(dict(code_value)).encode("utf8")


def get_and_delete_code_value(code: str):
    result = CodeValue(**json.loads(_db[code.encode("utf8")].decode("utf8")))
    del _db[code.encode("utf8")]
    return result


def get_code_value(code: str):
    return CodeValue(**json.loads(_db[code.encode("utf8")].decode("utf8")))
