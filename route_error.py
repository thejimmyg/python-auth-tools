from markupsafe import Markup

from render import render


def route_error_not_found(http):
    http.response.status = "404 Not Found"
    http.response.body = render(
        title="Not Found", body=Markup("<p>This page could not be found.</p>")
    )


def route_error_not_logged_in(http):
    http.response.status = "401 Not Authenticated"
    http.response.body = render(
        title="Not Logged In", body=Markup("""<p>Not logged in.</p>""")
    )
