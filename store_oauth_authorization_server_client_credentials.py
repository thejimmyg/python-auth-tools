import dbm
import json
from threading import RLock

from pydantic import BaseModel

from config_oauth_authorization_server import (
    config_oauth_authorization_server_client_credentials_db_path,
)

rlock = RLock()


class ClientCredentials(BaseModel):
    client_secret: str
    scopes: list[str]


_db = None


def store_oauth_authorization_server_client_credentials_init():
    global _db
    _db = dbm.open(config_oauth_authorization_server_client_credentials_db_path, "c")


def store_oauth_authorization_server_client_credentials_cleanup():
    _db.close()


def store_oauth_authorization_server_client_credentials_put(
    client: str, client_credentials: ClientCredentials
):
    with rlock:
        _db[client.encode("utf8")] = json.dumps(dict(client_credentials)).encode("utf8")


def store_oauth_authorization_server_client_credentials_get(client: str):
    with rlock:
        return ClientCredentials(
            **json.loads(_db[client.encode("utf8")].decode("utf8"))
        )
