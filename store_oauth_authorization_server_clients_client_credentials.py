import dbm
import json

from pydantic import BaseModel

from config_oauth_authorization_server import (
    oauth_authorization_server_clients_client_credentials_dbpath,
)


class ClientCredentialsClient(BaseModel):
    client_secret: str
    scopes: list[str]


_db = None


def oauth_authorization_server_clients_client_credentials_init():
    global _db
    _db = dbm.open(oauth_authorization_server_clients_client_credentials_dbpath, "c")


def oauth_authorization_server_clients_client_credentials_cleanup():
    _db.close()


def put_client_credentials_client(
    client: str, client_credentials_client: ClientCredentialsClient
):
    _db[client.encode("utf8")] = json.dumps(dict(client_credentials_client)).encode(
        "utf8"
    )


def get_client_credentials_client(client: str):
    return ClientCredentialsClient(
        **json.loads(_db[client.encode("utf8")].decode("utf8"))
    )
