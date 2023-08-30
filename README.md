# Python Auth Tools

This is a work in progress set of OAuth and SAML 2 auth components that are ported from Go code I wrote years ago, that itself was based on even earlier Python code.

I now intend to use it to help in testing other components.

They probably aren't much use to you.

[AGPLv3](https://www.gnu.org/licenses/agpl-3.0.en.html)

## Terminology

See [https://www.oauth.com/oauth2-servers/definitions/](https://www.oauth.com/oauth2-servers/definitions/)

## NTP

You need to be running an NTP daemon (and may need to restart it if you see drift) otherwise the SAML flow might fail because the token is issued by the remote server before your computer's current time.

## Code Structure

I'd like this code to run in multiple very different environments like Raspberry Pi or AWS Lambda. So there are a few things that are a bit different:

* `.py` files are named according to the convention `componenttype_componentname_subcomponentname.py`. This means that all files of the same type (config, routes, stores, helpers, etc) are all close together which in turn means it is easy to copy patterns for each component type between components.
* Everything ends up with long names. But the upside of this is that is incredibly clear what each thing is, and refactoring is more straightforward because there are fewer name collisions
* There is no package. All the individual `.py` files should be on `PYTHONPATH` and can therefore just be imported, no need for `setup.py`, `pyproject.toml` or `pip` in order to use them
* There are no directories for `.py` files. By keeping everything top level, everything can import everything else easily without the code needing to be installed as a package.
* There aren't really any classes, they aren't needed. Instead each module is designed to be used once (singleton pattern) and so can store its state in module-level global variables. This means everything can be normal Python functions. The code does uses classes for data validation though. If you need to use the same component twice, make a copy of the files with a different name. The implementations will probably diverge over time anyway, so in the long term you'll reduce bugs.
* There is a hooks system so that you can customise the behaviour of the existing code without needing classes/inheritance etc.
* The code isn't threadsafe, instead it uses gevent for cooperative multitasking making it very efficient in a single process. You an safely run multiple processes at once on the same computer and round-robin proxy to each if you want to make the most of the available CPUs.
* All HTTP headers are lowercase. If you set or try to access anything not lowercase, it won't error, but the behaviour is undefined.

## Understanding Hooks

To run any of the code, you compose the different `.py` files together into your own `hooks_` Python module that imports the `helper_hooks` module and sets its `hooks` variable with all the hooks you want to register.

That `hooks_` module name is then passed to one of the `cli_*.py` files on the command line when you run it.

Behind the scenes, each of the modules that can use your hooks will do so by looking them up in `helper_hooks.hooks`.

The only example of this is the `app_test.py` file which is used to run a server that combines an OAuth 2 Authorization Server, Clients, Resource Owners as well as Login, consen (albeit automatically granted) and SAML2 flows as part of the test suite.


## Install


```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

The SAML functionality needs `xmlsec1`. You can get it on macOS with `brew install libxmlsec1`. On Debian bookworm, just install `python3-pysaml2` and it is a dependency.

## Config

Optional:

```sh
TMP_DIR='./tmp'
STORE_DIR='./store'
```

## Plugins

* init
* cleanup
* routes
* \*\*hooks

XXX More documentation needed here.

* app
* plugin
* hook

## Run

In the first terminal:

```sh
source .venv/bin/activate
```

```sh
python3 cli_oauth_authorization_server_client_credentials_put.py app_test client secret read
python3 cli_oauth_authorization_server_code_pkce_put.py app_test client http://localhost:16001/oauth-code-pkce/callback read
python3 cli_oauth_authorization_server_keys_generate.py app_test test
python3 cli_oauth_authorization_server_keys_current_set.py app_test test
```

```sh
python3 cli_serve_gevent.py app_test
```

In the second terminal:

```sh
source .venv/bin/activate
```

```sh
export TOKEN=`python3 cli_oauth_authorization_server_sign_jwt.py app_test client sub "read" test` && echo $TOKEN
python3 cli_oauth_resource_owner_verify_jwt.py app_test "$TOKEN"
curl -H "Authorization: Bearer $TOKEN" -v http://localhost:16001/api/v1
```

```sh
python3 cli_webhook_provider_keys_generate.py app_test test
python3 cli_webhook_provider_keys_current_set.py app_test test
export PAYLOAD='{"hello": "world"}'
export SIG=`python3 cli_webhook_provider_sign_jwt.py app_test "$PAYLOAD" test` && echo $SIG
python3 cli_webhook_consumer_verify_jwt.py app_test "$SIG" "$PAYLOAD" "http://localhost:16001/.well-known/webhook-provider-jwks.json"
```

```sh
python3 cli_oauth_client_credentials.py app_test client secret read
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

On macOS you'll need a new version of ChromeDriver. You can fetch it like this:

```sh
curl -O  https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/mac-arm64/chromedriver-mac-arm64.zip
unzip chromedriver-mac-arm64.zip
mv chromedriver-mac-arm64/chromedriver .
rm chromedriver-mac-arm64.zip
rm -r chromedriver-mac-arm64
```

Then you can run the tests with the path to the local `chromedriver` like this:

```sh
rm -rf ./store ./test ./tmp && PATH="$PWD:$PATH" python3 test.py
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
from route_static import route_static

routes = {
    "/": route_static("python-auth-tools/static/file", "text/plain"),
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

## Conceptual ERD


At the moment there is no physical store or management for the oauth_authorization_server_user, you simply enter their sub as part of the code + PKCE flow.

The database structure looks like this:

```mermaid
erDiagram

    oauth_authorization_server_session {
        string session_id
        string code
    }

    oauth_authorization_server_current_key {
        string kid
    }


    oauth_authorization_server_client_credentials_client {
        string client_id
        string client_secret
        list[string] scopes
    }

    oauth_authorization_server_code_client {
        string client_id
        string redirect_uri
        list[string] scopes
    }

    oauth_authorization_server_code {
        string client_id
        string code_challenge
        list[string] scopes
        string state
        string sub
    }

    oauth_authorization_server ||--|{ oauth_authorization_server_client_credentials_client : "has many"
    oauth_authorization_server ||--|{ oauth_authorization_server_code_client : "has many"
    oauth_authorization_server_code_client ||--|{ oauth_authorization_server_code : has
    oauth_authorization_server ||--|{ oauth_authorization_server_user : "has many"
    oauth_authorization_server_user ||--|{ oauth_authorization_server_session : "has many"
    oauth_authorization_server ||--|{ oauth_authorization_server_session : "has many"
    oauth_authorization_server ||--|| oauth_authorization_server_current_key : "exactly one"
```

XXX Do we need oauth_authorization_server_code string state?

In addition the OAuth Authorizatioin Server uses the filesystem to store private keys and a `jwks.json` file:

```mermaid
erDiagram
    oauth_authorization_server_private_key {
        string kid
        string private_private_key
    }
    oauth_authorization_server ||--|{ oauth_authorization_server_private_key : "has many"
    oauth_authorization_server_jwks ||--|{ oauth_authorization_server_private_key : "has many"
```


When a Code + PKCE client redirects to the OAuth Authorizatioin Server authoire
endpoint, a code value is generated and stored, with the code itself being
added to the session. After the login, this means that the code value can be
retrieved from the session and sent to the client, where it can then call the
OAuth Authorizatioin Server token endpoint with the code to get the access
tokens.

XXX Why can't the session implementation be generic? At the moment it is specifically to cache the code that is requested (code verifier?)


The storage for a Code + PKCE client looks like this:

```mermaid
erDiagram
    oauth_code_pkce {
        string client_id
    }
    oauth_code_pkce_code_verifier {
        string state
        string code_verifier
    }
    oauth_code_pkce ||--|{ oauth_code_pkce_code_verifier : "has many"
```

And for a client credentials client there isn't really any storage needed beacuase the client_id, secret, and requested scopes are all passed at the time of the flow:

```mermaid
erDiagram
    oauth_client_credentials {
    }
```

The webhook provider structure is similar to the keys part of the OAuth Authorization Server:

```mermaid
erDiagram
    webhook_provider ||--|{ webhook_provider_key : "has many"
    webhook_provider ||--|| webhook_provider_current_key : "exactly one"
    webhook_provider_jwks ||--|{ webhook_provider_key : "has many"
```

## OAuth Code + PKCE Flow

This misses out scope checks too.

```mermaid
sequenceDiagram
    User's Browser->>OAuth Client Server: /oauth-code-pkce/login?scope=<scopes>
    OAuth Client Server->>OAuth Client Server: Generate a code verifier and state, derive a code challenge from the code verifier
    OAuth Client Server->>Code Verifier Store: Save state: code_verifier
    OAuth Client Server->>User's Browser: HTTP redirect response with Location set to authorize URL redirect
    User's Browser->>OAuth Authorization Server: /oauth/authorize?response_type=code&state=<state>&client_id=<client_id>&code_challenge=<code_challenge>&code_challenge_method=S256
    OAuth Authorization Server-->>OAuth Authorization Server: Login flow and consent (see other diagram)
    OAuth Authorization Server->>OAuth Authorization Server: Generate code value
    OAuth Authorization Server->>Code Value Store: Save code: client_id, code_challenge, scopes, state, sub
    OAuth Authorization Server->>User's Browser: HTTP redirect response with Location set to client redirect uri
    User's Browser->>OAuth Client Server: /oauth-code-pkce/callback?state=<state>&code=<code>
    OAuth Client Server->>Code Verifier Store: get and delete code_verifier using state <state>
    Code Verifier Store->>OAuth Client Server: <code_verifier>
    OAuth Client Server->>OAuth Authorization Server: Ask for token on the server /oauth/token?code_verifier=<code_verifier>&code=<code>&grant_type=code
    OAuth Authorization Server->>Code Value Store: Get client ID, code challenge, scopes and sub using the code <code>
    Code Value Store->>OAuth Authorization Server: <client ID>, <code_challenge>, <scopes>, <sub>
    OAuth Authorization Server->>OAuth Authorization Server: Verify the code challenge using the code verifier
    OAuth Authorization Server-->>OAuth Authorization Server: Sign key flow (see other diagram)
    OAuth Authorization Server->>OAuth Client Server: {access_token: <access_token>, expires: <expires>}
    OAuth Client Server-->>OAuth Client Server: Session flow (see other diagram)
    OAuth Client Server->>User's Browser: Success
```

Is it OK to use the state as the key for the code verifier in the client server? I think it is.

The token exchange doesn't check the sub matches the login session. If you have obtained the code, you can exchange it.

## OAuth Client Credentials Flow

This misses out scope checks too.

```mermaid
sequenceDiagram
    Machine->>OAuth Client Credentials Library: <client_id>, <secret>, <scopes>
    OAuth Client Credentials Library->>OAuth Authorization Server: Get /.well-known/openid-configuration
    OAuth Authorization Server->>OAuth Client Credentials Library: {token_endpoint: <token_endpoint>, ...}
    OAuth Client Credentials Library->>OAuth Authorization Server: <token_endpoint>?grant_type=client_credentials&scope=<scope>, Authorization: Basic base64encode(<client_id>+':'+<secret>)
    OAuth Authorization Server->>OAuth Client Credentials Library: {access_token: <access_token>, expires: <expires>}
    OAuth Client Credentials Library->>Machine: Success
```

## Resource Owner Flow


```mermaid
sequenceDiagram
    User/Machine->>OAuth Resource Owner: Make an API call with the <access_token>
    OAuth Resource Owner->>OAuth Resource Owner: extract <iss> key and verify it is an issuer we trust (XXX We don't verify yet?)
    OAuth Resource Owner->>OAuth Authorization Server: Get and cache <iss>/.well-known/openid-configuration
    OAuth Authorization Server->>OAuth Resource Owner: {jwks_uri: <jwks_uri>, ...}
    OAuth Resource Owner->>OAuth Authorization Server: Get and cache JWKS from <jwks_uri>
    OAuth Authorization Server->>OAuth Resource Owner: {keys: [{kid: <kid1>, ...}]}
    OAuth Resource Owner->>OAuth Resource Owner: Extract <kid> from <access_token>
    OAuth Resource Owner->>OAuth Resource Owner: Find the corresponding public keys in the JWKS response
    OAuth Resource Owner->>OAuth Resource Owner: Verify <access_token> signature using public key
    OAuth Resource Owner->>OAuth Resource Owner: Handle the API call
    OAuth Resource Owner->>User/Machine: API Response
```


## Webhook Flow

Send an event to a webhook consumer:

```mermaid
sequenceDiagram
    Resource Owner->>Webhook Provider: Trigger webhook consumers with an event <payload> {iss: ..., event: ...}
    Webhook Provider->>Webhook Current Key Store: Get and cache current key
    Webhook Current Key Store->>Webhook Provider: <kid>
    Webhook Provider->>Webhook Private Key Directory: Read private key <kid>
    Webhook Private Key Directory->>Webhook Provider: <private_key>
    Webhook Provider->>Webhook Provider: Sign <payload> using <private_key>
    Webhook Provider->>Webhook Provider: Detatch middle part of JWT leaving <detatched_token> of form ey..sig
    Webhook Provider->>Webhook Consumer: POST <payload> as the HTTP body with an HTTP header Authorization: <detatched_token>
```

The webhook consumer verifies the `<body>` it gets `POST`ed like this:

```mermaid
sequenceDiagram
    Webhook Consumer->>Webhook Consumer: read <iss> from payload body and verify it is the issuer we expect (XXX We don't verify yet?)
    Webhook Consumer->>Webhook Consumer: base64 encode the whole body to <body_base64_encoded>
    Webhook Consumer->>Webhook Consumer: read the authorisation header and re-assemble a <jwt> by putting <body_base64> in between the .. characters of the detatched token
    Webhook Consumer->>Webhook Provider: Get and cache keys from <iss>/.well-known/webhook-provider-jwks.json # XXX This URL is non-standard, but I think it is a sensible location
    Webhook Provider->>Webhook Consumer: {keys: [{kid: <kid1>, ...}]}
    Webhook Consumer->>Webhook Consumer: Extract <kid> from the generated <jwt>
    Webhook Consumer->>Webhook Consumer: Find the corresponding public keys in the JWKS response
    Webhook Consumer->>Webhook Consumer: Verify <jwt> signature using public key
    Webhook Consumer->>Webhook Consumer: Act on the other keys in the JSON body, now that you trust the authorization
```

This flow is robust in the face of key rotation, and doesn't require a shared secret of any type.

## SAML SP Flow

```mermaid
sequenceDiagram
```
