import time

from pydantic import BaseModel

from driver_key_value_store import (
    driver_key_value_store_del,
    driver_key_value_store_get,
    driver_key_value_store_put,
)


class CodePkceRequest(BaseModel):
    client_id: str
    code_challenge: str
    scopes: list[str] | None
    state: str | None
    sub: str | None


STORE = "oauth_authorization_server_code_pkce_request"


def store_oauth_authorization_server_code_pkce_request_put(
    code: str, code_pkce_request: CodePkceRequest
):
    # Allow the code to be valid for 30 seconds
    driver_key_value_store_put(STORE, code, code_pkce_request, ttl=time.time() + 30)


def store_oauth_authorization_server_code_pkce_request_get_and_delete(code: str):
    result = CodePkceRequest(**driver_key_value_store_get(STORE, code))
    result = store_oauth_authorization_code_pkce_request_get(code)
    driver_key_value_store_del(STORE, code)
    return result


def store_oauth_authorization_code_pkce_request_get(code: str):
    return CodePkceRequest(**driver_key_value_store_get(STORE, code))


def store_oauth_authorization_server_code_pkce_request_set_sub(code: str, sub: str):
    code_pkce_request = store_oauth_authorization_code_pkce_request_get(code)
    code_pkce_request.sub = sub
    store_oauth_authorization_server_code_pkce_request_put(code, code_pkce_request)
