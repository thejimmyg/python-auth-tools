import math
import urllib.parse
from datetime import datetime as dt

from jwcrypto import jwk, jwt

from config import config_url


#
# Sign
#


from store_oauth_authorization_server_key import (
    store_oauth_authorization_server_key_get_and_cache,
)

private_keys = {}


def helper_oauth_authorization_server_sign_jwt(
    client_id, sub, kid, expires_in=600, scopes=None
):
    if kid not in private_keys:
        private_keys[kid] = store_oauth_authorization_server_key_get_and_cache(kid)
    now = math.floor(dt.now().timestamp())
    jwt_claims = {
        "iss": config_url,
        "sub": sub,
        "aud": client_id,
        "iat": now,
        # 'nbf': now,
        "exp": now + expires_in,
        # 'jti': 'JWT ID'
    }
    if scopes:
        jwt_claims["scope"] = " ".join(scopes)
    jwt_header = {
        "alg": "RS256",
        "kid": kid,
    }
    jwt_token = jwt.JWT(
        header=jwt_header,
        claims=jwt_claims,
    )
    jwt_token.make_signed_token(jwk.JWK(**private_keys[kid]))
    signed_jwt = jwt_token.serialize()
    return signed_jwt


def helper_oauth_authorization_server_prepare_redirect_uri(
    code, code_pkce_request, redirect_uri
):
    url = redirect_uri + "?"
    if code_pkce_request.state:
        url += "state=" + urllib.parse.quote(code_pkce_request.state)
        url += "&code=" + urllib.parse.quote(code)
    else:
        url += "code=" + urllib.parse.quote(code)
    return url
