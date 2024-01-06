from http import cookies

from helper_log import helper_log
from config import config_host, config_scheme
from error import NotFound
from helper_pkce import helper_pkce_code_verifier
from route_error import route_error_not_logged_in
from store_session import store_session_get


def http_session_id(http, name):
    cookie = cookies.SimpleCookie()
    if "cookie" in http.request.headers:
        cookie.load(http.request.headers["cookie"])
    else:
        helper_log(__file__, f"No cookies found in the HTTP headers")
        raise NotFound(f"No cookies found in the HTTP headers")
    if name in cookie:
        return cookie[name].value
    raise NotFound(f"No session ID in cookie '{name}'")


def http_session_create(http, name):
    assert name
    session_id = helper_pkce_code_verifier()
    cookie = cookies.SimpleCookie()
    # if "cookie" in http.request.headers:
    #     cookie.load(http.request.headers["cookie"])
    cookie[name] = session_id
    _default_cookie_settings(http, cookie[name])
    _set_response_cookie_header(http, cookie)
    return session_id


def _default_cookie_settings(http, c):
    c["path"] = "/"
    # Can't use the port here https://datatracker.ietf.org/doc/html/rfc2109.html#section-2
    c["domain"] = config_host
    c["max-age"] = 3600
    c["secure"] = config_scheme == "https"
    c["version"] = 1
    c["httponly"] = True
    c["samesite"] = "Strict"


def http_session_destroy(http, name):
    assert name
    cookie = cookies.SimpleCookie()
    # if "cookie" in http.request.headers:
    #     cookie.load(http.request.headers["cookie"])
    cookie[name] = ""
    _default_cookie_settings(http, cookie[name])
    # Now make it expire immediately
    cookie[name]["max-age"] = 0
    _set_response_cookie_header(http, cookie)


def _set_response_cookie_header(http, cookie):
    # XXX But what to do about headers that are already set?
    # XXX This is why it is better to have an array, rather than dict for response headers
    lower_response_headers = [k.lower() for k in http.response.headers]
    parts = cookie.output().split(": ")
    assert parts[0].lower().strip() == 'set-cookie', parts[0]
    if parts[0].lower() in lower_response_headers:
        raise Exception("Setting multiple cookies is not supported yet")
    http.response.headers['Set-Cookie'] = ": ".join(parts[1:])
    if "Cache-Control".lower() in lower_response_headers:
        raise Exception("Cannot currently set the cache control headers twice")
    http.response.headers["Cache-Control"] = 'no-cache="set-cookie"'


def get_session_id_or_respond_early_not_logged_in(http, name):
    helper_log(__file__, f"Attempting to load session id {repr(name)}")
    try:
        session_id = http_session_id(http, name)
        helper_log(__file__, f"Success: {repr(session_id)}")
        return session_id
    except NotFound as e:
        helper_log(__file__, f"Could not load session_id {name}: {e}")
        route_error_not_logged_in(http)
        raise http.response.RespondEarly(str(e))


def get_session_or_respond_early_not_logged_in(http, name):
    helper_log(__file__, f"Attempting to load session id {repr(name)}")
    try:
        session_id = http_session_id(http, name)
        helper_log(__file__, f"Success: {repr(session_id)}")
        helper_log(__file__, f"Attempting to load session {session_id}")
        session = store_session_get(session_id)
        helper_log(__file__, f"Success: {repr(session)}")
        return session_id, session
    except NotFound as e:
        helper_log(__file__, f"Error loading session_id and session {name}: {e}")
        route_error_not_logged_in(http)
        raise http.response.RespondEarly(str(e))
