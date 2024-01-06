from route_oauth_resource_owner import (
    route_oauth_resource_owner_home,
    route_oauth_resource_owner_openapi,
)
from route_oauth_resource_owner_api import route_oauth_resource_owner_api_v1


def route_resourceowner(http):
    if http.request.path == "/resource-owner/api":
        return route_oauth_resource_owner_home(http)
    elif http.request.path == "/resource-owner/api/v1":
        return route_oauth_resource_owner_api_v1(http)
    elif http.request.path == "/resource-owner/api/openapi.json":
        return route_oauth_resource_owner_openapi(http)
    http.response.status = "404 Not Found"
    http.response.body = b"404 Not Found"
