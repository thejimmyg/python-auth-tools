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
    session = helper_pkce_code_verifier()
    cookie = cookies.SimpleCookie()
    if "cookie" in http.request.headers:
        cookie.load(http.request.headers["cookie"])
    cookie[name] = session
    # cookie['oauth']['expires'] =
    cookie[name]["path"] = "/"
    cookie[name]["comment"] = "upstream oauth"
    cookie[name][
        "domain"
    ] = config_host  # Can't use the port here https://datatracker.ietf.org/doc/html/rfc2109.html#section-2
    cookie[name]["max-age"] = 3600
    cookie["oauth"]["secure"] = config_scheme == "https://"
    cookie[name]["version"] = 1
    cookie[name]["httponly"] = True
    cookie[name]["samesite"] = "Strict"
    parts = cookie.output().split(": ")
    http.response.headers[parts[0].lower()] = ": ".join(parts[1:])
    # Should check already set?
    http.response.headers["cache-control"] = 'no-cache="set-cookie"'
    return session
