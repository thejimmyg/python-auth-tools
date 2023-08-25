import json
import urllib.parse

from saml2 import BINDING_HTTP_POST

from helper_saml_sp import saml_client
from render_saml_sp import render_saml_sp_success


def route_saml_sp_login(http):
    client = saml_client()
    request_id, info = client.prepare_for_authenticate()
    redirect_url = dict(info["headers"])["Location"]
    http.response.headers["location"] = redirect_url
    http.response.status = "302 Redirect"
    http.response.body = "Redirecting ..."


def route_saml_sp_acs(http):
    client = saml_client()
    q = urllib.parse.parse_qs(
        http.request.body.decode("utf8"),
        keep_blank_values=False,
        strict_parsing=True,
        encoding="utf-8",
        max_num_fields=10,
        separator="&",
    )
    authn_response = client.parse_authn_request_response(
        q["SAMLResponse"][0], BINDING_HTTP_POST
    )
    session_info = authn_response.session_info()
    # Serialise the NameID class
    session_info["name_id"] = str(session_info["name_id"])
    http.response.body = render_saml_sp_success(session_info=json.dumps(session_info))
