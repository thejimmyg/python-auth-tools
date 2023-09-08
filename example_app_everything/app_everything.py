from markupsafe import Markup
from route_auth import route_auth, route_auth_session
from route_client import route_client_home, route_client_logout, route_client_token
from route_home import route_home
from route_resource_owner_a import (
    route_resource_owner_a,
    route_resource_owner_a_api,
    route_resource_owner_a_api_read,
)
from route_resource_owner_b import (
    route_resource_owner_b,
    route_resource_owner_b_api,
    route_resource_owner_b_api_write,
)

import helper_hooks
from driver_key_value_store_sqlite import (
    driver_key_value_store_sqlite_cleanup,
    driver_key_value_store_sqlite_del,
    driver_key_value_store_sqlite_get,
    driver_key_value_store_sqlite_init,
    driver_key_value_store_sqlite_put,
)
from helper_log import helper_log
from helper_meta_refresh import helper_meta_refresh_html
from helper_oauth_resource_owner import helper_oauth_resource_owner_verify_jwt
from http_session import (
    get_session_id_or_respond_early_not_logged_in,
    http_session_create,
    http_session_destroy,
)
from plugin_oauth_test import (
    plugin_oauth_test_hook_oauth_authorization_server_is_signed_in,
    plugin_oauth_test_hook_oauth_authorization_server_on_authorize_when_not_signed_in,
    plugin_oauth_test_hook_oauth_authorization_server_on_save_code,
    plugin_oauth_test_route_oauth_authorization_server_consent,
    plugin_oauth_test_route_oauth_authorization_server_login,
)
from render import render
from route_error import route_error_not_found, route_error_not_logged_in
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
from store_session import Session, store_session_destroy, store_session_put

url_home = "/"
url_auth = url_home + "auth"
url_client = url_home + "client"
url_resource_owner_a = url_home + "resource-owner-a"
url_resource_owner_b = url_home + "resource-owner-b"
url_auth_session = url_auth + "/session"
url_auth_logout = url_auth + "/logout"
url_client_login = url_client + "/login"
url_client_logout = url_client + "/logout"
url_client_token = url_client + "/token"
url_client_callback = url_client + "/callback"
url_resource_owner_a_api = url_resource_owner_a + "/api"
url_resource_owner_b_api = url_resource_owner_b + "/api"
url_resource_owner_a_api_read = url_resource_owner_a_api + "/read"
url_resource_owner_b_api_write = url_resource_owner_b_api + "/write"

urls = dict([(k, v) for k, v in locals().items() if k.startswith("url_")])
print(urls)

# What about ones like Not Logged In, Logged Out that exist at a location, but not in navigation?

navigation = {
    (url_home, "Home"): {
        (url_auth, "Auth"): {
            (url_auth_session, "Auth Session"): {},
            (url_auth_logout, "Auth Logout"): {},
        },
        (url_client, "Client"): {
            (url_client_login, "Client Login"): {},
            (url_client_logout, "Client Logout"): {},
            (url_client_token, "Client Token"): {},
        },
        (url_resource_owner_a, "Resource Owner A"): {
            (url_resource_owner_a_api, "Resource Owner A API"): {}
        },
        (url_resource_owner_b, "Resource Owner B"): {
            (url_resource_owner_b_api, "Resource Owner B API"): {}
        },
    }
}


main_markup = Markup(
    """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>{{title}}</title>
    <link rel="stylesheet" href="/style.css">
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
  </head>
  <body>
    <main>
        <h2><a href="{url_home}">Everything</a></h2>
        <h1>{{title}}</h1>
        {{body}}
    </main>
	<script src="/script.js"></script>
  </body>
</html>"""
).format(url_home=urls["url_home"])


def hook_oauth_code_pkce_on_success(http, response):
    access_token = response["access_token"]
    helper_log(__file__, "Access token:", access_token)
    helper_log(__file__, "Creating session")
    session_id = http_session_create(http, "oauth_code_pkce")
    claims = helper_oauth_resource_owner_verify_jwt(access_token)
    helper_log(__file__, "Claims:", claims)
    store_session_put(
        session_id, Session(sub=claims["sub"], value=dict(access_token=access_token))
    )
    http.response.body = helper_meta_refresh_html("/oauth-code-pkce/dashboard")


def route_redirect_to_dashboard(http):
    http.response.body = helper_meta_refresh_html(urls["url_client"])


def route_oauth_authorization_server_logout(http):
    session_id = get_session_id_or_respond_early_not_logged_in(http, "oauth")
    logged_in = True
    try:
        store_session_destroy(session_id)
    except Exception as e:
        logged_in = False
        helper_log(__file__, "Could not destroy store session:", e)
    try:
        http_session_destroy(http, "oauth")
    except Exception as e:
        helper_log(__file__, "Could not destroy http session:", e)
        logged_in = False
    if not logged_in:
        return route_error_not_logged_in(http)
    http.response.body = render(
        title="Logged out",
        body=Markup("""<p>Successfully logged out.</p>"""),
    )


helper_hooks.hooks = {
    "init": [
        driver_key_value_store_sqlite_init,
    ],
    "cleanup": [
        driver_key_value_store_sqlite_cleanup,
    ],
    "urls": urls,
    "navigation": navigation,
    "routes": {
        # Default
        "*": route_error_not_found,
        urls["url_home"]: route_home,
        # Auth Routes
        urls["url_auth"]: route_auth,
        "/.well-known/jwks.json": route_oauth_authorization_server_jwks_json,
        "/.well-known/openid-configuration": route_oauth_authorization_server_openid_configuration,
        urls["url_auth_logout"]: route_oauth_authorization_server_logout,
        urls["url_auth_session"]: route_auth_session,
        "/oauth/authorize": route_oauth_authorization_server_authorize,
        "/oauth/token": route_oauth_authorization_server_token,
        "/oauth/login": plugin_oauth_test_route_oauth_authorization_server_login,
        "/oauth/consent": plugin_oauth_test_route_oauth_authorization_server_consent,
        # Client Routes
        urls["url_client"]: route_client_home,
        urls["url_client_logout"]: route_client_logout,
        urls["url_client_token"]: route_client_token,
        urls["url_client_login"]: route_oauth_code_pkce_login,
        urls["url_client_callback"]: route_oauth_code_pkce_callback,
        # XXX This should be a hook, not a route.
        "/oauth-code-pkce/dashboard": route_redirect_to_dashboard,
        # Resource Owner A Routes
        urls["url_resource_owner_a"]: route_resource_owner_a,
        urls["url_resource_owner_a_api"]: route_resource_owner_a_api,
        urls["url_resource_owner_a_api_read"]: route_resource_owner_a_api_read,
        # Resource Owner B Routes
        urls["url_resource_owner_b"]: route_resource_owner_b,
        urls["url_resource_owner_b_api"]: route_resource_owner_b_api,
        urls["url_resource_owner_b_api_write"]: route_resource_owner_b_api_write,
    },
    "oauth_code_pkce_on_success": hook_oauth_code_pkce_on_success,
    "oauth_authorization_server_on_authorize_when_not_signed_in": plugin_oauth_test_hook_oauth_authorization_server_on_authorize_when_not_signed_in,
    "oauth_authorization_server_is_signed_in": plugin_oauth_test_hook_oauth_authorization_server_is_signed_in,
    "oauth_authorization_server_on_save_code": plugin_oauth_test_hook_oauth_authorization_server_on_save_code,
    "driver_key_value_store_del": driver_key_value_store_sqlite_del,
    "driver_key_value_store_get": driver_key_value_store_sqlite_get,
    "driver_key_value_store_put": driver_key_value_store_sqlite_put,
    "main_markup": main_markup,
}
