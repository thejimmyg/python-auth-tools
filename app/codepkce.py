from plugin_oauth_test import (
    plugin_oauth_test_hook_oauth_code_pkce_on_success,
)
from route_oauth_code_pkce import (
    make_route_oauth_code_pkce_callback,
    route_oauth_code_pkce_login,
)

route_oauth_code_pkce_callback = make_route_oauth_code_pkce_callback(
    oauth_code_pkce_on_success=plugin_oauth_test_hook_oauth_code_pkce_on_success
)


def route_codepkce(http):
    if http.request.path == "/oauth-code-pkce/login":
        return route_oauth_code_pkce_login(http)
    elif http.request.path == "/oauth-code-pkce/callback":
        return route_oauth_code_pkce_callback(http)

    http.response.status = "404 Not Found"
    http.response.body = b"404 Not Found"
