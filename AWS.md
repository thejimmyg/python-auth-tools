```sh
export KVSTORE_DYNAMODB_TABLE_NAME=Auth-Auth
export DOMAIN=auth.apps.jimmyg.org

python3 cli_oauth_authorization_server_client_credentials_put.py app_test client secret read
python3 cli_oauth_authorization_server_code_pkce_put.py app_test client https://${DOMAIN}/oauth-code-pkce/callback read
python3 cli_oauth_authorization_server_keys_generate.py app_test test
python3 cli_oauth_authorization_server_keys_current_set.py app_test test
```

