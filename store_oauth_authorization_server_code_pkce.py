from pydantic import BaseModel

from driver_key_value_store import (
    driver_key_value_store_get,
    driver_key_value_store_put,
)


class CodePkce(BaseModel):
    redirect_uri: str
    scopes: list[str]


STORE = "oauth_authorization_server_code_pkce"


def store_oauth_authorization_server_code_pkce_put(client: str, code_pkce: CodePkce):
    driver_key_value_store_put(STORE, client, code_pkce)


def store_oauth_authorization_server_code_pkce_get(client: str):
    return CodePkce(**driver_key_value_store_get(STORE, client))
