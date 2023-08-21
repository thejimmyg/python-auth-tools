import dbm
import json

from pydantic import BaseModel

from config_oauth_authorization_server import (
    oauth_authorization_server_clients_code_dbpath,
)


class CodeClient(BaseModel):
    redirect_uri: str
    scopes: list[str]


_db = None


def oauth_authorization_server_clients_code_init():
    global _db
    _db = dbm.open(oauth_authorization_server_clients_code_dbpath, "c")


def oauth_authorization_server_clients_code_cleanup():
    _db.close()


def put_code_client(client: str, code_client: CodeClient):
    _db[client.encode("utf8")] = json.dumps(dict(code_client)).encode("utf8")


def get_code_client(client: str):
    return CodeClient(**json.loads(_db[client.encode("utf8")].decode("utf8")))
