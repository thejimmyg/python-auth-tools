from pydantic import BaseModel


class Request(BaseModel):
    path: str
    query: None | str
    headers: dict
    method: str
    body: None | bytes


class Response(BaseModel):
    status: str
    headers: dict
    body: None | bytes


class Http(BaseModel):
    request: Request
    response: Response


class RespondEarly(Exception):
    pass
