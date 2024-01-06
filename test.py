import json
import math
import os
import random
import subprocess
import threading
import time
import urllib.request

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from app.app import Home
from helper_oauth_resource_owner import helper_oauth_resource_owner_verify_jwt
from helper_pkce import helper_pkce_code_challenge, helper_pkce_code_verifier
from store_oauth_authorization_server_code_pkce_request import (
    CodePkceRequest,
    store_oauth_authorization_server_code_pkce_request_get_and_delete,
    store_oauth_authorization_server_code_pkce_request_put,
)
from store_session import Session, store_session_get, store_session_put

WIGGLE_ROOM = 2

from helper_navigation import (
    _crumbs_cache,
    _helper_navigation_generate_and_cache_breadcrumbs,
)


def test_navigation():
    url_home = "/"
    url_auth = url_home + "auth"
    url_client = url_home + "client"
    url_resource_owner_a = url_home + "resource-owner-a"
    url_resource_owner_b = url_home + "resource-owner-b"
    url_auth_session = url_auth + "/session"
    url_auth_logout = url_auth + "/logout"
    url_client_login = url_client + "/login"
    url_client_logout = url_client + "/logout"
    url_client_token = url_client + "/token"
    url_client + "/callback"
    url_resource_owner_a_api = url_resource_owner_a + "/api"
    url_resource_owner_b_api = url_resource_owner_b + "/api"
    url_resource_owner_a_api + "/read"
    url_resource_owner_b_api + "/write"

    navigation = {
        (url_home, "Home"): {
            (url_auth, "Auth"): {
                (url_auth_session, "Auth Session"): {},
                (url_auth_logout, "Auth Logout"): {},
            },
            (url_client, "Client"): {
                (url_client_login, "Client Login"): {},
                (url_client_token, "Client Token"): {},
                (url_client_logout, "Client Logout"): {},
            },
            (url_resource_owner_a, "Resource Owner A"): {
                (url_resource_owner_a_api, "Resource Owner A API"): {}
            },
            (url_resource_owner_b, "Resource Owner B"): {
                (url_resource_owner_b_api, "Resource Owner B API"): {}
            },
        }
    }

    home_crumbs = _helper_navigation_generate_and_cache_breadcrumbs(
        url_home, navigation
    )
    assert home_crumbs == [("/", "Home")], home_crumbs
    auth_crumbs = _helper_navigation_generate_and_cache_breadcrumbs(
        url_auth, navigation
    )
    assert auth_crumbs == [("/", "Home"), ("/auth", "Auth")], auth_crumbs
    auth_session_crumbs = _helper_navigation_generate_and_cache_breadcrumbs(
        url_auth_session, navigation
    )
    assert auth_session_crumbs == [
        ("/", "Home"),
        ("/auth", "Auth"),
        ("/auth/session", "Auth Session"),
    ], auth_session_crumbs
    client_logout_crumbs = _helper_navigation_generate_and_cache_breadcrumbs(
        url_client_logout, navigation
    )
    assert client_logout_crumbs == [
        ("/", "Home"),
        ("/client", "Client"),
        ("/client/logout", "Client Logout"),
    ], client_logout_crumbs
    client_logout_crumbs2 = _helper_navigation_generate_and_cache_breadcrumbs(
        url_client_logout, navigation
    )
    assert client_logout_crumbs2 == client_logout_crumbs
    assert len(_crumbs_cache) == 4, len(_cache)


def test_store():
    # store_oauth_authorization_server_code_pkce_request
    code_challenge = helper_pkce_code_challenge(helper_pkce_code_verifier())
    store_oauth_authorization_server_code_pkce_request_put(
        "123",
        CodePkceRequest(
            client_id="client_id",
            code_challenge=code_challenge,
        ),
    )
    v = store_oauth_authorization_server_code_pkce_request_get_and_delete("123")
    assert v == CodePkceRequest(
        client_id="client_id",
        code_challenge=code_challenge,
        scopes=None,
        state=None,
        sub=None,
    ), v

    # store_session
    code = helper_pkce_code_challenge(helper_pkce_code_verifier())
    store_session_put(
        "123",
        Session(value=dict(code=code)),
    )
    v = store_session_get("123")
    assert v.value == dict(code=code)
    assert v.csrf is not None
    assert v.sub is None

    # store_oauth_code_pkce_code_verifier
    # XXX


def test_render():
    actual = Home(title="OAuth Client Home").render()
    expected = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>OAuth Client Home</title>
    <link rel="stylesheet" href="/style.css">
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
  </head>
  <body>
    <main>
      <h1>OAuth Client Home</h1>
      <p>
        <a href="/oauth-code-pkce/login">Login without scopes</a>,
        <a href="/oauth-code-pkce/login?scope=read">login with read scope</a>,
        <a href="/oauth-code-pkce/login?scope=read%20offline_access">login with read and offline access scopes</a>,
        <a href="/oauth-code-pkce/login?scope=no-such-scope">login with an invalid scope</a>,
        <a href="/saml2/login/">login with SAML</a>.
      </p>
    </main>
    <script src="/script.js"></script>
  </body>
</html>"""
    if actual != expected:
        actual_lines = actual.split("\n")
        for i, line in enumerate(expected.split("\n")):
            if line != actual_lines[i]:
                print("-", line)
                print("+", actual_lines[i])
        raise AssertionError("Unexpected result of rendering Home")


def _login_as(driver, test_sub):
    assert "Login" in driver.page_source
    elem = driver.find_element(By.NAME, "sub")
    elem.clear()
    elem.send_keys(test_sub)
    elem.send_keys(Keys.RETURN)


def _check_jwt(now, url, test_sub):
    elem = driver.find_element(By.ID, "jwt")
    jwt = elem.text
    claims = helper_oauth_resource_owner_verify_jwt(jwt)
    assert claims["aud"] == "client"
    assert claims["exp"] > now and claims["exp"] <= now + 600 + WIGGLE_ROOM
    assert claims["iat"] >= now and claims["iat"] <= now + WIGGLE_ROOM, (
        claims["iat"],
        now,
        now + WIGGLE_ROOM,
    )
    assert claims["iss"] == url
    assert claims["sub"] == test_sub
    return jwt, claims


def _check_refresh():
    elem = driver.find_element(By.ID, "refresh")
    return elem.text


def oauth_code_pkce_browser(driver, url):
    print()
    print("Browser test code pkce", url)
    driver.get(url + "/")
    assert "OAuth Client Home" in driver.title
    elem = driver.find_element(By.LINK_TEXT, "Login without scopes")
    elem.click()

    now = math.floor(time.time())  # Round down
    test_sub = "test_sub_{}".format(now)
    _login_as(driver, test_sub)

    jwt, claims = _check_jwt(now, url, test_sub)
    assert "scope" not in claims
    return jwt, claims, test_sub


def oauth_code_pkce_browser_read_scope(driver, url):
    print()
    print("Browser test code pkce read scope", url)
    driver.get(url + "/")
    assert "OAuth Client Home" in driver.title
    elem = driver.find_element(By.LINK_TEXT, "login with read scope")
    elem.click()

    now = math.floor(time.time())  # Round down
    test_sub = "test_sub_{}".format(now)
    _login_as(driver, test_sub)

    elem = driver.find_element(By.ID, "consent-msg")
    assert (
        elem.text
        == "The page at {url}/oauth-code-pkce/callback is asking for the following permissions to your data:".format(
            url=url
        )
    ), elem.text
    elem = driver.find_element(By.NAME, "approve")
    elem.click()
    return _check_jwt(now, url, test_sub)


def oauth_code_pkce_browser_read_and_offline_access_scopes(driver, url):
    print()
    print("Browser test code pkce read and offline access scopes", url)
    driver.get(url + "/")
    assert "OAuth Client Home" in driver.title
    elem = driver.find_element(
        By.LINK_TEXT, "login with read and offline access scopes"
    )
    elem.click()

    now = math.floor(time.time())  # Round down
    test_sub = "test_sub_{}".format(now)
    _login_as(driver, test_sub)

    elem = driver.find_element(By.ID, "consent-msg")
    assert (
        elem.text
        == "The page at {url}/oauth-code-pkce/callback is asking for the following permissions to your data:".format(
            url=url
        )
    ), elem.text
    elem = driver.find_element(By.NAME, "approve")
    elem.click()
    refresh = _check_refresh()
    jwt, claims = _check_jwt(now, url, test_sub)
    return jwt, claims, test_sub, refresh


def oauth_code_pkce_browser_already_logged_in(driver, url, test_sub):
    print()
    print("Browser test code pkce when already logged in", url)
    now = math.floor(time.time())  # Round down
    driver.get(url + "/")
    assert "OAuth Client Home" in driver.title
    elem = driver.find_element(By.LINK_TEXT, "Login without scopes")
    elem.click()
    return _check_jwt(now, url, test_sub)


def oauth_code_pkce_browser_already_logged_in_read_scope(driver, url, test_sub):
    print()
    print("Browser test code pkce when already logged in read scope", url)
    now = math.floor(time.time())  # Round down
    driver.get(url + "/")
    assert "OAuth Client Home" in driver.title
    elem = driver.find_element(By.LINK_TEXT, "login with read scope")
    elem.click()

    now = math.floor(time.time())  # Round down
    "test_sub_{}".format(now)

    elem = driver.find_element(By.ID, "consent-msg")
    assert (
        elem.text
        == "The page at {url}/oauth-code-pkce/callback is asking for the following permissions to your data:".format(
            url=url
        )
    ), elem.text
    elem = driver.find_element(By.NAME, "approve")
    elem.click()
    return _check_jwt(now, url, test_sub)


def oauth_code_pkce_browser_invalid_scope(driver, url):
    print()
    print("Browser test code pkce invalid scope", url)
    now = math.floor(time.time())  # Round down
    driver.get(url + "/")
    assert "OAuth Client Home" in driver.title
    elem = driver.find_element(By.LINK_TEXT, "login with an invalid scope")
    elem.click()
    # Obviously we'd like to do better in future, perhaps by calling back with an invalid scope message in the JSON
    assert (
        driver.find_element(By.TAG_NAME, "body").text
        == "A server error occurred.  Please contact the administrator."
    ), driver.find_element(By.TAG_NAME, "body").text


def saml_sp_flow(driver, url):
    print()
    print("SAML SP flow")
    driver.get(url + "/")
    assert "OAuth Client Home" in driver.title
    elem = driver.find_element(By.LINK_TEXT, "login with SAML")
    elem.click()
    assert "IdP User" in driver.page_source
    for elem_id, value in [
        ("issuer", "oktadev/test/sample-sp"),
        ("acs", url + "/saml2/acs/"),
        ("audience", url + "/sample_sp"),
        ("login", "james@example.com"),
        ("firstName", "Firstname"),
        ("lastName", "Lastname"),
        ("email", "james@example.com"),
    ]:
        elem = driver.find_element(By.ID, elem_id)
        elem.clear()
        elem.send_keys(value)
    elem = driver.find_element(By.TAG_NAME, "button").click()
    print(driver.current_url)
    elem = driver.find_element(By.ID, "session_info")
    session_info = json.loads(elem.text)
    print(session_info)
    # {'ava': {'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress': ['james@example.com'], 'Email': ['james@example.com'], 'FirstName': ['Firstname'], 'LastName': ['Lastname']}, 'name_id': '<ns0:NameID xmlns:ns0="urn:oasis:names:tc:SAML:2.0:assertion" Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified">james@example.com</ns0:NameID>', 'came_from': None, 'issuer': 'oktadev/test/sample-sp', 'not_on_or_after': 1690903855, 'authn_info': [('urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified', [], '2023-08-01T14:30:55.899Z')], 'session_index': None}
    session_info["ava"]["urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"] = [
        "james@example.com"
    ]
    session_info["ava"]["Email"] = ["james@example.com"]
    session_info["ava"]["FirstName"] = ["Firstname"]
    session_info["ava"]["LastName"] = ["Lastname"]
    # }, 'name_id': '<ns0:NameID xmlns:ns0="urn:oasis:names:tc:SAML:2.0:assertion" Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified">james@example.com</ns0:NameID>', 'came_from': None, 'issuer': 'oktadev/test/sample-sp', 'not_on_or_after': 1690903883, 'authn_info': [('urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified', [], '2023-08-01T14:31:23.512Z')], 'session_index': None}


def make_authenticated_request_to_oauth_resource_owner(url, token, expect_sub=True):
    # curl -H "Authorization: Bearer $TOKEN" -v http://localhost:16001/resource-owner/api/v1
    print(url + "/resource-owner/api/v1")
    request = urllib.request.Request(
        url + "/resource-owner/api/v1",
        headers={"Authorization": "Bearer " + token},
    )
    with urllib.request.urlopen(request) as fp:
        response = json.loads(fp.read())
        print(response)
        assert list(response.keys()) == ["claims"], response.keys()
        # This doesn't match because iat and exp will be different.
        # assert json.dumps(response) == json.dumps({'claims': '{"aud": "client", "exp": 1690967312, "iat": 1690966712, "iss": "http://localhost:16001", "scope": "read offline_access", "sub": "sub"}'})
        claims = json.loads(response["claims"])
        assert claims["aud"] == "client"
        assert claims["iss"] == url
        assert claims["scope"] == "read offline_access", claims["scope"]
        if expect_sub:
            assert claims["sub"] == "sub"


def make_unauthenticated_request_to_oauth_resource_owner(url, token):
    print(url + "/resource-owner/api/v1")
    request = urllib.request.Request(
        url + "/resource-owner/api/v1",
        headers={"Authorization": "Bearer " + token + "invalid"},
    )
    try:
        with urllib.request.urlopen(request) as fp:
            json.loads(fp.read())
    except urllib.error.HTTPError as e:
        error = e.read().decode("utf8")
        print(e, error)
        assert error == "401 Not Authenticated", error
    else:
        raise Exception(
            "Fetching OAuth Resource Owner API did not raise when using an invalid token"
        )


def exec_cli_oauth_authorization_server_code_pkce_put(env, url):
    print()
    print("OAuth authorization server put code pkce")
    process = subprocess.Popen(
        [
            "python3",
            "cli_oauth_authorization_server_code_pkce_put.py",
            "client",
            url + "/oauth-code-pkce/callback",
            "read offline_access",
        ],
        env=env,
    )
    assert process.wait() == 0


def exec_cli_oauth_authorization_server_client_credentials_put(env):
    print()
    print("OAuth authorization server put client credentials")
    process = subprocess.Popen(
        [
            "python3",
            "cli_oauth_authorization_server_client_credentials_put.py",
            "client",
            "secret",
            "read offline_access",
        ],
        env=env,
    )
    assert process.wait() == 0


def exec_cli_oauth_authorization_server_keys_generate(env, kid):
    print()
    print("OAuth authorization server generate keys")
    process = subprocess.Popen(
        [
            "python3",
            "cli_oauth_authorization_server_keys_generate.py",
            kid,
        ],
        env=env,
    )
    assert process.wait() == 0


def exec_cli_oauth_authorization_server_keys_current_set(env, kid):
    print()
    print("OAuth authorization server set current key")
    process = subprocess.Popen(
        [
            "python3",
            "cli_oauth_authorization_server_keys_current_set.py",
            kid,
        ],
        env=env,
    )
    assert process.wait() == 0


def exec_cli_webhook_provider_keys_generate(env, kid):
    print()
    print("Webhook provider generate keys")
    process = subprocess.Popen(
        ["python3", "cli_webhook_provider_keys_generate.py", kid], env=env
    )
    assert process.wait() == 0


def exec_cli_webhook_provider_keys_current_set(env, kid):
    print()
    print("Webhook provider set current key")
    process = subprocess.Popen(
        ["python3", "cli_webhook_provider_keys_current_set.py", kid],
        env=env,
    )
    assert process.wait() == 0


def exec_cli_webhook_provider_sign_jwt(env, payload, kid):
    print()
    print("Webhook provider sign JWT")
    process = subprocess.Popen(
        ["python3", "cli_webhook_provider_sign_jwt.py", payload, kid],
        stdout=subprocess.PIPE,
        env=env,
    )
    (stdout, _) = process.communicate()
    assert process.wait() == 0
    print(stdout)
    sig = stdout.decode("utf8").strip()
    return sig


def exec_cli_webhook_consumer_verify_jwt(env, sig, body, jwks_url):
    print()
    print("Webhook consumer verify JWT", sig, body, jwks_url)
    process = subprocess.Popen(
        [
            "python3",
            "cli_webhook_consumer_verify_jwt.py",
            sig,
            body,
            jwks_url,
        ],
        stdout=subprocess.PIPE,
        env=env,
    )
    (stdout, _) = process.communicate()
    assert process.wait() == 0
    print(stdout)


def exec_cli_oauth_authorization_server_sign_jwt(env, kid):
    print()
    print("OAuth authorization server sign JWT")
    process = subprocess.Popen(
        [
            "python3",
            "cli_oauth_authorization_server_sign_jwt.py",
            "client",
            "sub",
            "read offline_access",
            kid,
        ],
        stdout=subprocess.PIPE,
        env=env,
    )
    (stdout, _) = process.communicate()
    assert process.wait() == 0
    print(stdout)
    token = stdout.decode("utf8").strip()
    return token


def exec_cli_oauth_client_credentials(env, client, secret, scopes):
    print()
    print("OAuth client credentials")
    process = subprocess.Popen(
        [
            "python3",
            "cli_oauth_client_credentials.py",
            client,
            secret,
            " ".join(scopes),
        ],
        stdout=subprocess.PIPE,
        env=env,
    )
    (stdout, _) = process.communicate()
    assert process.wait() == 0
    print(stdout)
    response = json.loads(stdout.decode("utf8").strip())
    # https://www.rfc-editor.org/rfc/rfc6749#section-4.4.3 Should not include a refresh token even though we passed the offline_access scope
    assert sorted(list(response.keys())) == ["access_token", "expires_in", "token_type"]
    assert response["expires_in"] == 600
    assert response["token_type"] == "bearer"
    helper_oauth_resource_owner_verify_jwt(response["access_token"])
    return response["access_token"]


def exec_cli_oauth_resource_owner_verify_jwt(env, token):
    print()
    print("OAuth resource owner verify JWT", token)
    process = subprocess.Popen(
        ["python3", "cli_oauth_resource_owner_verify_jwt.py", token],
        stdout=subprocess.PIPE,
        env=env,
    )
    (stdout, _) = process.communicate()
    assert process.wait() == 0
    print(stdout)


if __name__ == "__main__":
    # Unit tests
    test_navigation()
    test_render()
    test_store()

    # End to end
    port = 49152 + math.floor((65535 - 49152) * random.random())
    url = "http://localhost:" + str(port)
    store_dir = os.path.join("test", str(port), "store")
    print(url)
    os.makedirs(store_dir, exist_ok=True)
    tmp_dir = os.path.join("test", str(port), "tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    os.makedirs(os.path.join(store_dir, "oauth_authorization_server"), exist_ok=True)
    env = {
        "PYTHONPATH": os.getcwd(),
        "PATH": os.environ["PATH"],
        "URL": url,
        "STORE_DIR": store_dir,
        "TMP_DIR": tmp_dir,
    }
    if os.environ.get("SAML_SP_SLACK_SECONDS"):
        env["SAML_SP_SLACK_SECONDS"] = os.environ["SAML_SP_SLACK_SECONDS"]

    exec_cli_oauth_authorization_server_code_pkce_put(env, url)
    exec_cli_oauth_authorization_server_client_credentials_put(env)

    kid = "testoa"
    # exec_cli_oauth_authorization_server_keys_generate(env, "before")
    exec_cli_oauth_authorization_server_keys_generate(env, kid)
    exec_cli_oauth_authorization_server_keys_current_set(env, kid)
    # exec_cli_oauth_authorization_server_keys_generate(env, "zafter")

    oauth_code_pkce_token = exec_cli_oauth_authorization_server_sign_jwt(env, kid)

    webhook_provider_kid = "testw"
    exec_cli_webhook_provider_keys_generate(env, "beforew")
    exec_cli_webhook_provider_keys_generate(env, webhook_provider_kid)
    exec_cli_webhook_provider_keys_generate(env, "zafterw")
    exec_cli_webhook_provider_keys_current_set(env, webhook_provider_kid)
    body = json.dumps({"hello": "world"})
    sig = exec_cli_webhook_provider_sign_jwt(env, body, webhook_provider_kid)

    log_path = os.path.join(tmp_dir, "server.log")
    p = None

    def start_server():
        global p
        print()
        print("===>", url, "logging to", log_path)
        print()
        log = open(log_path, "wb")
        p = subprocess.Popen(
            # Have to run Python in unbuffered mode (-u) to get the logs streaming to the log files
            [
                "python3",
                "-u",
                "serve/adapter/wsgi/bin/serve_wsgi.py",
                "app.app:app",
                "localhost:" + str(port),
            ],
            env=env,
            stdout=log,
            stderr=log,
        )

    server_thread = threading.Thread(target=start_server, args=())
    server_thread.start()
    # Not ideal, but we need to wait for the server to start
    time.sleep(4)

    exec_cli_oauth_resource_owner_verify_jwt(env, oauth_code_pkce_token)
    make_authenticated_request_to_oauth_resource_owner(url, oauth_code_pkce_token)
    make_unauthenticated_request_to_oauth_resource_owner(url, oauth_code_pkce_token)
    # {
    #   "aud": "client",
    #   "exp": 1691075255,
    #   "iat": 1691074655,
    #   "iss": "http://localhost:61022",
    #   "scope": "read offline_access",
    #   "sub": "sub"
    # }
    oauth_client_credentials_token = exec_cli_oauth_client_credentials(
        env, "client", "secret", ["read", "offline_access"]
    )
    exec_cli_oauth_resource_owner_verify_jwt(env, oauth_client_credentials_token)
    try:
        exec_cli_oauth_resource_owner_verify_jwt(
            env, oauth_client_credentials_token + "1"
        )
    except:
        pass
    else:
        raise Exception("Invalid signature failed to raise an exception")

    make_authenticated_request_to_oauth_resource_owner(
        url, oauth_client_credentials_token, expect_sub=False
    )
    make_unauthenticated_request_to_oauth_resource_owner(
        url, oauth_client_credentials_token
    )
    # {
    #   "aud": "client",
    #   "exp": 1691075259,
    #   "iat": 1691074659,
    #   "iss": "http://localhost:61022",
    #   "sub": "client"
    # }

    exec_cli_webhook_consumer_verify_jwt(
        env, sig, body, jwks_url=url + "/.well-known/webhook-provider-jwks.json"
    )
    try:
        exec_cli_webhook_consumer_verify_jwt(
            env,
            sig + "1",
            body,
            jwks_url=url + "/.well-known/webhook-provider-jwks.json",
        )
    except:
        pass
    else:
        raise Exception("Invalid signature failed to raise an exception")

    # Refresh token
    driver = webdriver.Chrome()
    (
        jwt,
        claims,
        test_sub,
        refresh,
    ) = oauth_code_pkce_browser_read_and_offline_access_scopes(driver, url)
    print(jwt, claims, test_sub, refresh)
    assert (
        "." in refresh
        and len(refresh.split(".")[1]) == 64  # Current
        and len(refresh.split(".")[0]) == 63  # Family
    ), refresh
    driver.close()

    print(jwt, refresh)

    # Check we can issue a new access token and refresh token
    def grant_refresh_token(refresh_token):
        request = urllib.request.Request(
            url + "/oauth/token",
            method="POST",
            data=urllib.parse.urlencode(
                {"grant_type": "refresh_token", "refresh_token": refresh_token}
            ).encode("UTF-8"),
        )
        with urllib.request.urlopen(request) as fp:
            response = json.loads(fp.read())
            print(response)
        return response

    jwt_claims = helper_oauth_resource_owner_verify_jwt(jwt)
    print(jwt_claims)
    assert jwt_claims["aud"] == "client", jwt_claims
    assert jwt_claims["iss"] == url, (jwt_claims, url)

    # Need to wait 1 second for the issued token to be different (iat and exp will be different)
    time.sleep(1.1)
    response1 = grant_refresh_token(refresh)
    assert list(sorted(response1.keys())) == [
        "access_token",
        "expires_in",
        "refresh_token",
        "token_type",
    ], response1
    assert response1["expires_in"] == 600, response1["expires_in"]
    # https://datatracker.ietf.org/doc/html/rfc6749#section-7.1
    assert response1["token_type"] == "bearer", response1["token_type"]
    assert response1["refresh_token"].split(".")[0] == refresh.split(".")[0], (
        refresh,
        response1,
    )
    assert response1["refresh_token"].split(".")[1] != refresh.split(".")[1], (
        refresh,
        response1,
    )
    assert response1["access_token"] != jwt, (response1["access_token"], jwt)
    claims1 = helper_oauth_resource_owner_verify_jwt(response1["access_token"])
    print(claims1)
    # {'aud': 'client', 'exp': 1701626091, 'iat': 1701625491, 'iss': 'http://localhost:58326', 'scope': 'read offline_access', 'sub': 'test_sub_1701625490'}

    assert claims1["scope"] == jwt_claims["scope"], claims1
    assert claims1["aud"] == jwt_claims["aud"], claims1
    assert claims1["iss"] == jwt_claims["iss"], claims1
    assert claims1["sub"] == jwt_claims["sub"], claims1
    assert claims1["exp"] > jwt_claims["iat"], claims1
    assert claims1["exp"] > jwt_claims["exp"], claims1

    # Need to wait 1 second for the issued token to be different (iat and exp will be different)
    time.sleep(1.1)
    response2 = grant_refresh_token(response1["refresh_token"])
    assert list(sorted(response2.keys())) == [
        "access_token",
        "expires_in",
        "refresh_token",
        "token_type",
    ], response2
    assert response2["expires_in"] == 600, response2["expires_in"]
    assert response2["token_type"] == "bearer", response2["token_type"]
    assert response2["refresh_token"].split(".")[0] == refresh.split(".")[0], (
        refresh,
        response2,
    )
    assert (
        response2["refresh_token"].split(".")[1]
        != response1["refresh_token"].split(".")[1]
    ), (
        response1["refresh_token"],
        response2,
    )
    assert response2["refresh_token"].split(".")[1] != refresh.split(".")[1], (
        refresh,
        response2,
    )
    assert response2["access_token"] != jwt, (response2["access_token"], jwt)
    assert response2["access_token"] != response1["access_token"], (
        response2["access_token"],
        response1["access_token"],
    )
    claims2 = helper_oauth_resource_owner_verify_jwt(response2["access_token"])
    assert claims2["scope"] == jwt_claims["scope"], claims2
    assert claims2["aud"] == jwt_claims["aud"], claims2
    assert claims2["iss"] == jwt_claims["iss"], claims2
    assert claims2["sub"] == jwt_claims["sub"], claims2
    assert claims2["exp"] > claims1["exp"], (claims2, claims1)
    assert claims2["iat"] > claims1["iat"], (claims2, claims1)

    driver = webdriver.Chrome()
    browser_jwt, browser_claims, test_sub = oauth_code_pkce_browser(driver, url)
    saml_sp_flow(driver, url)
    (
        browser_jwt_already_logged_in,
        browser_claims_already_logged_in,
    ) = oauth_code_pkce_browser_already_logged_in(driver, url, test_sub)
    assert browser_jwt != browser_jwt_already_logged_in
    assert browser_claims["sub"] == browser_claims_already_logged_in["sub"]
    assert browser_claims["exp"] < browser_claims_already_logged_in["exp"]
    assert "scope" not in browser_claims
    assert "scope" not in browser_claims_already_logged_in
    oauth_code_pkce_browser_already_logged_in_read_scope(driver, url, test_sub)
    driver.close()

    driver = webdriver.Chrome()
    oauth_code_pkce_browser_invalid_scope(driver, url)
    oauth_code_pkce_browser_read_scope(driver, url)
    driver.close()

    p.kill()
    server_thread.join()
    print("SUCCESS! Server logs in:", log_path)
