import dbm
import json

from pydantic import BaseModel

from config_oauth_client import oauth_client_store_code_verifier_dbpath


class CodeVerifierValue(BaseModel):
    code_verifier: str


def put_code_verifier_value(state: str, code_verifier_value: CodeVerifierValue):
    with dbm.open(oauth_client_store_code_verifier_dbpath, "c") as db:
        db[state.encode("utf8")] = json.dumps(dict(code_verifier_value)).encode("utf8")


def get_and_delete_code_verifier_value(state: str):
    with dbm.open(oauth_client_store_code_verifier_dbpath, "c") as db:
        result = CodeVerifierValue(
            **json.loads(db[state.encode("utf8")].decode("utf8"))
        )
        del db[state.encode("utf8")]
    return result
