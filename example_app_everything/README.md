# Auth Full Example

## Setup

```
export PYTHONPATH="./:../python-auth-tools:$PYTHONPATH"
```

```
python3 ../cli_oauth_authorization_server_client_credentials_put.py app_everything client secret read
python3 ../cli_oauth_authorization_server_code_pkce_put.py app_everything client http://localhost:16001/client/callback read
python3 ../cli_oauth_authorization_server_keys_generate.py app_everything test
python3 ../cli_oauth_authorization_server_keys_current_set.py app_everything test
```

```sh
URL=http://localhost:16001 python3 ../cli_serve_gevent.py app_everything
```
