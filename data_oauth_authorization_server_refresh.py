from pydantic import BaseModel


class RefreshTokenFamily(BaseModel):
    client_id: str
    sub: str
    scopes_str: str
