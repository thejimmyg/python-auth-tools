from data_oauth_authorization_server_refresh import RefreshTokenFamily
import kvstore.driver
import time

STORE = "oauth_authorization_server_refresh"


def store_oauth_authorization_server_refresh_get_refresh_token(refresh_token):
    return kvstore.driver.get(STORE, "token/" + refresh_token, consistent=True)


def store_oauth_authorization_server_refresh_get_refresh_token_family(family):
    values, ttl = kvstore.driver.get(STORE, "family/" + family, consistent=True)
    return RefreshTokenFamily(**values)


def store_oauth_authorization_server_refresh_put_refresh_token_family(
    family, client_id, sub, scopes, refresh_family_expires_in
):
    kvstore.driver.put(
        STORE,
        "family/" + family,
        RefreshTokenFamily(
            client_id=client_id, sub=sub, scopes_str=" ".join(scopes)
        ).dict(),
        ttl=time.time() + refresh_family_expires_in,
    )


def store_oauth_authorization_server_refresh_put_refresh_token(
    refresh_token, expires_in
):
    kvstore.driver.put(
        STORE,
        "token/" + refresh_token,
        ttl=time.time() + expires_in,
    )
