import base64
import hashlib
import secrets


def helper_pkce_code_verifier():
    # https://docs.python.org/3/library/secrets.html#secrets.token_urlsafe
    # This means we aren't using the allowed '.' or '~' keys, but our pkce token is long
    code_verifier = secrets.token_urlsafe(96)[:128]
    assert len(code_verifier) == 128, "Code verifier too short"
    return code_verifier


def helper_pkce_code_challenge(code_verifier):
    hashed = hashlib.sha256(code_verifier.encode("ascii")).digest()
    encoded = base64.urlsafe_b64encode(hashed)
    # Needs to be 43 characters
    code_challenge = encoded.decode("ascii")[:43]
    assert len(code_challenge) == 43, (
        "Code challenge not 43 characters:" + code_challenge
    )
    return code_challenge
