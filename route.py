import config
from route_oauth_authorization_server import (
    oauth_authorization_server_authorize,
    oauth_authorization_server_consent,
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

routes = {
    "/saml2/login/": saml_login,
    "/saml2/acs/": saml_acs,
    "/": oauth_client_home,
    "/api": oauth_resource_owner_home,
    "/api/v1": v1,
    "/api/openapi.json": oauth_resource_owner_openapi,
    "/static/file": static("static/file", "text/plain"),
    "/.well-known/jwks.json": static(
        config.oauth_authorization_server_jwks_json,
        "application/json; charset=UTF8",
    ),
    "/.well-known/openid-configuration": oauth_authorization_server_openid_configuration,
    "/oauth-client/login": oauth_client_flow_code_pkce_login,
    "/oauth-client/callback": oauth_client_flow_code_pkce_callback,
    "/oauth/authorize": oauth_authorization_server_authorize,
    "/oauth/login": oauth_authorization_server_login,
    "/oauth/consent": oauth_authorization_server_consent,
    # "/oauth/logout": oauth_logout,
    "/oauth/token": oauth_authorization_server_token,
}
