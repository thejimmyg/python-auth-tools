from app_test import hooks
from plugin_oauth_session import (
    plugin_oauth_session_hook_oauth_code_pkce_on_success,
    plugin_oauth_session_route_dashboard,
    plugin_oauth_session_route_logout,
)

hooks["routes"]["/oauth-code-pkce/logout"] = plugin_oauth_session_route_logout
hooks["routes"]["/oauth-code-pkce/dashboard"] = plugin_oauth_session_route_dashboard
hooks[
    "oauth_code_pkce_on_success"
] = plugin_oauth_session_hook_oauth_code_pkce_on_success
