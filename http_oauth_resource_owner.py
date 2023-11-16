import traceback

from helper_log import helper_log
from helper_oauth_resource_owner import helper_oauth_resource_owner_verify_jwt


def http_oauth_resource_owner_verify_jwt_and_return_claims(http):
    try:
        auth = http.request.headers["authorization"]
        parts = auth.split(" ")
        if not auth or not parts[0].lower().strip() == "bearer":
            raise Exception("Not a bearer token")
        return helper_oauth_resource_owner_verify_jwt(" ".join(parts[1:]).strip())
    except Exception as e:
        helper_log(__file__, "Handling auth ERROR:", traceback.format_exc())
        http.response.status = "401 Not Authenticated"
        http.response.body = "401 Not Authenticated"
        raise http.response.RespondEarly(str(e))
