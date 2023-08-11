import traceback

from helper_http import RespondEarly
from helper_log import log
from helper_oauth_resource_owner import verify_jwt


def verify_jwt_and_return_claims(http):
    try:
        auth = http.request.headers["authorization"]
        parts = auth.split(" ")
        if not auth or not parts[0].lower().strip() == "bearer":
            raise Exception("Not a bearer token")
        return verify_jwt(" ".join(parts[1:]).strip())
    except Exception as e:
        log(__file__, "Handling auth ERROR:", traceback.format_exc())
        http.response.status = "401 Not Authenticated"
        http.response.body = "401 Not Authenticated"
        raise RespondEarly(str(e))
