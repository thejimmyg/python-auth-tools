# Set up the clients needed:
# dynamodb = boto3....

import json

from pydantic import BaseModel

from helper_log import helper_log
from http_oauth_resource_owner import (
    http_oauth_resource_owner_verify_jwt_and_return_claims,
)


class Claims(BaseModel):
    claims: str


def claims(claims) -> Claims:
    return Claims(claims=json.dumps(claims))


apis = {"claims": [claims, ["read"]]}


def route_oauth_resource_owner_api_v1(http):
    claims_ = http_oauth_resource_owner_verify_jwt_and_return_claims(http)
    helper_log(__file__, "Claims:", claims_, type(claims_))
    api = "claims"
    scopes = claims_.get("scope", "").split(" ")
    for scope in apis[api][1]:
        assert scope in scopes, "Missing scope " + scope
    # XXX Use BaseModel in the serve for JSON?
    http.response.body = dict(apis[api][0](claims_))
