"""
curl -H 'If-None-Match: bbe02f946d5455d74616fc9777557c22' -H "Authorization: Bearer $TOKEN" "${URL}/ok -v
curl -X POST -d '{}' "${URL}/static/file"
wrk -t 8 -d 10 -c 128 "${URL}/ok"



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

from gevent.server import StreamServer
from markupsafe import Markup

from helper_http import Http, Request, RespondEarly, Response
from helper_log import log


class BadRequest(Exception):
    pass


# Runs for each HTTP request on a connection
def handle(routes, method, path, query, request_headers, request_body=None):
    request = Request(
        path=path,
        query=query or None,
        headers=request_headers,
        method=method.lower(),
        body=request_body,
    )
    response = Response(status="200 OK", headers={}, body=None)
    http = Http(request=request, response=response)
    try:
        route = routes.get(http.request.path)
        found = False
        if route:
            route(http)
            found = True
        if not found:
            for path in routes:
                if http.request.path.startswith(path):
                    routes[path](http)
                    found = True
                    break
        if not found:
            http.response.status = "404 Not Found"
            http.response.body = b"404 Not Found"
    except RespondEarly:
        pass
    except Exception:
        # Keep whatever headers have been set (e.g. cookies), but show a 500
        http.response.status = "500 Error"
        http.response.body = b"500 Error"
        log(__file__, "ERROR:", traceback.format_exc())
    return http


# Runs for each incoming connection in a dedicated greenlet
def server(routes):
    def serve(socket, address):
        reader = socket.makefile(mode="rb")
        try:
            while True:
                line = reader.readline()
                if not line:
                    reader.close()
                    break
                try:
                    method, path, version = line.strip().split(b" ")
                except Exception as e:
                    raise BadRequest(str(e))
                query = None
                if b"?" in path:
                    parts = path.decode("ascii").split("?")
                    if len(parts) != 2:
                        raise BadRequest('Unescaped "?" character in query string')
                    path = parts[0]
                    query = parts[1]
                request_headers = {}
                while True:
                    line = reader.readline()
                    if line == b"\r\n":  # End of the request_headers
                        break
                    parts = line.decode("utf8").split(":")
                    if len(parts) < 2:
                        raise BadRequest(f"Invalid header: {line}")
                    header = parts[0].strip().lower()
                    if len(parts) > 2:
                        value = ":".join(parts[1:]).strip()
                    else:
                        value = parts[1].strip()
                    if header in request_headers:
                        request_headers[header] += "; " + value
                    else:
                        request_headers[header] = value
                request_body = None
                if "content-length" in request_headers:
                    request_body = reader.read(int(request_headers["content-length"]))
                http = handle(
                    routes, method, path, query, request_headers, request_body
                )
                response_body_changed = False
                auto_content_type: bytes = None
                if type(http.response.body) is Markup:
                    http.response.body = http.response.body.encode("utf8")
                    response_body_changed = True
                    auto_content_type = b"text/html; charset=UTF8"
                elif type(http.response.body) is str:
                    http.response.body = http.response.body.encode("utf8")
                    response_body_changed = True
                    auto_content_type = b"text/plain; charset=UTF8"
                elif type(http.response.body) is dict:
                    http.response.body = json.dumps(http.response.body).encode("utf8")
                    response_body_changed = True
                    auto_content_type = b"application/json; charset=UTF8"
                lower_response_headers = b""
                content_length_found = False
                content_type_found = False
                for k in http.response.headers:
                    lower_k = k.lower()
                    lower_response_headers += (
                        lower_k.encode("ascii")
                        + b": "
                        + (http.response.headers[k].encode("utf8"))
                        + b"\r\n"
                    )
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
                    lower_response_headers += (
                        b"content-type: " + auto_content_type + b"\r\n"
                    )

                if http.response.body and not content_length_found:
                    lower_response_headers += (
                        b"content-length: "
                        + (str(len(http.response.body)).encode("ascii"))
                        + b"\r\n"
                    )
                response = (
                    b"HTTP/1.1 "
                    + bytes(http.response.status, encoding="ascii")
                    + b"\r\n"
                    + lower_response_headers
                    + b"\r\n"
                    + bytes(http.response.body or b"")
                )
                socket.sendall(response)
                connection = request_headers.get("connection")
                if connection:
                    connection_lower = connection.lower()
                    if (
                        connection_lower == b"close"
                        or version == b"HTTP/1.0"
                        and connection_lower != "keep-alive"
                    ):
                        reader.close()
                        break
        except ConnectionResetError:
            # The connection is already closed, nothing to do
            pass
        except BadRequest as e:
            log(__file__, "Bad Request ERROR:", e)
            response = b"HTTP/1.1 400 Bad Request\r\nConnection: close\r\nContent-Length: 11\r\n\r\nBad Request"
            socket.sendall(response)
            reader.close()
        # https://stackoverflow.com/questions/7160983/catching-all-exceptions-in-python
        except Exception:
            log(__file__, "ERROR:", traceback.format_exc())
            response = b"HTTP/1.1 500 Error\r\nConnection: close\r\nContent-Length: 5\r\n\r\nError"
            socket.sendall(response)
            reader.close()
            raise

    return serve
