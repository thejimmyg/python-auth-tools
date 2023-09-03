from pydantic import BaseModel


class Session(BaseModel):
    value: dict
    sub: str | None
    csrf: str | None
