from data_oauth_authorization_server import ClientCredentials
from driver_key_value_store import (
    driver_key_value_store_get,
    driver_key_value_store_put,
)

STORE = "oauth_authorization_server_client_credentials"


def store_oauth_authorization_server_client_credentials_put(
    client: str, client_credentials: ClientCredentials
):
    driver_key_value_store_put(STORE, client, client_credentials)


def store_oauth_authorization_server_client_credentials_get(client: str):
    return ClientCredentials(**driver_key_value_store_get(STORE, client))
