```sh
export KVSTORE_DYNAMODB_TABLE_NAME=Auth-Table
export DOMAIN=auth.apps.jimmyg.org

python3 cli_oauth_authorization_server_client_credentials_put.py app_test client secret read
python3 cli_oauth_authorization_server_code_pkce_put.py app_test client https://${DOMAIN}/oauth-code-pkce/callback read
python3 cli_oauth_authorization_server_keys_generate.py app_test test
python3 cli_oauth_authorization_server_keys_current_set.py app_test test
```

A successful auth flow takes this long at the end:

```
REPORT RequestId: adceea81-81b7-44a2-9c9f-492fbbc8f199	Duration: 3550.56 ms	Billed Duration: 3551 ms	Memory Size: 128 MB	Max Memory Used: 116 MB	Init Duration: 1298.99 ms	
```
