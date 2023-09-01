import os

from pydantic import BaseModel


class CodePkceRequest(BaseModel):
    client_id: str
    code_challenge: str
    scopes: list[str] | None
    state: str | None
    sub: str | None


if os.environ.get("STORE_MODE", "") != "dbm":
    import time

    from driver_key_value_store_sqlite import (
        driver_key_value_store_del,
        driver_key_value_store_get,
        driver_key_value_store_put,
    )

    STORE = "oauth_authorization_server_code_pkce_request"

    def store_oauth_authorization_server_code_pkce_request_init():
        pass

    def store_oauth_authorization_server_code_pkce_request_cleanup():
        pass

    def store_oauth_authorization_server_code_pkce_request_put(
        code: str, code_pkce_request: CodePkceRequest
    ):
        # Allow the code to be valid for 30 seconds
        driver_key_value_store_put(STORE, code, code_pkce_request, ttl=time.time() + 30)

    def store_oauth_authorization_server_code_pkce_request_get_and_delete(code: str):
        result = CodePkceRequest(**driver_key_value_store_get(STORE, code))
        result = store_oauth_authorization_code_pkce_request_get(code)
        driver_key_value_store_del(STORE, code)
        return result

    def store_oauth_authorization_code_pkce_request_get(code: str):
        return CodePkceRequest(**driver_key_value_store_get(STORE, code))

    def store_oauth_authorization_server_code_pkce_request_set_sub(code: str, sub: str):
        code_pkce_request = store_oauth_authorization_code_pkce_request_get(code)
        code_pkce_request.sub = sub
        store_oauth_authorization_server_code_pkce_request_put(code, code_pkce_request)

else:
    import dbm
    import json
    from threading import RLock

    from config_oauth_authorization_server import (
        config_oauth_authorization_server_code_pkce_request_db_path,
    )

    rlock = RLock()

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
            _db[code.encode("utf8")] = json.dumps(dict(code_pkce_request)).encode(
                "utf8"
            )

    def store_oauth_authorization_server_code_pkce_request_get_and_delete(code: str):
        with rlock:
            result = CodePkceRequest(
                **json.loads(_db[code.encode("utf8")].decode("utf8"))
            )
            del _db[code.encode("utf8")]
            return result

    def store_oauth_authorization_code_pkce_request_get(code: str):
        with rlock:
            return CodePkceRequest(
                **json.loads(_db[code.encode("utf8")].decode("utf8"))
            )

    def store_oauth_authorization_server_code_pkce_request_set_sub(code: str, sub: str):
        with rlock:
            code_pkce_request = store_oauth_authorization_code_pkce_request_get(code)
            code_pkce_request.sub = sub
            store_oauth_authorization_server_code_pkce_request_put(
                code, code_pkce_request
            )
