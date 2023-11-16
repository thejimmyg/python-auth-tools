import traceback

from helper_log import helper_log


def make_app(routes):
    def app(http):
        request_path = http.request.path
        # assert request_path != '*' # Actually it can be * because this will just call the same thing as the * route anyway
        # if request_path == "/":
        #    request_path = ""

        try:
            route = routes.get(request_path)
            found = False
            if route:
                route(http)
                found = True
            if not found:
                candidates = []
                for path in routes:
                    if (
                        path != "/"
                        and path.endswith("/")
                        and http.request.path.startswith(path)
                    ):
                        candidates.append(path)
                if candidates:
                    # Choose the longest matching candidate
                    routes[sorted(candidates)[-1]](http)
                    found = True
            if not found:
                if "*" in routes:
                    routes["*"](http)
                else:
                    # This should never happen because you can always add a route {..., "*": not_found, ...}
                    http.response.status = "404 Not Found"
                    http.response.body = b"404 Not Found"
        except http.response.RespondEarly:
            pass
        except Exception:
            # Keep whatever headers have been set (e.g. cookies), but show a 500
            http.response.status = "500 Error"
            http.response.body = b"500 Error"
            helper_log(__file__, "ERROR:", traceback.format_exc())
        # _canonicalize_response(http)

    # def _canonicalize_response(http):
    #     response_body_changed = False
    #     auto_content_type: bytes = None
    #     if type(http.response.body) is str:
    #         http.response.body = http.response.body.encode("utf8")
    #         response_body_changed = True
    #         auto_content_type = "text/plain; charset=UTF8"
    #     elif type(http.response.body) is dict:
    #         http.response.body = json.dumps(http.response.body).encode("utf8")
    #         response_body_changed = True
    #         auto_content_type = "application/json; charset=UTF8"
    #     lower_response_headers = {}
    #     content_length_found = False
    #     content_type_found = False
    #     for k in http.response.headers:
    #         lower_k = k.lower()
    #         if lower_k in lower_response_headers:
    #             raise Exception(f"Duplicate key {lower_k} in response headers")
    #         lower_response_headers[lower_k] = http.response.headers[k]
    #         if lower_k == "content-length":
    #             # This can't happen since we are using a dictionary
    #             # if content_length_found is True:
    #             #     raise Exception(
    #             #         "Multiple content length headers in response"
    #             #     )
    #             content_length_found = True
    #         if response_body_changed and lower_k == "content-type":
    #             # if content_type_found is True:
    #             #    raise Exception(
    #             #        "Multiple content type headers in response"
    #             #    )
    #             content_type_found = True
    #     if response_body_changed and not content_type_found:
    #         lower_response_headers["content-type"] = auto_content_type
    #     if http.response.body and not content_length_found:
    #         lower_response_headers["content-length"] = str(len(http.response.body))
    #     http.response.headers = lower_response_headers
    return app


import helper_hooks

hook_module_path = "app_test"
helper_hooks.helper_hooks_setup(hook_module_path)

app = make_app(routes=helper_hooks.hooks["routes"])
