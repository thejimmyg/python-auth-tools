from markupsafe import Markup

import helper_hooks
from helper_navigation import helper_navigation_generate_and_cache_breadcrumbs
from http_session import get_session_id_or_respond_early_not_logged_in
from render import render


def route_auth(http):
    get_session_id_or_respond_early_not_logged_in(http, "oauth")
    http.response.body = render(
        "Auth",
        Markup(
            """
{breadcrumbs}
<ul>
        <li><a href="{url_auth_logout}">Logout</a> (Stub)</li>
        <li><a href="{url_auth_session}">Session</a></li>
</ul
            """
        ).format(
            url_auth_logout=helper_hooks.hooks["urls"]["url_auth_logout"],
            url_auth_session=helper_hooks.hooks["urls"]["url_auth_session"],
            url_home=helper_hooks.hooks["urls"]["url_home"],
            breadcrumbs=helper_navigation_generate_and_cache_breadcrumbs(
                helper_hooks.hooks["urls"]["url_auth"]
            ),
        ),
    )


def route_auth_session(http):
    session_id = get_session_id_or_respond_early_not_logged_in(http, "oauth")
    http.response.body = render(
        title="Auth Session",
        body=Markup(
            """
            {breadcrumbs}
            <p>Here's the session ID:</p>
            <p><span id="session_id">{session_id}</span></p>
            """
        ).format(
            session_id=session_id,
            url_home=helper_hooks.hooks["urls"]["url_home"],
            url_auth=helper_hooks.hooks["urls"]["url_auth"],
            breadcrumbs=helper_navigation_generate_and_cache_breadcrumbs(
                helper_hooks.hooks["urls"]["url_auth_session"]
            ),
        ),
    )
