from route_oauth_authorization_server import (
    oauth_authorization_server_authorize,
    oauth_authorization_server_consent,
    oauth_authorization_server_jwks_json,
    oauth_authorization_server_login,
    oauth_authorization_server_openid_configuration,
    oauth_authorization_server_token,
)
from route_oauth_client import oauth_client_home
from route_oauth_client_flow_code_pkce import (
    oauth_client_flow_code_pkce_callback,
    oauth_client_flow_code_pkce_login,
)
from route_oauth_resource_owner import (
    oauth_resource_owner_home,
    oauth_resource_owner_openapi,
)
from route_oauth_resource_owner_api import v1
from route_saml_sp import saml_acs, saml_login
from route_static import static
from route_webhook import webhook_jwks_json

routes = {
    "/saml2/login/": saml_login,
    "/saml2/acs/": saml_acs,
    "/": oauth_client_home,
    "/api": oauth_resource_owner_home,
    "/api/v1": v1,
    "/api/openapi.json": oauth_resource_owner_openapi,
    "/static/file": static("static/file", "text/plain"),
    "/.well-known/jwks.json": oauth_authorization_server_jwks_json,
    "/.well-known/webhook-jwks.json": webhook_jwks_json,
    "/.well-known/openid-configuration": oauth_authorization_server_openid_configuration,
    "/oauth-client/login": oauth_client_flow_code_pkce_login,
    "/oauth-client/callback": oauth_client_flow_code_pkce_callback,
    "/oauth/authorize": oauth_authorization_server_authorize,
    "/oauth/login": oauth_authorization_server_login,
    "/oauth/consent": oauth_authorization_server_consent,
    # "/oauth/logout": oauth_logout,
    "/oauth/token": oauth_authorization_server_token,
}


from store_oauth_authorization_server_clients_client_credentials import (
    oauth_authorization_server_clients_client_credentials_cleanup,
    oauth_authorization_server_clients_client_credentials_init,
)
from store_oauth_authorization_server_clients_code import (
    oauth_authorization_server_clients_code_cleanup,
    oauth_authorization_server_clients_code_init,
)
from store_oauth_authorization_server_codes import (
    oauth_authorization_server_codes_cleanup,
    oauth_authorization_server_codes_init,
)
from store_oauth_authorization_server_current_key import (
    oauth_authorization_server_current_key_cleanup,
    oauth_authorization_server_current_key_init,
)
from store_oauth_authorization_server_session import (
    oauth_authorization_server_session_cleanup,
    oauth_authorization_server_session_init,
)
from store_oauth_client_flow_code_pkce_code_verifier import (
    oauth_client_flow_code_pkce_code_verifier_cleanup,
    oauth_client_flow_code_pkce_code_verifier_init,
)
from store_webhook_server_current_key import (
    webhook_current_key_cleanup,
    webhook_current_key_init,
)

init = [
    oauth_authorization_server_codes_init,
    oauth_authorization_server_current_key_init,
    oauth_authorization_server_session_init,
    webhook_current_key_init,
    oauth_client_flow_code_pkce_code_verifier_init,
    oauth_authorization_server_clients_client_credentials_init,
    oauth_authorization_server_clients_code_init,
]
cleanup = [
    oauth_authorization_server_codes_cleanup,
    oauth_authorization_server_current_key_cleanup,
    oauth_authorization_server_session_cleanup,
    webhook_current_key_cleanup,
    oauth_client_flow_code_pkce_code_verifier_cleanup,
    oauth_authorization_server_clients_client_credentials_cleanup,
    oauth_authorization_server_clients_code_cleanup,
]
