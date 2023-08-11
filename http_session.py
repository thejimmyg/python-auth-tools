from http import cookies

import helper_pkce
from config_common import host, scheme


def get_session_id(http, name):
    cookie = cookies.SimpleCookie()
    if "cookie" in http.request.headers:
        cookie.load(http.request.headers["cookie"])
    if name in cookie:
        return cookie[name].value
    return None


def login(http, name):
    session = helper_pkce.code_verifier()
    cookie = cookies.SimpleCookie()
    if "cookie" in http.request.headers:
        cookie.load(http.request.headers["cookie"])
    cookie[name] = session
    # cookie['oauth']['expires'] =
    cookie[name]["path"] = "/"
    cookie[name]["comment"] = "upstream oauth"
    cookie[name][
        "domain"
    ] = host  # Can't use the port here https://datatracker.ietf.org/doc/html/rfc2109.html#section-2
    cookie[name]["max-age"] = 3600
    cookie["oauth"]["secure"] = scheme == "https://"
    cookie[name]["version"] = 1
    cookie[name]["httponly"] = True
    cookie[name]["samesite"] = "Strict"
    parts = cookie.output().split(": ")
    http.response.headers[parts[0].lower()] = ": ".join(parts[1:])
    # Should check already set?
    http.response.headers["cache-control"] = 'no-cache="set-cookie"'
    return session
