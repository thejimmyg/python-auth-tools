# Python Auth Tools

This is a work in progress set of OAuth and SAML 2 auth components that are ported from Go code I wrote years ago, that itself was based on even earlier Python code.

I now intend to use it to help in testing other components.

They probably aren't much use to you.

[AGPLv3](https://www.gnu.org/licenses/agpl-3.0.en.html)

## Terminology

See [https://www.oauth.com/oauth2-servers/definitions/](https://www.oauth.com/oauth2-servers/definitions/)

## NTP

You need to be running an NTP daemon (and may need to restart it if you see drift) otherwise the SAML flow might fail because the token is issued by the remote server before your computer's current time.

## Config

Optional:

```sh
TMP_DIR='./tmp'
STORE_DIR='./store'
```

## Install


```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

The SAML functionality needs `xmlsec1`. You can get it on macOS with `brew install libxmlsec1`. On Debian bookworm, just install `python3-pysaml2` and it is a dependency.

## Run

In the first terminal:

```sh
source .venv/bin/activate
```

```sh
mkdir -p ./store/oauth_authorization_server
python3 cli_oauth_authorization_server_generate_keys.py route_test test
python3 cli_oauth_authorization_server_set_current_key.py route_test test
cat << EOF > ./store/oauth_authorization_server/clients.json
{
    "client_credentials": {
        "client": {"secret": "secret", "scopes": ["read"]}
    },
    "code": {
        "client": {"redirect_uri": "http://localhost:16001/oauth-client/callback"}
    }
}
EOF
```

```sh
python3 cli_serve_gevent.py route_test
```

In the second terminal:

```sh
source .venv/bin/activate
```

```sh
export TOKEN=`python3 cli_oauth_authorization_server_sign_jwt.py client sub "read" test` && echo $TOKEN
python3 cli_oauth_resource_owner_verify_jwt.py "$TOKEN"
curl -H "Authorization: Bearer $TOKEN" -v http://localhost:16001/api/v1
```

```sh
python3 cli_webhook_generate_keys.py route_test test
python3 cli_webhook_set_current_key.py route_test test
export PAYLOAD='{"hello": "world"}'
export SIG=`python3 cli_webhook_sign_jwt.py "$PAYLOAD" test` && echo $SIG
python3 cli_webhook_consumer_verify_jwt.py "$SIG" "$PAYLOAD" "http://localhost:16001/.well-known/webhook-jwks.json"
```

```sh
python3 cli_oauth_client_flow_client_credentials.py client secret read
```

## Test

Install Chromium and Chromium Webdriver:

```sh
apt install -y chromium chromium-driver python3-selenium
```

Then run (deleting your existing stores):

```sh
sudo systemctl restart ntp
rm -rf ./store ./test ./tmp && python3 test.py
```

## Using this via a git submodule

```sh
git init
git submodule add https://github.com/thejimmyg/python-auth-tools
git add .gitmodules python-auth-tools
git commit -m 'Initialised project'
```

After cloning a repo with submodules, or if you want to update the submodule to the latest commit, run:

```sh
git submodule update
```

Or during development just symlink this project somewhere:

```sh
ln -s ../python-auth-tools python-auth-tools
```

Create you own plugin:

```sh
cat << EOF > my_app.py
from route_static import static

routes = {
    "/": static("python-auth-tools/static/file", "text/plain"),
}
EOF
```

Then you can use the files by adjusting your `PYTHONPATH`:

```sh
export PYTHONPATH="${PWD}:${PWD}/python-auth-tools:${PYTHONPATH}"
python3 python-auth-tools/cli_serve_gevent.py my_app
```

See [https://git-scm.com/book/en/v2/Git-Tools-Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) and [https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH)

## Contributions

Contributions must be public domain or licensed under the MIT license as well
as the AGPLv3, even though this code is AGPLv3. This allows for possible
re-licensing in future.

## Dev

```sh
isort . &&  autoflake -r --in-place --remove-unused-variables --remove-all-unused-imports . && black .
```
