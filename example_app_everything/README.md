# Example App Everything

## Setup

Create a virtual Python environment and install dependencies:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```sh
export PYTHONPATH="${PWD}:${PWD}/../:$PYTHONPATH"
```

Setup OAuth server clients and keys:

```sh
rm -r store
python3 ../cli_oauth_authorization_server_client_credentials_put.py app_everything client secret read
python3 ../cli_oauth_authorization_server_code_pkce_put.py app_everything client http://localhost:16001/client/callback read
python3 ../cli_oauth_authorization_server_keys_generate.py app_everything test
python3 ../cli_oauth_authorization_server_keys_current_set.py app_everything test
```

## Run

Activate the environment and set up the path:

```sh
source .venv/bin/activate
```

Run the server using WSGI:

```sh
URL=http://localhost:16001 python3 ../cli_serve_wsgi.py app_everything
```

Visit [http://localhost:16001/](http://localhost:16001/).

## Deploy to Lambda

Build and publish a layer with all the dependencies:

```sh
./build-lambda-layer-and-publish.sh mylibs3 'My libs 3'
```

Create and publish a lambda function:

```sh
```
