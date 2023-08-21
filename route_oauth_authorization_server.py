import base64
import urllib.parse

from markupsafe import Markup

import helper_pkce
from config_common import url
from config_oauth_authorization_server import oauth_authorization_server_jwks_json_path
from helper_log import log
from helper_oauth_authorization_server import sign_jwt
from http_session import get_session_id, login
from render import render_main
from route_oauth_resource_owner_api import apis
from route_static import static
from store_oauth_authorization_server_clients_client_credentials import (
    get_client_credentials_client,
)
from store_oauth_authorization_server_clients_code import get_code_client
from store_oauth_authorization_server_codes import (
    CodeValue,
    get_and_delete_code_value,
    get_code_value,
    put_code_value,
    set_code_sub,
)
from store_oauth_authorization_server_keys import get_and_cache_current_kid_value
from store_oauth_authorization_server_session import (
    SessionValue,
    get_session_value,
    put_session_value,
)

available_scopes = []
for api in apis:
    for required_scope in apis[api][1]:
        if required_scope not in available_scopes:
            available_scopes.append(required_scope)
log(__file__, "Available scopes:", available_scopes)


def _make_url(code, code_value, redirect_uri):
    url = redirect_uri + "?"
    if code_value.state:
        url += "state=" + urllib.parse.quote(code_value.state)
        url += "&code=" + urllib.parse.quote(code)
    else:
        url += "code=" + urllib.parse.quote(code)
    return url


def oauth_authorization_server_openid_configuration(http):
    http.response.body = {
        "issuer": url,
        "authorization_endpoint": url + "/oauth/authorize",
        "token_endpoint": url + "/oauth/token",
        "jwks_uri": url + "/.well-known/jwks.json",
        "grant_types_supported": [
            "authorization_code",
            "client_credentials",
        ],
        "token_endpoint_auth_methods_supported": ["client_secret_basic"],
        "scopes_supported": ["openid", "profile"],
        "code_challenge_methods_supported": ["S256"],
    }


def _get_scopes(q):
    scopes = []
    if "scope" in q:
        for scope in q["scope"][0].split(" "):
            assert scope in available_scopes, "Not a known scope: " + scope
            scopes.append(scope)
    return scopes


def oauth_authorization_server_authorize(http):
    q = urllib.parse.parse_qs(
        http.request.query,
        keep_blank_values=False,
        strict_parsing=True,
        encoding="utf-8",
        max_num_fields=10,
        separator="&",
    )
    assert len(q) >= 5, "Unexpected query string length"
    assert len(q["response_type"]) == 1
    assert q["response_type"][0] == "code", "response_type != code"
    assert len(q["code_challenge_method"]) == 1
    assert q["code_challenge_method"][0] == "S256", "code_challenge != S256"
    assert len(q["code_challenge"]) == 1
    assert len(q["client_id"]) == 1
    client_id = q["client_id"][0]
    client = get_code_client(client_id)
    scopes = _get_scopes(q)
    # XXX Assert scopes are allowed in the client
    assert client.scopes, client.scopes
    state = None
    if "state" in q:
        assert len(q["state"]) == 1
        state = q["state"][0]
    session_id = get_session_id(http, "oauth")
    logged_in = False
    approved_scopes = False
    sub = None
    if session_id:
        logged_in = True
        approved_scopes = True
        sub = "sub2"
    new_code = helper_pkce.code_verifier()
    code_value = CodeValue(
        client_id=client_id,
        code_challenge=q["code_challenge"][0],
        scopes=scopes,
        state=state,
        sub=sub,
    )
    put_code_value(new_code, code_value)
    if logged_in and approved_scopes:
        # We know the sub, so we can issue the code
        url = _make_url(new_code, code_value, client.redirect_uri)
        http.response.status = "302 Redirect"
        http.response.headers["location"] = url
        http.response.body = "Redirecting ..."
    else:
        # At this point we need some sort of session so that we can handle login interactions and then update the claims with the sub (and anything else)
        session_id = login(http, "oauth")
        put_session_value(session_id, SessionValue(code=new_code))
        http.response.body = Markup(
            '<html><head><meta http-equiv="refresh" content="0; url={path}"></head><body><a href="{path}"></a></body></html>'
        ).format(path="/oauth/login")


def oauth_authorization_server_login(http):
    session_id = get_session_id(http, "oauth")
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
        http.response.body = render_main(title="Login", body=form)
    else:
        session = get_session_value(session_id)
        set_code_sub(session.code, sub)
        # XXX This should actually lookup consent, and if needed redirect to the consent screen
        code_value = get_code_value(session.code)
        url = _make_url(
            session.code, code_value, get_code_client(code_value.client_id).redirect_uri
        )
        http.response.status = "302 Redirect"
        http.response.headers["location"] = url
        http.response.body = "Redirecting ..."


def oauth_authorization_server_consent(http):
    http.response.body = render_main(
        title="Not yet", body="Need to ask for consent here."
    )


def oauth_authorization_server_token(http):
    # For client credentials
    # See https://datatracker.ietf.org/doc/html/rfc6749#section-4.4
    # grant_type=client_credentials
    # Authorization: Basic czZCaGRSa3F0MzpnWDFmQmF0M2JW
    # get client id/client secret
    # return access_token
    # curl -H 'Authorization: Basic client:secret' -v "${URL}/oauth/token?grant_type=client_credentials"
    http.response.status = "400 Bad Request"
    http.response.headers["content-type"] = "application/json;charset=UTF-8"
    http.response.headers["cache-control"] = "no-store"
    http.response.headers["pragma"] = "no-cache"

    q = urllib.parse.parse_qs(
        http.request.query,
        keep_blank_values=False,
        strict_parsing=True,
        encoding="utf-8",
        max_num_fields=10,
        separator="&",
    )
    assert len(q) >= 1, "Unexpected query string length"
    assert "grant_type" in q
    assert len(q["grant_type"]) == 1
    grant_type = q["grant_type"][0]
    assert grant_type in ["client_credentials", "code"]

    if grant_type == "client_credentials":
        # http.request.query != 'grant_type=client_credentials':
        # http.response.body = {'error': 'invalid_request', 'error_description': "Expected only 'grant_type=client_credentials' as the query string"}
        # return
        creds = http.request.headers.get("authorization", "").strip()
        if creds[:6].lower() != "basic ":
            # Perhaps this should be a 401? https://datatracker.ietf.org/doc/html/rfc6749#section-5.1
            http.response.body = {
                "error": "invalid_request",
                "error_description": "Expected basic Authorization header",
            }
            return
        log(__file__, "Basic authorization header:", creds[6:])
        log(
            __file__, "Base64 decoded basic header:", base64.b64decode(creds[6:] + "==")
        )
        client_id, secret = base64.b64decode(creds[6:] + "==").decode("utf8").split(":")
        # XXX This isn't quite right
        sub = client_id
        client = get_client_credentials_client(client_id)
        if secret != client.client_secret:
            http.response.body = {
                "error": "invalid_client",
                "error_description": "Invalid credentials",
            }
            return
        allowed_scopes = client.scopes
        scopes = _get_scopes(q)
        for scope in scopes:
            assert (
                scope in allowed_scopes
            ), "Scope is available in the app but not allowed in the client credentials client"
    elif grant_type == "code":
        assert "code" in q
        assert len(q["code"]) == 1
        assert "code_verifier" in q
        assert len(q["code_verifier"]) == 1
        code = q["code"][0]
        code_verifier = q["code_verifier"][0]
        code_value = get_and_delete_code_value(code)
        if code_value.sub is None or code_value.scopes is None:
            raise Exception("Not completed auth flow before trying to get token")
        client_id = code_value.client_id
        code_challenge = code_value.code_challenge
        scopes = code_value.scopes
        sub = code_value.sub
        log(
            __file__,
            "Authorize code params:",
            code,
            code_verifier,
            code_value.client_id,
            code_challenge,
            sub,
        )
        # This is the key check - if the code_challenge we recieved at the start can be generated from this code verifier, it is the same client and we can issue a token.
        assert helper_pkce.code_challenge(code_verifier) == code_challenge
    expires_in = 600
    http.response.status = "200 OK"
    http.response.body = {
        "access_token": sign_jwt(
            client_id=client_id,
            sub=sub,
            expires_in=expires_in,
            scopes=scopes,
            kid=get_and_cache_current_kid_value(),
        ),
        "token_type": "bearer",
        "expires_in": expires_in,
    }


oauth_authorization_server_jwks_json = static(
    oauth_authorization_server_jwks_json_path,
    "application/json; charset=UTF8",
)
