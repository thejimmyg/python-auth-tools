import dbm
import json

from pydantic import BaseModel

from config import oauth_authorization_server_store_codes_dbpath


class CodeValue(BaseModel):
    client_id: str
    code_challenge: str
    scopes: list[str] | None
    state: str | None
    sub: str | None


def put_code_value(code: str, code_value: CodeValue):
    with dbm.open(oauth_authorization_server_store_codes_dbpath, "c") as db:
        db[code.encode("utf8")] = json.dumps(dict(code_value)).encode("utf8")


def set_code_sub(code: str, sub: str):
    with dbm.open(oauth_authorization_server_store_codes_dbpath, "c") as db:
        code_value = CodeValue(**json.loads(db[code.encode("utf8")].decode("utf8")))
        code_value.sub = sub
        db[code.encode("utf8")] = json.dumps(dict(code_value)).encode("utf8")


def get_and_delete_code_value(code: str):
    with dbm.open(oauth_authorization_server_store_codes_dbpath, "c") as db:
        result = CodeValue(**json.loads(db[code.encode("utf8")].decode("utf8")))
        del db[code.encode("utf8")]
    return result


def get_code_value(code: str):
    with dbm.open(oauth_authorization_server_store_codes_dbpath, "c") as db:
        return CodeValue(**json.loads(db[code.encode("utf8")].decode("utf8")))
