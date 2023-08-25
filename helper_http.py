import traceback

from pydantic import BaseModel

from helper_log import helper_log


class Request(BaseModel):
    path: str
    query: None | str
    headers: dict
    method: str
    body: None | bytes


class Response(BaseModel):
    status: str
    headers: dict
    body: None | bytes


class Http(BaseModel):
    request: Request
    response: Response


class RespondEarly(Exception):
    pass


# Runs for each HTTP request on a connection
def helper_http_handle(routes, method, path, query, request_headers, request_body=None):
    request = Request(
        path=path,
        query=query or None,
        headers=request_headers,
        method=method.lower(),
        body=request_body,
    )
    response = Response(status="200 OK", headers={}, body=None)
    http = Http(request=request, response=response)
    request_path = http.request.path
    if request_path == "/":
        request_path = ""

    try:
        route = routes.get(request_path)
        found = False
        if route:
            route(http)
            found = True
        if not found:
            candidates = []
            for path in routes:
                if path.endswith("/") and http.request.path.startswith(path):
                    candidates.append(path)
            if candidates:
                # Choose the longest matching candidate
                routes[sorted(candidates)[-1]](http)
                found = True
        # This should never happen because you can always add a route {..., "/": not_found, ...}
        if not found:
            http.response.status = "404 Not Found"
            http.response.body = b"404 Not Found"
    except RespondEarly:
        pass
    except Exception:
        # Keep whatever headers have been set (e.g. cookies), but show a 500
        http.response.status = "500 Error"
        http.response.body = b"500 Error"
        helper_log(__file__, "ERROR:", traceback.format_exc())
    return http
