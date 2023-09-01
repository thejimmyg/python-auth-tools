import os

from pydantic import BaseModel


class ClientCredentials(BaseModel):
    client_secret: str
    scopes: list[str]


if os.environ.get("STORE_MODE", "") != "dbm":
    from driver_key_value_store_sqlite import (
        driver_key_value_store_get,
        driver_key_value_store_put,
    )

    STORE = "oauth_authorization_server_client_credentials"

    def store_oauth_authorization_server_client_credentials_init():
        pass

    def store_oauth_authorization_server_client_credentials_cleanup():
        pass

    def store_oauth_authorization_server_client_credentials_put(
        client: str, client_credentials: ClientCredentials
    ):
        driver_key_value_store_put(STORE, client, client_credentials)

    def store_oauth_authorization_server_client_credentials_get(client: str):
        return ClientCredentials(**driver_key_value_store_get(STORE, client))

else:
    import dbm
    import json
    from threading import RLock

    from config_oauth_authorization_server import (
        config_oauth_authorization_server_client_credentials_db_path,
    )

    rlock = RLock()
    _db = None

    def store_oauth_authorization_server_client_credentials_init():
        global _db
        _db = dbm.open(
            config_oauth_authorization_server_client_credentials_db_path, "c"
        )

    def store_oauth_authorization_server_client_credentials_cleanup():
        _db.close()

    def store_oauth_authorization_server_client_credentials_put(
        client: str, client_credentials: ClientCredentials
    ):
        with rlock:
            _db[client.encode("utf8")] = json.dumps(dict(client_credentials)).encode(
                "utf8"
            )

    def store_oauth_authorization_server_client_credentials_get(client: str):
        with rlock:
            return ClientCredentials(
                **json.loads(_db[client.encode("utf8")].decode("utf8"))
            )
