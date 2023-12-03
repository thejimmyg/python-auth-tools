import helper_hooks
from driver_key_value_store_sqlite import (
    driver_key_value_store_sqlite_cleanup,
    driver_key_value_store_sqlite_del,
    driver_key_value_store_sqlite_get,
    driver_key_value_store_sqlite_init,
    driver_key_value_store_sqlite_put,
)
from plugin_oauth_test import (
    plugin_oauth_test_hook_oauth_authorization_server_is_signed_in,
    plugin_oauth_test_hook_oauth_authorization_server_on_authorize_when_not_signed_in,
    plugin_oauth_test_hook_oauth_authorization_server_on_save_code,
    plugin_oauth_test_hook_oauth_code_pkce_on_success,
    plugin_oauth_test_route_oauth_authorization_server_consent,
    plugin_oauth_test_route_oauth_authorization_server_login,
)
from render import Base, Html
from route_error import route_error_not_found
from route_oauth_authorization_server import (
    route_oauth_authorization_server_authorize,
    route_oauth_authorization_server_jwks_json,
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


class Home(Base):
    def __init__(self, title):
        self._title = title

    def body(self):
        return Html(
            """\
      <p>
        <a href="/oauth-code-pkce/login">Login without scopes</a>,
        <a href="/oauth-code-pkce/login?scope=read">login with read scope</a>,
        <a href="/oauth-code-pkce/login?scope=read%20offline_access">login with read and offline access scopes</a>,
        <a href="/oauth-code-pkce/login?scope=no-such-scope">login with an invalid scope</a>,
        <a href="/saml2/login/">login with SAML</a>.
      </p>"""
        )


def route_home(http):
    http.response.body = Home(title="OAuth Client Home")


hooks = helper_hooks.hooks = {
    "init": [
        driver_key_value_store_sqlite_init,
    ],
    "cleanup": [
        driver_key_value_store_sqlite_cleanup,
    ],
    "routes": {
        "/saml2/login/": route_saml_sp_login,
        "/saml2/acs/": route_saml_sp_acs,
        "/": route_home,
        "*": route_error_not_found,
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
        "/oauth/login": plugin_oauth_test_route_oauth_authorization_server_login,
        "/oauth/consent": plugin_oauth_test_route_oauth_authorization_server_consent,
        "/oauth/token": route_oauth_authorization_server_token,
    },
    "oauth_code_pkce_on_success": plugin_oauth_test_hook_oauth_code_pkce_on_success,
    "oauth_authorization_server_on_authorize_when_not_signed_in": plugin_oauth_test_hook_oauth_authorization_server_on_authorize_when_not_signed_in,
    "oauth_authorization_server_is_signed_in": plugin_oauth_test_hook_oauth_authorization_server_is_signed_in,
    "oauth_authorization_server_on_save_code": plugin_oauth_test_hook_oauth_authorization_server_on_save_code,
    "driver_key_value_store_del": driver_key_value_store_sqlite_del,
    "driver_key_value_store_get": driver_key_value_store_sqlite_get,
    "driver_key_value_store_put": driver_key_value_store_sqlite_put,
}
