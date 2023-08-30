from markupsafe import Markup

from render import render


def route_not_found(http):
    http.response.status = "404 Not Found"
    http.response.body = render(
        title="Not Found", body=Markup("<p>This page could not be found.</p>")
    )
