import json
import math
import os
import random
import subprocess
import threading
import time
import urllib.request
from helper_crypto import verify_jwt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def oauth_client_flow_code_okce(driver, url):
    print(url)
    driver.get(url + "/")
    assert "OAuth Client Home" in driver.title
    elem = driver.find_element(By.LINK_TEXT, "Login without scopes")
    elem.click()
    assert "Login" in driver.page_source
    elem = driver.find_element(By.NAME, "sub")
    elem.clear()
    now = math.floor(time.time())  # Round down
    test_sub = "test_sub_{}".format(now)
    elem.send_keys(test_sub)
    elem.send_keys(Keys.RETURN)
    elem = driver.find_element(By.ID, "jwt")
    jwt = elem.text
    claims = verify_jwt(jwt)
    # print(oidc)
    # assert oidc['issuer'] == url
    # assert oidc['authorization_endpoint'] = url + '/oauth/authorize',
    # assert oidc['token_endpoint'] =  url+'/oauth/token', 'jwks_uri': url + '/.well-known/jwks.json', 'grant_types_supported': ['authorization_code', 'client_credentials'], 'token_endpoint_auth_methods_supported': ['client_secret_basic'], 'scopes_supported': ['openid', 'profile'], 'code_challenge_methods_supported': ['S256']}
    wiggle_room = 2
    assert claims["aud"] == "client"
    assert claims["exp"] > now and claims["exp"] <= now + 600 + wiggle_room
    assert claims["iat"] >= now and claims["iat"] <= now + wiggle_room, (
        claims["iat"],
        now,
    )
    assert claims["iss"] == url
    assert claims["sub"] == test_sub


def saml_sp_flow(driver, url):
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


def make_authenticated_request_to_oauth_resource_owner(url, token):
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
        assert claims["sub"] == "sub"


def make_unauthenticated_request_to_oauth_resource_owner(url, token):
    print(url + "/api/v1")
    request = urllib.request.Request(
        url + "/api/v1",
        headers={"Authorization": "Bearer " + token + "invalid"},
    )
    try:
        with urllib.request.urlopen(request) as fp:
            response = json.loads(fp.read())
    except urllib.error.HTTPError as e:
        error = e.read().decode("utf8")
        print(e, error)
        assert error == "401 Not Authenticated", error
    else:
        raise Exception(
            "Fetching OAuth Resource Owner API did not raise when using an invalid token"
        )


def generate_keys(env):
    private_key_process = subprocess.Popen(
        ["python3", "cli_oauth_authorization_server_generate_keys.py"], env=env
    )
    assert private_key_process.wait() == 0
    private_key_process.wait()


def sign_jwt_proc(env):
    print("About to sign JWT")
    print()
    sign_jwt_process = subprocess.Popen(
        [
            "python3",
            "cli_oauth_authorization_server_sign_jwt.py",
            "client",
            "sub",
            "read",
        ],
        stdout=subprocess.PIPE,
        env=env,
    )
    (stdout, _) = sign_jwt_process.communicate()
    assert sign_jwt_process.wait() == 0
    print(stdout)
    token = stdout.decode("utf8").strip()
    return token


def client_credentials_flow(env, client, secret):
    print("About to run client credentials flow")
    print()
    client_credentials_process = subprocess.Popen(
        ["python3", "cli_oauth_client_flow_client_credentials.py", client, secret],
        stdout=subprocess.PIPE,
        env=env,
    )
    (stdout, _) = client_credentials_process.communicate()
    assert client_credentials_process.wait() == 0
    print(stdout)
    response = json.loads(stdout.decode("utf8").strip())
    assert sorted(list(response.keys())) == ["access_token", "expires_in", "token_type"]
    assert response["expires_in"] == 600
    assert response["token_type"] == "bearer"
    verify_jwt(response["access_token"])
    return response["access_token"]


def verify_jwt_proc(env, token):
    print("Verify JWT", token)
    print()
    verify_jwt_process = subprocess.Popen(
        ["python3", "cli_oauth_resource_owner_verify_jwt.py", token],
        stdout=subprocess.PIPE,
        env=env,
    )
    (stdout, _) = verify_jwt_process.communicate()
    assert verify_jwt_process.wait() == 0
    print(stdout)


if __name__ == "__main__":
    port = 49152 + math.floor((65535 - 49152) * random.random())
    url = "http://localhost:" + str(port)
    store_dir = os.path.join("test", str(port), "store")
    print(url)
    os.makedirs(store_dir, exist_ok=True)
    tmp_dir = os.path.join("test", str(port), "tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    os.makedirs(os.path.join(store_dir, "oauth_authorization_server"), exist_ok=True)
    with open(
        os.path.join(store_dir, "oauth_authorization_server", "clients.json"), "w"
    ) as fp:
        fp.write(
            json.dumps(
                {
                    "client_credentials": {
                        "client": {"secret": "secret", "scopes": []}
                    },
                    "code": {
                        "client": {"redirect_uri": url + "/oauth-client/callback"}
                    },
                }
            )
        )
    env = {
        "PATH": os.environ["PATH"],
        "URL": url,
        "STORE_DIR": store_dir,
        "TMP_DIR": tmp_dir,
    }

    generate_keys(env)

    code_flow_token = sign_jwt_proc(env)

    log_path = os.path.join(tmp_dir, "server.log")
    p = [None]

    def start_server():
        print(url, "logging to", log_path)
        log = open(log_path, "wb")
        p[0] = subprocess.Popen(
            # Have to run Python in unbuffered mode (-u) to get the logs streaming to the log files
            ["python3", "-u", "cli_serve_gevent.py"],
            env=env,
            stdout=log,
            stderr=log,
        )

    server_thread = threading.Thread(target=start_server, args=())
    server_thread.start()
    # Not ideal, but we need to wait for the server to start
    time.sleep(10)

    verify_jwt_proc(env, code_flow_token)
    # {
    #   "aud": "client",
    #   "exp": 1691075255,
    #   "iat": 1691074655,
    #   "iss": "http://localhost:61022",
    #   "scope": "read",
    #   "sub": "sub"
    # }
    client_flow_token = client_credentials_flow(env, "client", "secret")
    verify_jwt_proc(env, client_flow_token)
    # {
    #   "aud": "client",
    #   "exp": 1691075259,
    #   "iat": 1691074659,
    #   "iss": "http://localhost:61022",
    #   "sub": "client"
    # }
    for token in [code_flow_token]:
        make_authenticated_request_to_oauth_resource_owner(url, token)
        make_unauthenticated_request_to_oauth_resource_owner(url, token)
    driver = webdriver.Chrome()
    oauth_client_flow_code_okce(driver, url)
    saml_sp_flow(driver, url)
    p[0].kill()
    server_thread.join()
    driver.close()
    print("SUCCESS! Server logs in:", log_path)
