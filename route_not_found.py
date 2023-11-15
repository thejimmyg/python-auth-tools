from render import Base, Html


def route_not_found(http):
    http.response.status = "404 Not Found"
    http.response.body = Base(
        title="Not Found", body=Html("<p>This page could not be found.</p>")
    )
