from markupsafe import Markup

import helper_hooks
from render import render
from route_oauth_authorization_server import (
    route_oauth_authorization_server_authorize,
    route_oauth_authorization_server_consent,
    route_oauth_authorization_server_jwks_json,
    route_oauth_authorization_server_login,
    route_oauth_authorization_server_openid_configuration,
    route_oauth_authorization_server_token,
)
from route_oauth_code_pkce import (
    route_oauth_code_pkce_callback,
    route_oauth_code_pkce_login,
)
from route_oauth_resource_owner import (
    route_oauth_resource_owner_home,
    route_oauth_resource_owner_openapi,
)
from route_oauth_resource_owner_api import route_oauth_resource_owner_api_v1
from route_saml_sp import route_saml_sp_acs, route_saml_sp_login
from route_static import route_static
from route_webhook_provider import route_webhook_provider_jwks_json
from store_oauth_authorization_server_client_credentials import (
    store_oauth_authorization_server_client_credentials_cleanup,
    store_oauth_authorization_server_client_credentials_init,
)
from store_oauth_authorization_server_code_pkce import (
    store_oauth_authorization_server_code_pkce_cleanup,
    store_oauth_authorization_server_code_pkce_init,
)
from store_oauth_authorization_server_codes import (
    store_oauth_authorization_server_codes_cleanup,
    store_oauth_authorization_server_codes_init,
)
from store_oauth_authorization_server_keys_current import (
    store_oauth_authorization_server_keys_current_cleanup,
    store_oauth_authorization_server_keys_current_init,
)
from store_oauth_authorization_server_session import (
    store_oauth_authorization_server_session_cleanup,
    store_oauth_authorization_server_session_init,
)
from store_oauth_code_pkce_code_verifier import (
    store_oauth_code_pkce_code_verifier_cleanup,
    store_oauth_code_pkce_code_verifier_init,
)
from store_webhook_provider_keys_current import (
    store_webhook_provider_keys_current_cleanup,
    store_webhook_provider_keys_current_init,
)

home_markup = Markup(
    """<p>
    <a href="/oauth-code-pkce/login">Login without scopes</a>,  <a href="/oauth-code-pkce/login?scope=read">login with read scope</a>, <a href="/oauth-code-pkce/login?scope=no-such-scope">login with an invalid scope</a>, <a href="/saml2/login/">login with SAML</a>.</p>"""
)


def render_home(title: str):
    return render(title=title, body=home_markup)


def home(http):
    http.response.body = render_home(title="OAuth Client Home")


helper_hooks.hooks = {
    "init": [
        store_oauth_authorization_server_codes_init,
        store_oauth_authorization_server_keys_current_init,
        store_oauth_authorization_server_session_init,
        store_webhook_provider_keys_current_init,
        store_oauth_code_pkce_code_verifier_init,
        store_oauth_authorization_server_client_credentials_init,
        store_oauth_authorization_server_code_pkce_init,
    ],
    "cleanup": [
        store_oauth_authorization_server_codes_cleanup,
        store_oauth_authorization_server_keys_current_cleanup,
        store_oauth_authorization_server_session_cleanup,
        store_webhook_provider_keys_current_cleanup,
        store_oauth_code_pkce_code_verifier_cleanup,
        store_oauth_authorization_server_client_credentials_cleanup,
        store_oauth_authorization_server_code_pkce_cleanup,
    ],
    "routes": {
        "/saml2/login/": route_saml_sp_login,
        "/saml2/acs/": route_saml_sp_acs,
        "/": home,
        "/api": route_oauth_resource_owner_home,
        "/api/v1": route_oauth_resource_owner_api_v1,
        "/api/openapi.json": route_oauth_resource_owner_openapi,
        "/static/file": route_static("static/file", "text/plain"),
        "/.well-known/jwks.json": route_oauth_authorization_server_jwks_json,
        "/.well-known/webhook-provider-jwks.json": route_webhook_provider_jwks_json,
        "/.well-known/openid-configuration": route_oauth_authorization_server_openid_configuration,
        "/oauth-code-pkce/login": route_oauth_code_pkce_login,
        "/oauth-code-pkce/callback": route_oauth_code_pkce_callback,
        "/oauth/authorize": route_oauth_authorization_server_authorize,
        "/oauth/login": route_oauth_authorization_server_login,
        "/oauth/consent": route_oauth_authorization_server_consent,
        "/oauth/token": route_oauth_authorization_server_token,
    },
}
