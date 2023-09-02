import time

from pydantic import BaseModel

from driver_key_value_store_sqlite import (
    driver_key_value_store_del,
    driver_key_value_store_get,
    driver_key_value_store_put,
)


class CodeVerifier(BaseModel):
    code_verifier: str


STORE = "oauth_code_pkce_code_verifier"


def store_oauth_code_pkce_code_verifier_put(state: str, code_verifier: CodeVerifier):
    # Allow 5 mins for the flow (to allow for login and consent)
    driver_key_value_store_put(STORE, state, code_verifier, ttl=time.time() + (5 * 60))


def store_oauth_code_pkce_code_verifier_get_and_delete(state: str):
    result = CodeVerifier(**driver_key_value_store_get(STORE, state))
    driver_key_value_store_del(STORE, state)
    return result
