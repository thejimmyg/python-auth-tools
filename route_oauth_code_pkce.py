"""
Steps:

* Render the dashboard page with the JWT in it, don't just return text
* Create a session store [key]: JSON
* Set the session cookie http_only, secure unless http.request.headers['host'] starts with http and DEV_MODE=true
* 
"""

import json
import urllib.parse

import helper_hooks
from config import config_url
from helper_log import helper_log
from helper_pkce import helper_pkce_code_challenge, helper_pkce_code_verifier
from store_oauth_code_pkce_code_verifier import (
    CodeVerifier,
    store_oauth_code_pkce_code_verifier_get_and_delete,
    store_oauth_code_pkce_code_verifier_put,
)

# XXX Expiring old code verifiers


# def session_from_cookie(http):
#     http.response.status = "401 Not logged in"
#     http.response.body = "Not logged in"
#     raise RespondEarly()
#
#
# def start_session(http):
#     jwt = jwt_from_cookie(http, None)
#     http.response.status = "200 OK"
#     http.response.body = "OK" + jwt


def route_oauth_code_pkce_callback(http):
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
    code_verifier = store_oauth_code_pkce_code_verifier_get_and_delete(
        q["state"][0]
    ).code_verifier
    code = q["code"][0]
    token_url = (
        config_url
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
        helper_log(__file__, "URL:", token_url)
        with urllib.request.urlopen(token_url) as fp:
            response = json.loads(fp.read())
            assert response["token_type"] == "bearer"
            helper_hooks.hooks["oauth_code_pkce_on_success"](http, response)
    except urllib.error.HTTPError as e:
        helper_log(__file__, "ERROR:", e.read().decode())
        http.response.body = "Could not get access token."


# XXX Good to send state here too so we can use it to retireve the code_verfier
def route_oauth_code_pkce_login(http):
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

    code_verifier = helper_pkce_code_verifier()
    state = helper_pkce_code_verifier()
    store_oauth_code_pkce_code_verifier_put(
        state, CodeVerifier(code_verifier=code_verifier)
    )
    code_challenge = helper_pkce_code_challenge(code_verifier)
    # pair = code_verifier, code_challenge
    http.response.status = "302 Redirect"
    # See https://datatracker.ietf.org/doc/html/rfc7636#section-1.1
    # https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.1
    # Don't need state if using PKCE?
    client = "client"
    authorize_url = (
        config_url
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
