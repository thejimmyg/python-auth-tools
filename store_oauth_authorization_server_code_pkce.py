from data_oauth_authorization_server import CodePkce
import kvstore.driver

STORE = "oauth_authorization_server_code_pkce"


def store_oauth_authorization_server_code_pkce_put(client: str, code_pkce: CodePkce):
    values = code_pkce.dict()
    for scope in values["scopes"]:
        assert " " not in scope
    values["scopes"] = " ".join(values["scopes"])
    kvstore.driver.put(STORE, client, values)


def store_oauth_authorization_server_code_pkce_get(client: str):
    values, ttl = kvstore.driver.get(STORE, client, consistent=True)
    values["scopes"] = [scope for scope in values["scopes"].split(" ") if scope]
    return CodePkce(**values)
