import dbm
import json

from pydantic import BaseModel

from config_oauth_authorization_server import (
    config_oauth_authorization_server_code_pkce_consent_db_path,
)


class CodePkceConsent(BaseModel):
    scopes: list[str] | None


_db = None


def store_oauth_authorization_server_code_pkce_consent_init():
    global _db
    _db = dbm.open(config_oauth_authorization_server_code_pkce_consent_db_path, "c")


def store_oauth_authorization_server_code_pkce_consent_cleanup():
    _db.close()


def store_oauth_authorization_server_code_pkce_consent_put(
    sub: str, client_id: str, code_pkce_consent: CodePkceConsent
):
    _db[f"{sub} {client_id}".encode("utf8")] = json.dumps(
        dict(code_pkce_consent)
    ).encode("utf8")


def store_oauth_authorization_code_pkce_consent_get(sub: str, client_id: str):
    return CodePkceConsent(
        **json.loads(_db[f"{sub} {client_id}".encode("utf8")].decode("utf8"))
    )
