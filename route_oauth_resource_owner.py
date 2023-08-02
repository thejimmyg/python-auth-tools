from render_oauth_resource_owner import render_oauth_resource_owner_home
from config import url
import json


def oauth_resource_owner_home(http):
    http.response.body = render_oauth_resource_owner_home(title="Resource Owner Home")


def oauth_resource_owner_openapi(http):
    http.response.body = {
        "openapi": "3.0.1",
        "info": {
            "title": "Resource Owner",
            "description": "This is a sample API",
            "version": "0.1.0",
        },
        "tags": [],
        "paths": {
            "/api/v1": {
                "get": {
                    "operationId": "echo_claims",
                    "security": [{"token": []}],
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/TokenClaims"
                                    }
                                }
                            },
                        },
                        "400": {"$ref": "#/components/responses/400"},
                        "401": {"$ref": "#/components/responses/401"},
                        "403": {"$ref": "#/components/responses/403"},
                        "500": {"$ref": "#/components/responses/500"},
                    },
                }
            }
        },
        "components": {
            "securitySchemes": {
                "token": {
                    "description": "This API key is the OAuth2 ID token obtained from signing in. It identifies the specific user making a request. It is in the form of a JSON Web Token and is quite long. You should pass it as the value of the Authorization header in API requests.\n\nHere's an example:\n\n`Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c`",
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header",
                }
            },
            "responses": {
                "400": {
                    "description": "Usually because the JSON you sent failed validation but can be due to other invalid HTTP request such as malformed HTTP headers.",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/BadRequest"}
                        }
                    },
                },
                "401": {
                    "description": "No API key was sent in the Authorization header, or your token is invalid.",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Unauthorized"}
                        }
                    },
                },
                "403": {
                    "description": "Your token is missing from the Authorization header or is invalid.",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Forbidden"}
                        }
                    },
                },
                "404": {
                    "description": "Not found.",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/NotFound"}
                        }
                    },
                },
                "500": {
                    "description": "An unexpected error occurred.",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ServerError"}
                        }
                    },
                },
            },
            "schemas": {
                "Forbidden": {
                    "title": "The ID Token passed in the Authorization header does not have one of the necessary scopes to access this resource, or a subsequent permission check failed.",
                    "type": "object",
                    "required": ["message"],
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The 'Forbidden' string",
                            "example": "Forbidden",
                        }
                    },
                    "example": {"message": "Forbidden"},
                },
                "NotFound": {
                    "title": "Not Found",
                    "type": "object",
                    "required": ["message"],
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The 'Not Found' string",
                            "example": "Not Found",
                        }
                    },
                    "example": {"message": "Not Found"},
                },
                "Unauthorized": {
                    "title": "No ID Token found in the Authorization header",
                    "type": "object",
                    "required": ["message"],
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The 'Unauthorized' string",
                            "example": "Unauthorized",
                        }
                    },
                    "example": {"message": "Unauthorized"},
                },
                "ServerError": {
                    "title": "An error occurred",
                    "type": "object",
                    "required": ["message"],
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The 'Error' string",
                            "example": "Error",
                        },
                        "error": {
                            "type": "string",
                            "description": "A string explaining what went wrong",
                            "example": "The handler could not be found",
                        },
                    },
                    "example": {"message": "Error", "error": "An error occurred"},
                },
                "Success": {
                    "title": "The operation succeeded",
                    "type": "object",
                    "required": ["message"],
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The 'Success' string",
                            "example": "Success",
                        }
                    },
                    "example": {"message": "Success"},
                },
                "BadRequest": {
                    "title": "Your request body failed validation",
                    "type": "object",
                    "required": ["message"],
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The 'Bad Request' string",
                            "example": "Bad Request",
                        },
                        "errors": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "example": "missing 'id' property",
                            },
                            "description": "A list of the validation errors",
                            "example": ["missing 'id' property"],
                        },
                    },
                    "example": {
                        "message": "Bad Request",
                        "errors": ["missing 'id' property"],
                    },
                },
                "EmptyRequest": {
                    "description": "Empty",
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {},
                    "example": {},
                },
                "TokenClaims": {
                    "title": "The expected claims.",
                    "type": "object",
                    "required": ["claims"],
                    "properties": {
                        "claims": {
                            "type": "string",
                            "description": "A JSON-encoded string containing the token claims.",
                            "example": {
                                "claims": json.dumps(
                                    {
                                        "aud": "aud",
                                        "exp": 1690538896,
                                        "iat": 1690538296,
                                        "iss": url,
                                        "sub": "client",
                                    }
                                )
                            },
                        }
                    },
                },
            },
        },
    }
