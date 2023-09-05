import urllib.parse

from markupsafe import Markup

from helper_log import helper_log
from helper_meta_refresh import helper_meta_refresh_html
from helper_oauth_authorization_server import (
    helper_oauth_authorization_server_prepare_redirect_uri,
)
from http_session import http_session_create, http_session_get_id
from render import render
from store_oauth_authorization_server_code_pkce import (
    store_oauth_authorization_server_code_pkce_get,
)
from store_oauth_authorization_server_code_pkce_consent import (
    store_oauth_authorization_code_pkce_consent_get,
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
    helper_log(__file__, "In login hook")
    session_id = http_session_get_id(http, "oauth")
    if not session_id:
        http.response.status = "401 Not Authenticated"
        http.response.body = "401 Not Authenticated"
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
        # Note we don't really need a CSRF check here because a username and password would really be used to authenticate the request
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
        http.response.status = "302 Redirect"
        http.response.headers["location"] = "/oauth/consent"
        http.response.body = "Redirecting ..."
        helper_log(__file__, "Redirecting to", "/oauth/consent")


def plugin_oauth_test_route_oauth_authorization_server_consent(http):
    session_id = http_session_get_id(http, "oauth")
    if not session_id:
        http.response.status = "401 Not Authenticated"
        http.response.body = "401 Not Authenticated"
        return
    session = store_session_get(session_id)
    try:
        code_pkce_request = store_oauth_authorization_code_pkce_request_get(
            session.value["code"]
        )
        code_pkce = store_oauth_authorization_server_code_pkce_get(
            code_pkce_request.client_id
        )
    except Exception as e:
        helper_log(__file__, e)
        http.response.body = "OAuth flow has expired. Please try again."
        return

    url = helper_oauth_authorization_server_prepare_redirect_uri(
        session.value["code"],
        code_pkce_request,
        code_pkce.redirect_uri,
    )
    if not code_pkce_request.scopes:
        http.response.body = helper_meta_refresh_html(url)
        return
    try:
        code_pkce_consent = store_oauth_authorization_code_pkce_consent_get(
            session.sub, code_pkce_request.client_id
        )
        print("\n\n=========================\n\n", code_pkce_consent)
        for scope in code_pkce_request.scopes:
            if scope not in code_pkce_consent.scopes:
                raise Exception("Scope not consented to", scope)
        # Otherwise we're all good. Redirect
        http.response.body = helper_meta_refresh_html(url)
        return
    except Exception:
        helper_log(
            __file__,
            f"No code PKCE consent for {session.sub} {code_pkce_request.client_id}",
        )
        if http.request.method == "post":
            body = http.request.body.decode("utf8")
            form = urllib.parse.parse_qs(
                body,
                keep_blank_values=False,
                strict_parsing=True,
                encoding="utf-8",
                max_num_fields=10,
                separator="&",
            )
            csrfs = form.get("csrf", [])
            assert len(csrfs) == 1
            if csrfs[0] != session.csrf:
                raise Exception("CSRF check failed")
            approves = form.get("approve", [])
            if len(approves) == 1 and approves[0] == "Approve":
                helper_log(__file__, "We've approved the request")
                http.response.body = helper_meta_refresh_html(url)
                return
            else:
                helper_log(
                    __file__, "We've rejected the request or done something strange"
                )
                del session.value["code"]
                store_session_put(session_id, session)
                http.response.body = "Rejected!"
                return
        else:
            http.response.body = render(
                title="Permissions Consent",
                body=Markup(
                    """
                <p id="consent-msg">The page at {redirect_uri} is asking for the following permissions to your data:</p>

                {permissions}

                <form method="POST" action="">
                  <input type="hidden" name="csrf" value="{csrf}">
                  <input type="submit" name="approve" value="Approve">
                  <input type="submit" name="reject" value="Reject">
                </form>
                """.format(
                        redirect_uri=code_pkce.redirect_uri,
                        csrf=session.csrf,
                        permissions=Markup("<ul><li>")
                        + Markup("</li><li>").join(code_pkce_request.scopes)
                        + Markup("</li></ul>"),
                    )
                ),
            )
            return


def plugin_oauth_test_hook_oauth_authorization_server_is_signed_in(http):
    try:
        session_id = http_session_get_id(http, "oauth")
        session = store_session_get(session_id)
        sub = session.sub
        assert sub
    except Exception as e:
        helper_log(
            __file__,
            "Not signed in, preparing code PKCE request without sub, and triggering login hook",
            e,
        )
        return False, None, None
    else:
        return True, sub, dict(session_id=session_id, session=session)


def plugin_oauth_test_hook_oauth_authorization_server_on_save_code(
    http, context, new_code
):
    session = context["session"]
    session_id = context["session_id"]
    session.value.update(dict(code=new_code))
    store_session_put(session_id, session)
