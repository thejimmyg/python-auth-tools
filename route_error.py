from render import Base, Html


def route_error_not_found(http):
    http.response.status = "404 Not Found"
    http.response.body = Base(
        title="Not Found", body=Html("<p>This page could not be found.</p>")
    )


def route_error_not_logged_in(http):
    http.response.status = "401 Not Authenticated"
    http.response.body = Base(
        title="Not Logged In", body=Html("""<p>Not logged in.</p>""")
    )
