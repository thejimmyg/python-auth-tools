"""
Steps:

* Render the dashboard page with the JWT in it, don't just return text
* Create a session store [key]: JSON
* Set the session cookie http_only, secure unless http.request.headers['host'] starts with http and DEV_MODE=true
* 
"""

import json
import urllib.parse

import helper_pkce
import plugins
from config_common import url
from helper_http import RespondEarly
from helper_log import log
from render_oauth_client import render_oauth_client_success
from store_oauth_client_flow_code_pkce_code_verifier import (
    CodeVerifierValue,
    get_and_delete_code_verifier_value,
    put_code_verifier_value,
)

# XXX Expiring old code verifiers


def session_from_cookie(http):
    http.response.status = "401 Not logged in"
    http.response.body = "Not logged in"
    raise RespondEarly()


def start_session(http):
    jwt = jwt_from_cookie(http, None)
    http.response.status = "200 OK"
    http.response.body = "OK" + jwt


def oauth_client_flow_code_pkce_callback(http):
    q = urllib.parse.parse_qs(
        http.request.query,
        keep_blank_values=False,
        strict_parsing=True,
        encoding="utf-8",
        max_num_fields=10,
        separator="&",
    )
    assert len(q) >= 1, "Unexpected query string length"
    assert len(q["code"]) == 1
    if "state" in q:
        assert len(q["state"]) == 1
    code_verifier = get_and_delete_code_verifier_value(q["state"][0]).code_verifier
    code = q["code"][0]
    token_url = (
        url
        + "/oauth/token?code_verifier="
        + urllib.parse.quote(code_verifier)
        + "&code="
        + urllib.parse.quote(code)
        + "&grant_type=code"
    )
    # http.response.status = '302 Redirect'
    # http.response.headers['location'] = token_url
    # http.response.body = b'Redirecting ...'

    # XXX Make this spec-compliant
    try:
        log(__file__, "URL:", token_url)
        with urllib.request.urlopen(token_url) as fp:
            response = json.loads(fp.read())
            assert response["token_type"] == "bearer"

            def on_success(http, response):
                global log
                access_token = response["access_token"]
                log(__file__, "Access token:", access_token)
                http.response.body = render_oauth_client_success(jwt=access_token)

            getattr(plugins, "oauth_client_flow_code_pkce_on_success", on_success)(
                http, response
            )
    except urllib.error.HTTPError as e:
        log(__file__, "ERROR:", e.read().decode())
        http.response.body = "Could not get access token."


# XXX Good to send state here too so we can use it to retireve the code_verfier
def oauth_client_flow_code_pkce_login(http):
    q = urllib.parse.parse_qs(
        http.request.query,
        keep_blank_values=False,
        strict_parsing=True,
        encoding="utf-8",
        max_num_fields=1,
        separator="&",
    )
    scope = None
    if "scope" in q:
        assert len(q["scope"]) == 1
        scope = q["scope"][0]

    code_verifier = helper_pkce.code_verifier()
    state = helper_pkce.code_verifier()
    put_code_verifier_value(state, CodeVerifierValue(code_verifier=code_verifier))
    code_challenge = helper_pkce.code_challenge(code_verifier)
    # pair = code_verifier, code_challenge
    http.response.status = "302 Redirect"
    # See https://datatracker.ietf.org/doc/html/rfc7636#section-1.1
    # https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.1
    # Don't need state if using PKCE?
    client = "client"
    authorize_url = (
        url
        + "/oauth/authorize?response_type=code&state="
        + urllib.parse.quote(state)
        + "&client_id="
        + urllib.parse.quote(client)
        + "&code_challenge="
        + urllib.parse.quote(code_challenge)
        + "&code_challenge_method=S256"
    )
    if scope:
        authorize_url += "&scope=" + urllib.parse.quote(scope)
    http.response.headers["location"] = authorize_url
    http.response.body = "Redirecting ..."
