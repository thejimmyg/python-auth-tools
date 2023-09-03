from pydantic import BaseModel

from driver_key_value_store import (
    driver_key_value_store_get,
    driver_key_value_store_put,
)


class ClientCredentials(BaseModel):
    client_secret: str
    scopes: list[str]


STORE = "oauth_authorization_server_client_credentials"


def store_oauth_authorization_server_client_credentials_put(
    client: str, client_credentials: ClientCredentials
):
    driver_key_value_store_put(STORE, client, client_credentials)


def store_oauth_authorization_server_client_credentials_get(client: str):
    return ClientCredentials(**driver_key_value_store_get(STORE, client))
