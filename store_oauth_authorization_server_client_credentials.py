from data_oauth_authorization_server import ClientCredentials
import kvstore.driver

STORE = "oauth_authorization_server_client_credentials"


def store_oauth_authorization_server_client_credentials_put(
    client: str, client_credentials: ClientCredentials
):
    values = client_credentials.dict()
    for scope in values["scopes"]:
        assert " " not in scope
    values["scopes"] = " ".join(values["scopes"])
    kvstore.driver.put(STORE, client, values)


def store_oauth_authorization_server_client_credentials_get(client: str):
    data, ttl = kvstore.driver.get(STORE, client, consistent=True)
    data["scopes"] = [scope for scope in data["scopes"].split(" ") if scope]
    return ClientCredentials(**data)
