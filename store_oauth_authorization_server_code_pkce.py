import os

from pydantic import BaseModel


class CodePkce(BaseModel):
    redirect_uri: str
    scopes: list[str]


if os.environ.get("STORE_MODE", "") != "dbm":
    from driver_key_value_store_sqlite import (
        driver_key_value_store_get,
        driver_key_value_store_put,
    )

    STORE = "oauth_authorization_server_code_pkce"

    def store_oauth_authorization_server_code_pkce_init():
        pass

    def store_oauth_authorization_server_code_pkce_cleanup():
        pass

    def store_oauth_authorization_server_code_pkce_put(
        client: str, code_pkce: CodePkce
    ):
        driver_key_value_store_put(STORE, client, code_pkce)

    def store_oauth_authorization_server_code_pkce_get(client: str):
        return CodePkce(**driver_key_value_store_get(STORE, client))

else:
    import dbm
    import json
    from threading import RLock

    from config_oauth_authorization_server import (
        config_oauth_authorization_server_code_pkce_db_path,
    )

    rlock = RLock()
    _db = None

    def store_oauth_authorization_server_code_pkce_init():
        global _db
        _db = dbm.open(config_oauth_authorization_server_code_pkce_db_path, "c")

    def store_oauth_authorization_server_code_pkce_cleanup():
        _db.close()

    def store_oauth_authorization_server_code_pkce_put(
        client: str, code_pkce: CodePkce
    ):
        with rlock:
            _db[client.encode("utf8")] = json.dumps(dict(code_pkce)).encode("utf8")

    def store_oauth_authorization_server_code_pkce_get(client: str):
        with rlock:
            return CodePkce(**json.loads(_db[client.encode("utf8")].decode("utf8")))
