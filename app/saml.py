from route_saml_sp import route_saml_sp_acs, route_saml_sp_login


def route_saml(http):
    if http.request.path == "/saml2/login/":
        return route_saml_sp_login(http)
    elif http.request.path == "/saml2/acs/":
        return route_saml_sp_acs(http)
    http.response.status = "404 Not Found"
    http.response.body = b"404 Not Found"
