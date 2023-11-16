import time
import json

from data_session import Session
from driver_key_value_store import (
    driver_key_value_store_del,
    driver_key_value_store_get,
    driver_key_value_store_put,
)
from helper_pkce import helper_pkce_code_verifier

STORE = "session"


def store_session_put(session_id: str, session: Session):
    assert session_id
    if session.csrf is None:
        session.csrf = helper_pkce_code_verifier()
    values = session.dict()
    if "value" in values:
        values["value"] = json.dumps(values["value"])
    if "sub" in values and values["sub"] is None:
        del values["sub"]
    # Valid for 16 hours
    driver_key_value_store_put(
        STORE, session_id, values, ttl=time.time() + (16 * 60 * 60)
    )


def store_session_get(session_id: str):
    assert session_id
    values = driver_key_value_store_get(STORE, session_id)
    if "value" in values:
        values["value"] = json.loads(values["value"])
    if "sub" not in values:
        values["sub"] = None
    return Session(**values)


def store_session_destroy(session_id: str):
    assert session_id
    driver_key_value_store_del(STORE, session_id)


def store_session_set_sub(session_id: str, sub: str):
    assert session_id
    session = store_session_get(session_id)
    session.sub = sub
    store_session_put(session_id, session)
