from plugin_oauth_test import (
    plugin_oauth_test_hook_oauth_authorization_server_on_authorize_when_not_signed_in,
    plugin_oauth_test_hook_oauth_authorization_server_is_signed_in,
    plugin_oauth_test_hook_oauth_authorization_server_on_save_code,
    plugin_oauth_test_route_oauth_authorization_server_consent,
    plugin_oauth_test_route_oauth_authorization_server_login,
)
from route_oauth_authorization_server import (
    make_route_oauth_authorization_server_authorize,
    route_oauth_authorization_server_jwks_json,
    route_oauth_authorization_server_openid_configuration,
    route_oauth_authorization_server_token,
)

route_oauth_authorization_server_authorize = make_route_oauth_authorization_server_authorize(
    oauth_authorization_server_on_authorize_when_not_signed_in=plugin_oauth_test_hook_oauth_authorization_server_on_authorize_when_not_signed_in,
    oauth_authorization_server_is_signed_in=plugin_oauth_test_hook_oauth_authorization_server_is_signed_in,
    oauth_authorization_server_on_save_code=plugin_oauth_test_hook_oauth_authorization_server_on_save_code,
)


def route_authorizationserver(http):
    if http.request.path == "/.well-known/jwks.json":
        return route_oauth_authorization_server_jwks_json(http)
    elif http.request.path == "/.well-known/openid-configuration":
        return route_oauth_authorization_server_openid_configuration(http)
    elif http.request.path == "/oauth/authorize":
        return route_oauth_authorization_server_authorize(http)
    elif http.request.path == "/oauth/login":
        return plugin_oauth_test_route_oauth_authorization_server_login(http)
    elif http.request.path == "/oauth/consent":
        return plugin_oauth_test_route_oauth_authorization_server_consent(http)
    elif http.request.path == "/oauth/token":
        return route_oauth_authorization_server_token(http)
    http.response.status = "404 Not Found"
    http.response.body = b"404 Not Found"
