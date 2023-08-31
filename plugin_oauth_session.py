from markupsafe import Markup

from helper_log import helper_log
from helper_meta_refresh import helper_meta_refresh_html
from helper_oauth_resource_owner import helper_oauth_resource_owner_verify_jwt
from http_session import http_session_create, http_session_destroy, http_session_get_id
from render import render
from store_session import (
    Session,
    store_session_destroy,
    store_session_get,
    store_session_put,
)


def plugin_oauth_session_hook_oauth_code_pkce_on_success(http, response):
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


def not_logged_in(http):
    http.response.status = "401 Not Authenticated"
    http.response.body = render(
        title="Not Logged In", body=Markup("""<p>Not logged in.</p>""")
    )


def make_route_token(
    name,
    key="access_token",
    markup=Markup(
        """<p>Successfully logged in. Here's the access token: <span id="jwt">{access_token}</span></p>"""
    ),
):
    assert type(markup) is Markup

    def route_token(http):
        session_id = http_session_get_id(http, name)
        try:
            session = store_session_get(session_id)
        except Exception as e:
            helper_log(__file__, e)
            return not_logged_in(http)
        http.response.body = render(
            title="Token",
            body=markup.format(
                access_token=session.value.get(key), session_id=session_id
            ),
        )

    return route_token


plugin_oauth_session_route_dashboard = make_route_token("oauth_code_pkce")


def make_plugin_oauth_session_route_logout(name):
    def plugin_oauth_session_route_logout(http):
        session_id = http_session_get_id(http, name)
        try:
            store_session_destroy(session_id)
        except:
            return not_logged_in(http)
        try:
            http_session_destroy(http, name)
        except:
            return not_logged_in(http)
        http.response.body = render(
            title="Logged out",
            body=Markup("""<p>Successfully logged out.</p>"""),
        )

    return plugin_oauth_session_route_logout


plugin_oauth_session_route_logout = make_plugin_oauth_session_route_logout(
    "oauth_code_pkce"
)
