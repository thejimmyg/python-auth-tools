import os
import time

from pydantic import BaseModel


class CodeVerifier(BaseModel):
    code_verifier: str


if os.environ.get("STORE_MODE", "") != "dbm":
    from driver_key_value_store_sqlite import (
        driver_key_value_store_del,
        driver_key_value_store_get,
        driver_key_value_store_put,
    )

    STORE = "oauth_code_pkce_code_verifier"

    def store_oauth_code_pkce_code_verifier_init():
        pass

    def store_oauth_code_pkce_code_verifier_cleanup():
        pass

    def store_oauth_code_pkce_code_verifier_put(
        state: str, code_verifier: CodeVerifier
    ):
        # Allow 5 mins for the flow (to allow for login and consent)
        driver_key_value_store_put(
            STORE, state, code_verifier, ttl=time.time() + (5 * 60)
        )

    def store_oauth_code_pkce_code_verifier_get_and_delete(state: str):
        result = CodeVerifier(**driver_key_value_store_get(STORE, state))
        driver_key_value_store_del(STORE, state)
        return result

else:
    import dbm
    import json
    from threading import RLock

    from config_oauth_code_pkce import config_oauth_code_pkce_code_verifier_db_path

    rlock = RLock()

    _db = None

    def store_oauth_code_pkce_code_verifier_init():
        global _db
        _db = dbm.open(config_oauth_code_pkce_code_verifier_db_path, "c")

    def store_oauth_code_pkce_code_verifier_cleanup():
        _db.close()

    def store_oauth_code_pkce_code_verifier_put(
        state: str, code_verifier: CodeVerifier
    ):
        with rlock:
            _db[state.encode("utf8")] = json.dumps(dict(code_verifier)).encode("utf8")

    def store_oauth_code_pkce_code_verifier_get_and_delete(state: str):
        with rlock:
            result = CodeVerifier(
                **json.loads(_db[state.encode("utf8")].decode("utf8"))
            )
            del _db[state.encode("utf8")]
            return result
