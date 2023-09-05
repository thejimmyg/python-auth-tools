from markupsafe import Markup
from route_client import route_client_home
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
from http_session import http_session_create, http_session_destroy, http_session_get_id
from plugin_oauth_test import (
    plugin_oauth_test_hook_oauth_authorization_server_is_signed_in,
    plugin_oauth_test_hook_oauth_authorization_server_on_authorize_when_not_signed_in,
    plugin_oauth_test_hook_oauth_authorization_server_on_save_code,
    plugin_oauth_test_route_oauth_authorization_server_consent,
    plugin_oauth_test_route_oauth_authorization_server_login,
)
from render import render
from route_not_found import route_not_found
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
from store_session import (
    Session,
    store_session_destroy,
    store_session_get,
    store_session_put,
)

urls = {
    "url_home": "/",
}
urls.update(
    {
        # These ones don't need to start with / since url_home already ends with /
        "url_auth": urls["url_home"] + "auth",
        "url_client": urls["url_home"] + "client",
        "url_resource_owner_a": urls["url_home"] + "resource-owner-a",
        "url_resource_owner_b": urls["url_home"] + "resource-owner-b",
    }
)
urls.update(
    {
        "url_auth_token": urls["url_auth"] + "/token",
        "url_auth_logout": urls["url_auth"] + "/logout",
        "url_client_login": urls["url_client"] + "/login",
        "url_client_logout": urls["url_client"] + "/logout",
        "url_client_token": urls["url_client"] + "/token",
        "url_client_callback": urls["url_client"] + "/callback",
        "url_resource_owner_a_api": urls["url_resource_owner_a"] + "/api",
        "url_resource_owner_b_api": urls["url_resource_owner_b"] + "/api",
    }
)
urls.update(
    {
        "url_resource_owner_a_api_read": urls["url_resource_owner_a_api"] + "/read",
        "url_resource_owner_b_api_write": urls["url_resource_owner_b_api"] + "/write",
    }
)


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


def route_not_logged_in(http):
    http.response.status = "401 Not Authenticated"
    http.response.body = render(
        title="Not Logged In", body=Markup("""<p>Not logged in.</p>""")
    )


def route_home(http):
    http.response.body = render(
        "Home",
        Markup(
            """
<ul>
  <li><a href="{url_auth}">Auth</a> (Stub)</li>
  <li><a href="{url_client}">Client</a> (System Under Test)</li>
  <li><a href="{url_resource_owner_a}">Resource Owner A</a> (Stub)</li>
  <li><a href="{url_resource_owner_b}">Resource Owner B</a> (Stub)</li>
</ul>
"""
        ).format(
            url_auth=urls["url_auth"],
            url_client=urls["url_client"],
            url_resource_owner_a=urls["url_resource_owner_a"],
            url_resource_owner_b=urls["url_resource_owner_b"],
        ),
    )


def route_auth(http):
    session_id = http_session_get_id(http, "oauth")
    if session_id:
        login_or_logout = Markup(
            """
<ul>
            <li><a href="{url_auth_logout}">Logout</a> (Stub)</li>
            <li><a href="{url_auth_token}">Token</a></li>
</ul>
"""
        ).format(
            url_auth_logout=urls["url_auth_logout"],
            url_auth_token=urls["url_auth_token"],
        )
    else:
        login_or_logout = Markup("<p>Not logged in.</p>")
    http.response.body = render(
        "Auth",
        Markup("""{login_or_logout}""").format(
            login_or_logout=login_or_logout,
        ),
    )


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
        <h1><a href="{url_home}">Everything</a></h1>
        <h2>{{title}}</h2>
        {{body}}
    </main>
	<script src="/script.js"></script>
  </body>
</html>"""
).format(url_home=urls["url_home"])


def route_redirect_to_dashboard(http):
    http.response.body = helper_meta_refresh_html(urls["url_client"])


def route_oauth_authorization_server_logout(http):
    session_id = http_session_get_id(http, "oauth")
    logged_in = True
    try:
        store_session_destroy(session_id)
    except Exception as e:
        logged_in = False
        helper_log(__file__, "Could not destory store session:", e)
    try:
        http_session_destroy(http, "oauth")
    except Exception as e:
        helper_log(__file__, "Could not destory http session:", e)
        logged_in = False
    if not logged_in:
        return route_not_logged_in(http)
    http.response.body = render(
        title="Logged out",
        body=Markup("""<p>Successfully logged out.</p>"""),
    )


def route_code_pkce_logout(http):
    session_id = http_session_get_id(http, "oauth_code_pkce")
    logged_in = True
    try:
        store_session_destroy(session_id)
    except Exception as e:
        helper_log(__file__, "Could not destory store session:", e)
        logged_in = False
    try:
        http_session_destroy(http, "oauth_code_pkce")
    except Exception as e:
        helper_log(__file__, "Could not destory http session:", e)
        logged_in = False
    if not logged_in:
        return route_not_logged_in(http)
    http.response.body = render(
        title="Logged out",
        body=Markup("""<p>Successfully logged out.</p>"""),
    )


def route_token(http):
    try:
        session_id = http_session_get_id(http, "oauth")
    except Exception as e:
        helper_log(__file__, e)
        return route_not_logged_in(http)
    http.response.body = render(
        title="Auth Token",
        body=Markup(
            """
            <p><a href="{url_home}">Home</a> &gt; <a href="{url_auth}">Auth</a> &gt; Token</p>
            <p>Here's the session ID:</p>
            <p><span id="session_id">{session_id}</span></p>
            """
        ).format(
            session_id=session_id,
            url_home=urls["url_home"],
            url_auth=urls["url_auth"],
        ),
    )


def route_client_token(http):
    try:
        session_id = http_session_get_id(http, "oauth_code_pkce")
        session = store_session_get(session_id)
    except Exception as e:
        helper_log(__file__, e)
        return route_not_logged_in(http)
    http.response.body = render(
        title="Client Token",
        body=Markup(
            """
            <p><a href="{url_home}">Home</a> &gt; <a href="{url_client}">Client</a> &gt; Token</p>
            <p>Here's the JWT access token:</p>
            <p><span id="jwt">{access_token}</span></p>"""
        ).format(
            access_token=session.value.get("access_token"),
            url_home=urls["url_home"],
            url_client=urls["url_client"],
        ),
    )


helper_hooks.hooks = {
    "init": [
        driver_key_value_store_sqlite_init,
    ],
    "cleanup": [
        driver_key_value_store_sqlite_cleanup,
    ],
    "urls": urls,
    "routes": {
        # Default
        "*": route_not_found,
        urls["url_home"]: route_home,
        # Auth Routes
        urls["url_auth"]: route_auth,
        "/.well-known/jwks.json": route_oauth_authorization_server_jwks_json,
        "/.well-known/openid-configuration": route_oauth_authorization_server_openid_configuration,
        urls["url_auth_logout"]: route_oauth_authorization_server_logout,
        urls["url_auth_token"]: route_token,
        "/oauth/authorize": route_oauth_authorization_server_authorize,
        "/oauth/token": route_oauth_authorization_server_token,
        "/oauth/login": plugin_oauth_test_route_oauth_authorization_server_login,
        "/oauth/consent": plugin_oauth_test_route_oauth_authorization_server_consent,
        # Client Routes
        urls["url_client"]: route_client_home,
        urls["url_client_logout"]: route_code_pkce_logout,
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
}
