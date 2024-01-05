import time

from data_oauth_code_pkce import CodeVerifier
import kvstore.driver

STORE = "oauth_code_pkce_code_verifier"


def store_oauth_code_pkce_code_verifier_put(state: str, code_verifier: CodeVerifier):
    # Allow 5 mins for the flow (to allow for login and consent)
    kvstore.driver.put(STORE, state, code_verifier.dict(), ttl=time.time() + (5 * 60))


def store_oauth_code_pkce_code_verifier_get_and_delete(state: str):
    values, ttl = kvstore.driver.get(STORE, state, consistent=True)
    result = CodeVerifier(**values)
    kvstore.driver.delete(STORE, state)
    return result
