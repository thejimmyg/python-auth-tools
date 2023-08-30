import urllib.parse

from markupsafe import Markup

from helper_log import helper_log
from helper_meta_refresh import helper_meta_refresh_html
from http_session import http_session_create, http_session_get_id
from render import render
from route_oauth_authorization_server import _make_url
from store_oauth_authorization_server_code_pkce import (
    store_oauth_authorization_server_code_pkce_get,
)
from store_oauth_authorization_server_code_pkce_request import (
    store_oauth_authorization_code_pkce_request_get,
    store_oauth_authorization_server_code_pkce_request_set_sub,
)
from store_session import (
    Session,
    store_session_get,
    store_session_put,
    store_session_set_sub,
)


def plugin_oauth_test_hook_oauth_code_pkce_on_success(http, response):
    global log
    access_token = response["access_token"]
    helper_log(__file__, "Access token:", access_token)
    http.response.body = render(
        title="Success!",
        body=Markup(
            """<p>Successfully logged in. Here's the access token: <span id="jwt">{access_token}</span></p>"""
        ).format(access_token=access_token),
    )


def plugin_oauth_test_hook_oauth_authorization_server_on_authorize_when_not_signed_in(
    http, new_code
):
    # At this point we need some sort of session so that we can handle login interactions and then update the claims with the sub (and anything else).
    # We should redirect away from the authorize URL to continue the flow
    session_id = http_session_create(http, "oauth")
    store_session_put(session_id, Session(value=dict(code=new_code), sub=None))
    http.response.body = helper_meta_refresh_html("/oauth/login")


def plugin_oauth_test_route_oauth_authorization_server_login(http):
    session_id = http_session_get_id(http, "oauth")
    if not session_id:
        return
    sub = ""
    if http.request.method == "post":
        form = urllib.parse.parse_qs(
            http.request.body.decode("utf8"),
            keep_blank_values=False,
            strict_parsing=True,
            encoding="utf-8",
            max_num_fields=10,
            separator="&",
        )
        subs = form.get("sub", [])
        if len(subs) == 1:
            sub = subs[0]
    if http.request.method == "get" or not sub:
        form = Markup(
            """
            <form method="post">
                <input type="text" name="sub" placeholder="sub" value="{sub}">
                <input type="submit">
            </form>
            <p>Session ID is: {session_id}"""
        ).format(session_id=session_id, sub=sub)
        http.response.body = render(title="Login", body=form)
    else:
        session = store_session_get(session_id)
        store_session_set_sub(session_id, sub)
        store_oauth_authorization_server_code_pkce_request_set_sub(
            session.value["code"], sub
        )
        # XXX This should actually lookup consent, and if needed redirect to the consent screen
        code_pkce_request = store_oauth_authorization_code_pkce_request_get(
            session.value["code"]
        )
        url = _make_url(
            session.value["code"],
            code_pkce_request,
            store_oauth_authorization_server_code_pkce_get(
                code_pkce_request.client_id
            ).redirect_uri,
        )
        http.response.status = "302 Redirect"
        http.response.headers["location"] = url
        http.response.body = "Redirecting ..."


def plugin_oauth_test_route_oauth_authorization_server_consent(http):
    http.response.body = render(title="Not yet", body="Need to ask for consent here.")
