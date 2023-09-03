from pydantic import BaseModel


class CodeVerifier(BaseModel):
    code_verifier: str
