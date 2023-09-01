"""
curl -H 'If-None-Match: bbe02f946d5455d74616fc9777557c22' -H "Authorization: Bearer $TOKEN" "${URL}/ok -v
curl -X POST -d '{}' "${URL}/static/file"
wrk -t 8 -d 10 -c 128 "${URL}/ok"
"""

import traceback

from helper_http import helper_http_handle
from helper_log import helper_log


class BadRequest(Exception):
    pass


# Runs for each incoming connection in a dedicated greenlet
def serve_gevent(routes):
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
                http = helper_http_handle(
                    routes, method, path, query, request_headers, request_body
                )
                response_headers_bytes = b""
                for k, v in http.response.headers.items():
                    response_headers_bytes += (
                        k.encode("ascii") + b": " + v.encode("utf8") + b"\r\n"
                    )
                response = (
                    b"HTTP/1.1 "
                    + bytes(http.response.status, encoding="ascii")
                    + b"\r\n"
                    + response_headers_bytes
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
            helper_log(__file__, "Bad Request ERROR:", e)
            response = b"HTTP/1.1 400 Bad Request\r\nConnection: close\r\nContent-Length: 11\r\n\r\nBad Request"
            socket.sendall(response)
            reader.close()
        # https://stackoverflow.com/questions/7160983/catching-all-exceptions-in-python
        except Exception:
            helper_log(__file__, "ERROR:", traceback.format_exc())
            response = b"HTTP/1.1 500 Error\r\nConnection: close\r\nContent-Length: 5\r\n\r\nError"
            socket.sendall(response)
            reader.close()
            raise

    return serve
