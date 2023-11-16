from data_oauth_authorization_server import CodePkce
from driver_key_value_store import (
    driver_key_value_store_get,
    driver_key_value_store_put,
)

STORE = "oauth_authorization_server_code_pkce"


def store_oauth_authorization_server_code_pkce_put(client: str, code_pkce: CodePkce):
    values = code_pkce.dict()
    for scope in values["scopes"]:
        assert " " not in scope
    values["scopes"] = " ".join(values["scopes"])
    driver_key_value_store_put(STORE, client, values)


def store_oauth_authorization_server_code_pkce_get(client: str):
    values = driver_key_value_store_get(STORE, client)
    values["scopes"] = [scope for scope in values["scopes"].split(" ") if scope]
    return CodePkce(**values)
