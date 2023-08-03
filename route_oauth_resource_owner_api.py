# Set up the clients needed:
# dynamodb = boto3....

import json
import traceback

from pydantic import BaseModel

from helper_crypto import verify_jwt
from helper_http import RespondEarly
from helper_log import log


class Claims(BaseModel):
    claims: str


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


def claims(claims) -> Claims:
    return Claims(claims=json.dumps(claims))


apis = {"claims": [claims, ["read"]]}


def v1(http):
    claims_ = verify_jwt_and_return_claims(http)
    log(__file__, "Claims:", claims_, type(claims_))
    api = "claims"
    scopes = claims_.get("scope", "").split(" ")
    for scope in apis[api][1]:
        assert scope in scopes, "Missing scope " + scope
    # XXX Use BaseModel in the serve for JSON?
    http.response.body = dict(apis[api][0](claims_))
