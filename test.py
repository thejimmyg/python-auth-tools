import json
import math
import os
import random
import subprocess
import sys
import threading
import time
import urllib.request

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import helper_hooks
from app_test import render_home
from driver_key_value_store_sqlite import (
    driver_key_value_store_sqlite_del,
    driver_key_value_store_sqlite_get,
    driver_key_value_store_sqlite_put,
)
from helper_log import helper_log
from helper_oauth_resource_owner import helper_oauth_resource_owner_verify_jwt
from helper_pkce import helper_pkce_code_challenge, helper_pkce_code_verifier
from render import render
from render_oauth_resource_owner import render_oauth_resource_owner_home
from render_saml_sp import render_saml_sp_success
from store_oauth_authorization_server_code_pkce_request import (
    CodePkceRequest,
    store_oauth_authorization_server_code_pkce_request_get_and_delete,
    store_oauth_authorization_server_code_pkce_request_put,
)
from store_session import Session, store_session_get, store_session_put

WIGGLE_ROOM = 2
# CLI_SERVE_FILE = "cli_serve_gevent.py"
CLI_SERVE_FILE = sys.argv[1]

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

    helper_hooks.hooks["navigation"] = navigation

    home_crumbs = _helper_navigation_generate_and_cache_breadcrumbs(url_home)
    assert home_crumbs == [("/", "Home")], home_crumbs
    auth_crumbs = _helper_navigation_generate_and_cache_breadcrumbs(url_auth)
    assert auth_crumbs == [("/", "Home"), ("/auth", "Auth")], auth_crumbs
    auth_session_crumbs = _helper_navigation_generate_and_cache_breadcrumbs(
        url_auth_session
    )
    assert auth_session_crumbs == [
        ("/", "Home"),
        ("/auth", "Auth"),
        ("/auth/session", "Auth Session"),
    ], auth_session_crumbs
    client_logout_crumbs = _helper_navigation_generate_and_cache_breadcrumbs(
        url_client_logout
    )
    assert client_logout_crumbs == [
        ("/", "Home"),
        ("/client", "Client"),
        ("/client/logout", "Client Logout"),
    ], client_logout_crumbs
    client_logout_crumbs2 = _helper_navigation_generate_and_cache_breadcrumbs(
        url_client_logout
    )
    assert client_logout_crumbs2 == client_logout_crumbs
    assert len(_crumbs_cache) == 4, len(_cache)


def test_driver_key_value_store_sqlite():
    driver_key_value_store_sqlite_put(
        store="test",
        key="foo1",
        value=dict(banana=3.14, foo="hello"),
        ttl=time.time() + 0.1,
    )
    result = driver_key_value_store_sqlite_get(store="test", key="foo1")
    assert result == {"banana": 3.14, "foo": "hello"}, result
    helper_log(__file__, "Stored foo1 successfully")

    driver_key_value_store_sqlite_put(
        store="test",
        key="foo1",
        value=dict(banana=3.15, foo="goodbye"),
        ttl=time.time() + 0.1,
    )
    result = driver_key_value_store_sqlite_get(store="test", key="foo1")
    assert result == {"banana": 3.15, "foo": "goodbye"}, result
    helper_log(__file__, "Updated foo1 successfully")

    driver_key_value_store_sqlite_put(
        store="test",
        key="foo1",
        value=dict(banana=3.16, foo="bye"),
    )
    result = driver_key_value_store_sqlite_get(store="test", key="foo1")
    assert result == {"banana": 3.16, "foo": "bye"}, result
    helper_log(__file__, "Updated foo1 successfully without a ttl")

    time.sleep(0.11)
    result = driver_key_value_store_sqlite_get(store="test", key="foo1")
    assert result == {"banana": 3.16, "foo": "bye"}, result
    helper_log(__file__, "foo1 is still there after the ttl time")

    driver_key_value_store_sqlite_put(
        store="test", key="foo2", value=dict(banana=3.14, foo="hello")
    )
    result = driver_key_value_store_sqlite_get(store="test", key="foo2")
    assert result == {"banana": 3.14, "foo": "hello"}, result

    driver_key_value_store_sqlite_put(
        store="test", key="foo3", value=dict(banana=3.14, foo="hello"), ttl=time.time()
    )
    try:
        print(driver_key_value_store_sqlite_get(store="test", key="foo3"))
    except:
        helper_log(__file__, "Cannot print foo3 since it has already expired")
    else:
        raise Exception("Showed the foo3 result when it should have expired")

    driver_key_value_store_sqlite_put(
        store="test", key="foo4", value=dict(banana=3.14, foo="hello")
    )
    driver_key_value_store_sqlite_del(store="test", key="foo4")

    try:
        print(driver_key_value_store_sqlite_get(store="test", key="foo4"))
    except:
        helper_log(__file__, "Cannot print foo4 since it has been successfully deleted")
    else:
        raise Exception("Showed the foo4 result when it should have expired")


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
    assert (
        render(title="main")
        == """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>main</title>
    <link rel="stylesheet" href="/style.css">
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
  </head>
  <body>
    <main>
        <h1>main</h1>
        
    </main>
	<script src="/script.js"></script>
  </body>
</html>"""
    ), render(title="main")

    assert (
        render_home(title="OAuth Client Home")
        == """<!DOCTYPE html>
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
    <a href="/oauth-code-pkce/login">Login without scopes</a>,  <a href="/oauth-code-pkce/login?scope=read">login with read scope</a>, <a href="/oauth-code-pkce/login?scope=no-such-scope">login with an invalid scope</a>, <a href="/saml2/login/">login with SAML</a>.</p>
    </main>
	<script src="/script.js"></script>
  </body>
</html>"""
    ), render_home(title="OAuth Client Home")

    assert (
        render_oauth_resource_owner_home(title="OAuth Resource Owner Home")
        == """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>OAuth Resource Owner Home</title>
    <link rel="stylesheet" href="/style.css">
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
  </head>
  <body>
    <main>
        <h1>OAuth Resource Owner Home</h1>
        <p>This is where the API V1 definitions will go.</p>
    </main>
	<script src="/script.js"></script>
  </body>
</html>"""
    ), render_oauth_resource_owner_home(title="OAuth Resource Owner Home")

    assert (
        render_saml_sp_success(session_info={})
        == """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Success!</title>
    <link rel="stylesheet" href="/style.css">
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
  </head>
  <body>
    <main>
        <h1>Success!</h1>
        <p>Successfully logged in with SAML. Here's the session info: <span id="session_info">{}</span></p>
    </main>
	<script src="/script.js"></script>
  </body>
</html>"""
    ), render_saml_sp_success(session_info={})


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
        driver.find_element(By.TAG_NAME, "body").text == "500 Error"
    ), driver.getPageSource()


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
    # curl -H "Authorization: Bearer $TOKEN" -v http://localhost:16001/api/v1
    print(url + "/api/v1")
    request = urllib.request.Request(
        url + "/api/v1",
        headers={"Authorization": "Bearer " + token},
    )
    with urllib.request.urlopen(request) as fp:
        response = json.loads(fp.read())
        print(response)
        assert list(response.keys()) == ["claims"], response.keys()
        # This doesn't match because iat and exp will be different.
        # assert json.dumps(response) == json.dumps({'claims': '{"aud": "client", "exp": 1690967312, "iat": 1690966712, "iss": "http://localhost:16001", "scope": "read", "sub": "sub"}'})
        claims = json.loads(response["claims"])
        assert claims["aud"] == "client"
        assert claims["iss"] == url
        assert claims["scope"] == "read"
        if expect_sub:
            assert claims["sub"] == "sub"


def make_unauthenticated_request_to_oauth_resource_owner(url, token):
    print(url + "/api/v1")
    request = urllib.request.Request(
        url + "/api/v1",
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
            "app_test",
            "client",
            url + "/oauth-code-pkce/callback",
            "read",
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
            "app_test",
            "client",
            "secret",
            "read",
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
            "app_test",
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
            "app_test",
            kid,
        ],
        env=env,
    )
    assert process.wait() == 0


def exec_cli_webhook_provider_keys_generate(env, kid):
    print()
    print("Webhook provider generate keys")
    process = subprocess.Popen(
        ["python3", "cli_webhook_provider_keys_generate.py", "app_test", kid], env=env
    )
    assert process.wait() == 0


def exec_cli_webhook_provider_keys_current_set(env, kid):
    print()
    print("Webhook provider set current key")
    process = subprocess.Popen(
        ["python3", "cli_webhook_provider_keys_current_set.py", "app_test", kid],
        env=env,
    )
    assert process.wait() == 0


def exec_cli_webhook_provider_sign_jwt(env, payload, kid):
    print()
    print("Webhook provider sign JWT")
    process = subprocess.Popen(
        ["python3", "cli_webhook_provider_sign_jwt.py", "app_test", payload, kid],
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
            "app_test",
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
            "app_test",
            "client",
            "sub",
            "read",
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
            "app_test",
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
    assert sorted(list(response.keys())) == ["access_token", "expires_in", "token_type"]
    assert response["expires_in"] == 600
    assert response["token_type"] == "bearer"
    helper_oauth_resource_owner_verify_jwt(response["access_token"])
    return response["access_token"]


def exec_cli_oauth_resource_owner_verify_jwt(env, token):
    print()
    print("OAuth resource owner verify JWT", token)
    process = subprocess.Popen(
        ["python3", "cli_oauth_resource_owner_verify_jwt.py", "app_test", token],
        stdout=subprocess.PIPE,
        env=env,
    )
    (stdout, _) = process.communicate()
    assert process.wait() == 0
    print(stdout)


if __name__ == "__main__":
    from helper_hooks import helper_hooks_setup

    helper_hooks_setup("app_test")

    # Unit tests
    test_navigation()
    test_render()
    test_driver_key_value_store_sqlite()
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
            ["python3", "-u", CLI_SERVE_FILE, "app_test"],
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
    #   "scope": "read",
    #   "sub": "sub"
    # }
    oauth_client_credentials_token = exec_cli_oauth_client_credentials(
        env, "client", "secret", ["read"]
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
