from route_error import route_error_not_found

from route_webhook_provider import route_webhook_provider_jwks_json
from route_static import route_static
from .home import route_home
from .saml import route_saml
from .resourceowner import route_resourceowner
from .authorizationserver import route_authorizationserver
from .codepkce import route_codepkce


import traceback
from helper_log import helper_log


def app(http):
    if http.request.path == "/":
        return route_home(http)
    elif http.request.path == "/static/file":
        return route_static("static/file", "text/plain")(http)
    elif http.request.path.startswith("/saml2/"):
        return route_saml(http)
    elif http.request.path == "/.well-known/webhook-provider-jwks.json":
        return route_webhook_provider_jwks_json(http)
    elif http.request.path.startswith("/resource-owner/"):
        return route_resourceowner(http)
    elif http.request.path.startswith("/oauth/") or http.request.path in [
        "/.well-known/jwks.json",
        "/.well-known/openid-configuration",
    ]:
        return route_authorizationserver(http)
    elif http.request.path.startswith("/oauth-code-pkce/"):
        return route_codepkce(http)
    return route_error_not_found(http)
