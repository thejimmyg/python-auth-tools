import traceback

from helper_log import helper_log

from plugin_oauth_test import (
    plugin_oauth_test_hook_oauth_authorization_server_is_signed_in,
    plugin_oauth_test_hook_oauth_authorization_server_on_authorize_when_not_signed_in,
    plugin_oauth_test_hook_oauth_authorization_server_on_save_code,
    plugin_oauth_test_hook_oauth_code_pkce_on_success,
    plugin_oauth_test_route_oauth_authorization_server_consent,
    plugin_oauth_test_route_oauth_authorization_server_login,
)
from render import Base, Html
from route_error import route_error_not_found
from route_oauth_authorization_server import (
    make_route_oauth_authorization_server_authorize,
    route_oauth_authorization_server_jwks_json,
    route_oauth_authorization_server_openid_configuration,
    route_oauth_authorization_server_token,
)
from route_oauth_code_pkce import (
    make_route_oauth_code_pkce_callback,
    route_oauth_code_pkce_login,
)
from route_oauth_resource_owner import (
    route_oauth_resource_owner_home,
    route_oauth_resource_owner_openapi,
)
from route_oauth_resource_owner_api import route_oauth_resource_owner_api_v1
from route_saml_sp import route_saml_sp_acs, route_saml_sp_login
from route_static import route_static
from route_webhook_provider import route_webhook_provider_jwks_json


class Home(Base):
    def __init__(self, title):
        self._title = title

    def body(self):
        return Html(
            """\
      <p>
        <a href="/oauth-code-pkce/login">Login without scopes</a>,
        <a href="/oauth-code-pkce/login?scope=read">login with read scope</a>,
        <a href="/oauth-code-pkce/login?scope=read%20offline_access">login with read and offline access scopes</a>,
        <a href="/oauth-code-pkce/login?scope=no-such-scope">login with an invalid scope</a>,
        <a href="/saml2/login/">login with SAML</a>.
      </p>"""
        )


def route_home(http):
    http.response.body = Home(title="OAuth Client Home")


routes = {
    "/saml2/login/": route_saml_sp_login,
    "/saml2/acs/": route_saml_sp_acs,
    "/": route_home,
    "*": route_error_not_found,
    # These API routes need re-designing in light of serve
    "/resource-owner/api": route_oauth_resource_owner_home,
    "/resource-owner/api/v1": route_oauth_resource_owner_api_v1,
    "/resource-owner/api/openapi.json": route_oauth_resource_owner_openapi,
    "/static/file": route_static("static/file", "text/plain"),
    "/.well-known/jwks.json": route_oauth_authorization_server_jwks_json,
    "/.well-known/webhook-provider-jwks.json": route_webhook_provider_jwks_json,
    "/.well-known/openid-configuration": route_oauth_authorization_server_openid_configuration,
    "/oauth-code-pkce/login": route_oauth_code_pkce_login,
    "/oauth-code-pkce/callback": make_route_oauth_code_pkce_callback(
        oauth_code_pkce_on_success=plugin_oauth_test_hook_oauth_code_pkce_on_success
    ),
    "/oauth/authorize": make_route_oauth_authorization_server_authorize(
        oauth_authorization_server_on_authorize_when_not_signed_in=plugin_oauth_test_hook_oauth_authorization_server_on_authorize_when_not_signed_in,
        oauth_authorization_server_is_signed_in=plugin_oauth_test_hook_oauth_authorization_server_is_signed_in,
        oauth_authorization_server_on_save_code=plugin_oauth_test_hook_oauth_authorization_server_on_save_code,
    ),
    "/oauth/login": plugin_oauth_test_route_oauth_authorization_server_login,
    "/oauth/consent": plugin_oauth_test_route_oauth_authorization_server_consent,
    "/oauth/token": route_oauth_authorization_server_token,
}

def app(http):
    request_path = http.request.path
    # assert request_path != '*' # Actually it can be * because this will just call the same thing as the * route anyway
    # if request_path == "/":
    #    request_path = ""

    try:
        route = routes.get(request_path)
        found = False
        if route:
            route(http)
            found = True
        if not found:
            candidates = []
            for path in routes:
                if (
                    path != "/"
                    and path.endswith("/")
                    and http.request.path.startswith(path)
                ):
                    candidates.append(path)
            if candidates:
                # Choose the longest matching candidate
                routes[sorted(candidates)[-1]](http)
                found = True
        if not found:
            if "*" in routes:
                routes["*"](http)
            else:
                # This should never happen because you can always add a route {..., "*": not_found, ...}
                http.response.status = "404 Not Found"
                http.response.body = b"404 Not Found"
    except http.response.RespondEarly:
        pass
    except Exception:
        # Keep whatever headers have been set (e.g. cookies), but show a 500
        http.response.status = "500 Error"
        http.response.body = b"500 Error"
        helper_log(__file__, "ERROR:", traceback.format_exc())
    # _canonicalize_response(http)

# def _canonicalize_response(http):
#     response_body_changed = False
#     auto_content_type: bytes = None
#     if type(http.response.body) is str:
#         http.response.body = http.response.body.encode("utf8")
#         response_body_changed = True
#         auto_content_type = "text/plain; charset=UTF8"
#     elif type(http.response.body) is dict:
#         http.response.body = json.dumps(http.response.body).encode("utf8")
#         response_body_changed = True
#         auto_content_type = "application/json; charset=UTF8"
#     lower_response_headers = {}
#     content_length_found = False
#     content_type_found = False
#     for k in http.response.headers:
#         lower_k = k.lower()
#         if lower_k in lower_response_headers:
#             raise Exception(f"Duplicate key {lower_k} in response headers")
#         lower_response_headers[lower_k] = http.response.headers[k]
#         if lower_k == "content-length":
#             # This can't happen since we are using a dictionary
#             # if content_length_found is True:
#             #     raise Exception(
#             #         "Multiple content length headers in response"
#             #     )
#             content_length_found = True
#         if response_body_changed and lower_k == "content-type":
#             # if content_type_found is True:
#             #    raise Exception(
#             #        "Multiple content type headers in response"
#             #    )
#             content_type_found = True
#     if response_body_changed and not content_type_found:
#         lower_response_headers["content-type"] = auto_content_type
#     if http.response.body and not content_length_found:
#         lower_response_headers["content-length"] = str(len(http.response.body))
#     http.response.headers = lower_response_headers
