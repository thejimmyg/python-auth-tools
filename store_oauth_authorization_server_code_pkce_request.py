import time

from data_oauth_authorization_server import CodePkceRequest
import kvstore.driver

STORE = "oauth_authorization_server_code_pkce_request"


def store_oauth_authorization_server_code_pkce_request_put(
    code: str, code_pkce_request: CodePkceRequest
):
    # Allow the code to be valid for 30 seconds
    values = code_pkce_request.dict()
    if values["scopes"]:
        for scope in values["scopes"]:
            assert " " not in scope
        values["scopes"] = " ".join(values["scopes"])
    else:
        del values["scopes"]
    if values["state"] is None:
        del values["state"]
    if values["sub"] is None:
        del values["sub"]
    kvstore.driver.put(STORE, code, values, ttl=time.time() + 30)


def store_oauth_authorization_server_code_pkce_request_get_and_delete(code: str):
    result = store_oauth_authorization_code_pkce_request_get(code)
    kvstore.driver.delete(STORE, code)
    return result


def store_oauth_authorization_code_pkce_request_get(code: str):
    values, ttl = kvstore.driver.get(STORE, code, consistent=True)
    if values.get("scopes"):
        values["scopes"] = [scope for scope in values["scopes"].split(" ") if scope]
    # else:
    #     values["scopes"] = None
    # if "state" not in values:
    #     values["state"] = None
    # if "sub" not in values:
    #     values["sub"] = None
    return CodePkceRequest(**values)


def store_oauth_authorization_server_code_pkce_request_set_sub(code: str, sub: str):
    code_pkce_request = store_oauth_authorization_code_pkce_request_get(code)
    code_pkce_request.sub = sub
    store_oauth_authorization_server_code_pkce_request_put(code, code_pkce_request)
