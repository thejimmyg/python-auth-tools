import base64
import json


def lambda_handler(event, context):
    try:
        import helper_hooks

        hook_module_path = "hooks"
        helper_hooks.helper_hooks_setup(hook_module_path)

        from helper_http import helper_http_handle

        routes = helper_hooks.hooks["routes"]

        method = event["requestContext"]["http"]["method"].lower()
        path = event["rawPath"]
        query = event["rawQueryString"]
        request_headers = event["headers"]
        request_body = None
        if event.get("body"):
            if event.get("isBase64Encoded"):
                request_body = base64.b64decode(event["body"])
            else:
                request_body = event["body"]
        http = helper_http_handle(
            routes, method, path, query, request_headers, request_body
        )
        return {
            "statusCode": int(http.response.status.split(" ")[0]),
            "headers": http.response.headers,
            "body": base64.b64encode(http.response.body),
            "isBase64Encoded": True,
        }
    except Exception as e:
        return {
            "statusCode": 200,
            "body": json.dumps([repr(event), repr(context), repr(e)]),
        }
