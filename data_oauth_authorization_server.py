from pydantic import BaseModel


class ClientCredentials(BaseModel):
    client_secret: str
    scopes: list[str]


class CodePkce(BaseModel):
    redirect_uri: str
    scopes: list[str]


class CodePkceConsent(BaseModel):
    scopes: list[str] | None


class CodePkceRequest(BaseModel):
    client_id: str
    code_challenge: str
    scopes: list[str] | None
    state: str | None
    sub: str | None


# There is also a keys_current data structure which is just the kid, so doens't need a class
