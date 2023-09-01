import dbm
import json
from threading import RLock

from pydantic import BaseModel

from config_oauth_code_pkce import config_oauth_code_pkce_code_verifier_db_path

rlock = RLock()


class CodeVerifier(BaseModel):
    code_verifier: str


_db = None


def store_oauth_code_pkce_code_verifier_init():
    global _db
    _db = dbm.open(config_oauth_code_pkce_code_verifier_db_path, "c")


def store_oauth_code_pkce_code_verifier_cleanup():
    _db.close()


def store_oauth_code_pkce_code_verifier_put(state: str, code_verifier: CodeVerifier):
    with rlock:
        _db[state.encode("utf8")] = json.dumps(dict(code_verifier)).encode("utf8")


def store_oauth_code_pkce_code_verifier_get_and_delete(state: str):
    with rlock:
        result = CodeVerifier(**json.loads(_db[state.encode("utf8")].decode("utf8")))
        del _db[state.encode("utf8")]
        return result
