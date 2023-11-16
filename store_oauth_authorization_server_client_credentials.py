from data_oauth_authorization_server import ClientCredentials
from driver_key_value_store import (
    driver_key_value_store_get,
    driver_key_value_store_put,
)

STORE = "oauth_authorization_server_client_credentials"


def store_oauth_authorization_server_client_credentials_put(
    client: str, client_credentials: ClientCredentials
):
    values = client_credentials.dict()
    for scope in values["scopes"]:
        assert " " not in scope
    values["scopes"] = " ".join(values["scopes"])
    driver_key_value_store_put(STORE, client, values)


def store_oauth_authorization_server_client_credentials_get(client: str):
    data = driver_key_value_store_get(STORE, client)
    data["scopes"] = [scope for scope in data["scopes"].split(" ") if scope]
    return ClientCredentials(**data)
