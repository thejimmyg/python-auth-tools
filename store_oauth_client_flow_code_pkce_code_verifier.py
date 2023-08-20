import dbm
import json

from pydantic import BaseModel

from config_oauth_client import oauth_client_flow_code_pkce_code_verifier_dbpath


class CodeVerifierValue(BaseModel):
    code_verifier: str


_db = None


def oauth_client_flow_code_pkce_code_verifier_init():
    global _db
    _db = dbm.open(oauth_client_flow_code_pkce_code_verifier_dbpath, "c")


def oauth_client_flow_code_pkce_code_verifier_cleanup():
    _db.close()


def put_code_verifier_value(state: str, code_verifier_value: CodeVerifierValue):
    _db[state.encode("utf8")] = json.dumps(dict(code_verifier_value)).encode("utf8")


def get_and_delete_code_verifier_value(state: str):
    result = CodeVerifierValue(**json.loads(_db[state.encode("utf8")].decode("utf8")))
    del _db[state.encode("utf8")]
    return result
