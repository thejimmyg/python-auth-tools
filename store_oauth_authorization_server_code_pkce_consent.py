from data_oauth_authorization_server import CodePkceConsent
from driver_key_value_store import (
    driver_key_value_store_get,
    driver_key_value_store_put,
)

STORE = "oauth_authorization_server_code_pkce_consent"


def store_oauth_authorization_server_code_pkce_consent_put(
    sub: str, client_id: str, code_pkce_consent: CodePkceConsent
):
    driver_key_value_store_put(STORE, client_id + " " + sub, code_pkce_consent)


def store_oauth_authorization_code_pkce_consent_get(sub: str, client_id: str):
    return CodePkceConsent(**driver_key_value_store_get(STORE, client_id + " " + sub))
