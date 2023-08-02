import dbm
import json
from pydantic import BaseModel
import os


from config import oauth_authorization_server_store_session_dbpath


class SessionValue(BaseModel):
    code: str


def put_session_value(session: str, session_value: SessionValue):
    with dbm.open(oauth_authorization_server_store_session_dbpath, "c") as db:
        db[session.encode("utf8")] = json.dumps(dict(session_value)).encode("utf8")


def get_session_value(session: str):
    with dbm.open(oauth_authorization_server_store_session_dbpath, "c") as db:
        result = SessionValue(**json.loads(db[session.encode("utf8")].decode("utf8")))
    return result


if __name__ == "__main__":
    import helper_pkce

    put_session_value(
        "123",
        SessionValue(
            client_id="client_id",
            session_challenge=helper_pkce.session_challenge(
                helper_pkce.session_verifier()
            ),
        ),
    )
    print(get_and_delete_session_value("123"))
