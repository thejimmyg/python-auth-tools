"""
We can keep this simple by making some assumptions:

* The whole request and response can fit in memory and we don't want any HTTP streaming features

This module does a few things for us:

* Add a content length if it is missing
* Convert headers to bytes, using ascii for keys, and UTF-8 for values
* Encode the body as UTF8 if it is returned as a string or Markup object
* JSON encode the body as UTF8 if it is a dict
* If the body is changed and the Content-Type is missing, set it
"""

import json
import traceback
import uuid

from markupsafe import Markup
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
    context: dict


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
    http = Http(request=request, response=response, context=dict(uid=uuid.uuid4()))
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
    _canonicalize_response(http)
    return http


def _canonicalize_response(http):
    response_body_changed = False
    auto_content_type: bytes = None
    if type(http.response.body) is Markup:
        http.response.body = http.response.body.encode("utf8")
        response_body_changed = True
        auto_content_type = "text/html; charset=UTF8"
    elif type(http.response.body) is str:
        http.response.body = http.response.body.encode("utf8")
        response_body_changed = True
        auto_content_type = "text/plain; charset=UTF8"
    elif type(http.response.body) is dict:
        http.response.body = json.dumps(http.response.body).encode("utf8")
        response_body_changed = True
        auto_content_type = "application/json; charset=UTF8"
    lower_response_headers = {}
    content_length_found = False
    content_type_found = False
    for k in http.response.headers:
        lower_k = k.lower()
        if lower_k in lower_response_headers:
            raise Exception(f"Duplicate key {lower_k} in response headers")
        lower_response_headers[lower_k] = http.response.headers[k]
        if lower_k == "content-length":
            # This can't happen since we are using a dictionary
            # if content_length_found is True:
            #     raise Exception(
            #         "Multiple content length headers in response"
            #     )
            content_length_found = True
        if response_body_changed and lower_k == "content-type":
            # if content_type_found is True:
            #    raise Exception(
            #        "Multiple content type headers in response"
            #    )
            content_type_found = True
    if response_body_changed and not content_type_found:
        lower_response_headers["content-type"] = auto_content_type
    if http.response.body and not content_length_found:
        lower_response_headers["content-length"] = str(len(http.response.body))
    http.response.headers = lower_response_headers
