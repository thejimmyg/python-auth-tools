from markupsafe import Markup

import helper_hooks
from http_session import http_session_get_id
from render import render


def route_client_home(http):
    session_id = http_session_get_id(http, "oauth_code_pkce")
    if session_id:
        login_or_logout = Markup(
            """
            <li><a href="{url_client_logout}">Logout</a> (Stub)</li>
            <li><a href="{url_client_token}">Token</a></li>
            """
        ).format(
            url_client_logout=helper_hooks.hooks["urls"]["url_client_logout"],
            url_client_token=helper_hooks.hooks["urls"]["url_client_token"],
        )
    else:
        login_or_logout = Markup(
            '<li><a href="{url_client_login}">Login</a> (Stub)</li>'
        ).format(url_client_login=helper_hooks.hooks["urls"]["url_client_login"])
    http.response.body = render(
        "Client",
        Markup(
            """
<p><a href="{url_home}">Home</a> &gt; Client</p>
<ul>
  {login_or_logout}
</ul>
"""
        ).format(
            url_home=helper_hooks.hooks["urls"]["url_home"],
            login_or_logout=login_or_logout,
        ),
    )
