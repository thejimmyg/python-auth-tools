from markupsafe import Markup

import helper_hooks
from error import NotFound
from helper_log import helper_log
from helper_navigation import helper_navigation_generate_and_cache_breadcrumbs
from http_session import (
    get_session_id_or_respond_early_not_logged_in,
    get_session_or_respond_early_not_logged_in,
    http_session_destroy,
    http_session_id,
)
from render import render
from route_error import route_error_not_logged_in
from store_session import store_session_destroy


def route_client_home(http):
    try:
        http_session_id(http, "oauth_code_pkce")
    except NotFound:
        login_or_logout = Markup(
            '<li><a href="{url_client_login}">Login</a> (Stub)</li>'
        ).format(url_client_login=helper_hooks.hooks["urls"]["url_client_login"])
    else:
        login_or_logout = Markup(
            """
            <li><a href="{url_client_logout}">Logout</a> (Stub)</li>
            <li><a href="{url_client_token}">Token</a></li>
            """
        ).format(
            url_client_logout=helper_hooks.hooks["urls"]["url_client_logout"],
            url_client_token=helper_hooks.hooks["urls"]["url_client_token"],
        )
    http.response.body = render(
        "Client",
        Markup(
            """
{breadcrumbs}
<ul>{login_or_logout}</ul>
"""
        ).format(
            login_or_logout=login_or_logout,
            breadcrumbs=helper_navigation_generate_and_cache_breadcrumbs(
                helper_hooks.hooks["urls"]["url_client"]
            ),
        ),
    )


def route_client_token(http):
    session_id, session = get_session_or_respond_early_not_logged_in(
        http, "oauth_code_pkce"
    )
    http.response.body = render(
        title="Client Token",
        body=Markup(
            """
            {breadcrumbs}
            <p>Here's the JWT access token:</p>
            <p><span id="jwt">{access_token}</span></p>"""
        ).format(
            access_token=session.value.get("access_token"),
            url_home=helper_hooks.hooks["urls"]["url_home"],
            url_client=helper_hooks.hooks["urls"]["url_client"],
            breadcrumbs=helper_navigation_generate_and_cache_breadcrumbs(
                helper_hooks.hooks["urls"]["url_client_token"]
            ),
        ),
    )


def route_client_logout(http):
    session_id = get_session_id_or_respond_early_not_logged_in(http, "oauth_code_pkce")
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
        return route_error_not_logged_in(http)
    http.response.body = render(
        title="Logged out",
        body=Markup("""<p>Successfully logged out.</p>"""),
    )
