from render_oauth_client import render_oauth_client_home


def oauth_client_home(http):
    http.response.body = render_oauth_client_home(title="OAuth Client Home")
