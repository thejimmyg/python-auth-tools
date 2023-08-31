from http import cookies

from config import config_host, config_scheme
from helper_pkce import helper_pkce_code_verifier


def http_session_get_id(http, name):
    cookie = cookies.SimpleCookie()
    if "cookie" in http.request.headers:
        cookie.load(http.request.headers["cookie"])
    if name in cookie:
        return cookie[name].value
    return None


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
    c["secure"] = config_scheme == "https://"
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
    parts = cookie.output().split(": ")
    if parts[0].lower() in http.response.headers:
        raise Exception("Setting multiple cookies is not supported yet")
    http.response.headers[parts[0].lower()] = ": ".join(parts[1:])
    if "cache-control" in http.response.headers:
        raise Exception("Cannot currently set the cache control headers twice")
    http.response.headers["cache-control"] = 'no-cache="set-cookie"'
