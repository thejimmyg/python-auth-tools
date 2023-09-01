import os

from pydantic import BaseModel


class CodePkceConsent(BaseModel):
    scopes: list[str] | None


if os.environ.get("STORE_MODE", "") != "dbm":
    from driver_key_value_store_sqlite import (
        driver_key_value_store_get,
        driver_key_value_store_put,
    )

    STORE = "oauth_authorization_server_code_pkce_consent"

    def store_oauth_authorization_server_code_pkce_consent_init():
        pass

    def store_oauth_authorization_server_code_pkce_consent_cleanup():
        pass

    def store_oauth_authorization_server_code_pkce_consent_put(
        sub: str, client_id: str, code_pkce_consent: CodePkceConsent
    ):
        driver_key_value_store_put(STORE, client_id + " " + sub, code_pkce_consent)

    def store_oauth_authorization_code_pkce_consent_get(sub: str, client_id: str):
        return CodePkceConsent(
            **driver_key_value_store_get(STORE, client_id + " " + sub)
        )

else:
    import dbm
    import json
    from threading import RLock

    from config_oauth_authorization_server import (
        config_oauth_authorization_server_code_pkce_consent_db_path,
    )

    rlock = RLock()

    _db = None

    def store_oauth_authorization_server_code_pkce_consent_init():
        global _db
        _db = dbm.open(config_oauth_authorization_server_code_pkce_consent_db_path, "c")

    def store_oauth_authorization_server_code_pkce_consent_cleanup():
        _db.close()

    def store_oauth_authorization_server_code_pkce_consent_put(
        sub: str, client_id: str, code_pkce_consent: CodePkceConsent
    ):
        with rlock:
            _db[f"{sub} {client_id}".encode("utf8")] = json.dumps(
                dict(code_pkce_consent)
            ).encode("utf8")

    def store_oauth_authorization_code_pkce_consent_get(sub: str, client_id: str):
        with rlock:
            return CodePkceConsent(
                **json.loads(_db[f"{sub} {client_id}".encode("utf8")].decode("utf8"))
            )
