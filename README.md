# Python Auth Tools

This is a work in progress set of OAuth and SAML 2 auth components that are ported from Go code I wrote years ago, that itself was based on even earlier Python code.

I now intend to use it to help in testing other components.

They probably aren't much use to you.

[AGPLv3](https://www.gnu.org/licenses/agpl-3.0.en.html)

## Terminology

See [https://www.oauth.com/oauth2-servers/definitions/](https://www.oauth.com/oauth2-servers/definitions/)

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
python3 cli_oauth_authorization_server_generate_keys.py
cat << EOF > ./store/oauth_authorization_server/clients.json
{
    "client_credentials": {
        "client": {"secret": "secret", "scopes": []}
    },
    "code": {
        "client": {"redirect_uri": "http://localhost:16001/oauth-client/callback"}
    }
}
EOF
```

```sh
python3 cli_serve_gevent.py
```

In the second terminal:

```sh
source .venv/bin/activate
```

```sh
export TOKEN=`python3 cli_oauth_authorization_server_sign_jwt.py client sub "read"` && echo $TOKEN
python3 cli_oauth_resource_owner_verify_jwt.py "$TOKEN"
curl -H "Authorization: Bearer $TOKEN" -v http://localhost:16001/api/v1
```

```sh
python3 cli_oauth_client_flow_client_credentials.py client secret
```

## Dev

```sh
isort .
autoflake -r --in-place --remove-unused-variables .
black .
```

## Test

Install Chromium and Chromium Webdriver:

```sh
apt install -y chromium chromium-driver python3-selenium
```

Then run:

```sh
python3 test.py
```

## Contributions

Contributions must be public domain or licensed under the MIT license.
