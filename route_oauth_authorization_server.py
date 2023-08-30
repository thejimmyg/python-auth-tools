import base64
import urllib.parse

import helper_hooks
from config import config_url
from config_oauth_authorization_server import (
    config_oauth_authorization_server_jwks_json_path,
)
from helper_log import helper_log
from helper_oauth_authorization_server import helper_oauth_authorization_server_sign_jwt
from helper_pkce import helper_pkce_code_challenge, helper_pkce_code_verifier
from http_session import http_session_get_id
from route_oauth_resource_owner_api import apis
from route_static import route_static
from store_oauth_authorization_server_client_credentials import (
    store_oauth_authorization_server_client_credentials_get,
)
from store_oauth_authorization_server_code_pkce import (
    store_oauth_authorization_server_code_pkce_get,
)
from store_oauth_authorization_server_code_pkce_request import (
    CodePkceRequest,
    store_oauth_authorization_server_code_pkce_request_get_and_delete,
    store_oauth_authorization_server_code_pkce_request_put,
)
from store_oauth_authorization_server_keys_current import (
    store_oauth_authorization_server_keys_current_get_and_cache,
)
from store_session import store_session_get, store_session_put

available_scopes = []
for api in apis:
    for required_scope in apis[api][1]:
        if required_scope not in available_scopes:
            available_scopes.append(required_scope)
helper_log(__file__, "Available scopes:", available_scopes)


def route_oauth_authorization_server_openid_configuration(http):
    http.response.body = {
        "issuer": config_url,
        "authorization_endpoint": config_url + "/oauth/authorize",
        "token_endpoint": config_url + "/oauth/token",
        "jwks_uri": config_url + "/.well-known/jwks.json",
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


def route_oauth_authorization_server_authorize(http):
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
    client = store_oauth_authorization_server_code_pkce_get(client_id)
    scopes = _get_scopes(q)
    # XXX Assert scopes are allowed in the client
    assert client.scopes, client.scopes
    state = None
    if "state" in q:
        assert len(q["state"]) == 1
        state = q["state"][0]
    new_code = helper_pkce_code_verifier()
    session_id = http_session_get_id(http, "oauth")
    if session_id:
        session = store_session_get(session_id)
        sub = session.sub
        assert sub
        code_pkce_request = CodePkceRequest(
            client_id=client_id,
            code_challenge=q["code_challenge"][0],
            scopes=scopes,
            state=state,
            sub=sub,  # Can be None to start with, it should be updated later if it is.
        )
        session.value = dict(code=new_code)
        store_session_put(session_id, session)
        store_oauth_authorization_server_code_pkce_request_put(
            new_code, code_pkce_request
        )
        # We can redirect straight to the consent code
        http.response.status = "302 Redirect"
        http.response.headers["location"] = "/oauth/consent"
        http.response.body = "Redirecting ..."
        helper_log(__file__, "Redirecting to", "/oauth/consent")
        return
    else:
        helper_log(
            __file__,
            "Not signed in, preparing code PKCE request without sub, and triggering login hook",
        )
        code_pkce_request = CodePkceRequest(
            client_id=client_id,
            code_challenge=q["code_challenge"][0],
            scopes=scopes,
            state=state,
            sub=None,
        )
        store_oauth_authorization_server_code_pkce_request_put(
            new_code, code_pkce_request
        )
        # Start a login flow
        helper_hooks.hooks[
            "oauth_authorization_server_on_authorize_when_not_signed_in"
        ](http, new_code)


def route_oauth_authorization_server_token(http):
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
        helper_log(__file__, "Basic authorization header:", creds[6:])
        helper_log(
            __file__, "Base64 decoded basic header:", base64.b64decode(creds[6:] + "==")
        )
        client_id, secret = base64.b64decode(creds[6:] + "==").decode("utf8").split(":")
        # XXX This isn't quite right
        sub = client_id
        client = store_oauth_authorization_server_client_credentials_get(client_id)
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
        code_pkce_request = (
            store_oauth_authorization_server_code_pkce_request_get_and_delete(code)
        )
        if code_pkce_request.sub is None or code_pkce_request.scopes is None:
            raise Exception("Not completed auth flow before trying to get token")
        client_id = code_pkce_request.client_id
        code_challenge = code_pkce_request.code_challenge
        scopes = code_pkce_request.scopes
        sub = code_pkce_request.sub
        helper_log(
            __file__,
            "Authorize code params:",
            code,
            code_verifier,
            code_pkce_request.client_id,
            code_challenge,
            sub,
        )
        # This is the key check - if the code_challenge we recieved at the start can be generated from this code verifier, it is the same client and we can issue a token.
        assert helper_pkce_code_challenge(code_verifier) == code_challenge
    expires_in = 600
    http.response.status = "200 OK"
    http.response.body = {
        "access_token": helper_oauth_authorization_server_sign_jwt(
            client_id=client_id,
            sub=sub,
            expires_in=expires_in,
            scopes=scopes,
            kid=store_oauth_authorization_server_keys_current_get_and_cache(),
        ),
        "token_type": "bearer",
        "expires_in": expires_in,
    }


route_oauth_authorization_server_jwks_json = route_static(
    config_oauth_authorization_server_jwks_json_path,
    "application/json; charset=UTF8",
)
