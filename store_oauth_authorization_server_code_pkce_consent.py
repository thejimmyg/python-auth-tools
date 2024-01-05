from data_oauth_authorization_server import CodePkceConsent
import kvstore.driver

STORE = "oauth_authorization_server_code_pkce_consent"


def store_oauth_authorization_server_code_pkce_consent_put(
    sub: str, client_id: str, code_pkce_consent: CodePkceConsent
):
    kvstore.driver.put(STORE, client_id + "/" + sub, code_pkce_consent)


def store_oauth_authorization_code_pkce_consent_get(sub: str, client_id: str):
    values, ttl = kvstore.driver.get(STORE, client_id + "/" + sub, consistent=True)
    return CodePkceConsent(**values)
