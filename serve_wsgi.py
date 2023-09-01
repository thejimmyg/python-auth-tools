"""
python3 cli_serve_wsgi.py app_wsgi_hello

export URL=http://localhost:16001
curl "${URL}" -v
curl -X POST -d 'Some data' "${URL}" -v
"""


from helper_http import helper_http_handle
from helper_log import helper_log


def serve_wsgi(routes, debug=False):
    def serve_wsgi_application(environ, start_response):
        if debug:
            for key, value in environ.items():
                helper_log(__file__, f"{key}: {value}")
        method = environ["REQUEST_METHOD"].lower()
        path = environ["PATH_INFO"].lower()
        query = environ.get("QUERY_STRING", "")
        request_headers = {}
        for key in environ:
            if key.startswith("HTTP_"):
                request_header_name = key[5:].lower()
                if request_header_name in request_headers:
                    request_headers[request_header_name] += "; " + environ[key]
                else:
                    request_headers[request_header_name] = environ[key]
        request_body = None
        if "wsgi.input" in environ and environ.get("CONTENT_LENGTH"):
            request_body = environ["wsgi.input"].read(int(environ["CONTENT_LENGTH"]))
        http = helper_http_handle(
            routes, method, path, query, request_headers, request_body
        )
        response_headers = []
        for (
            response_header_name,
            response_header_value,
        ) in http.response.headers.items():
            response_headers.append((response_header_name, response_header_value))
        start_response(http.response.status, response_headers)
        return [http.response.body]

    return serve_wsgi_application
