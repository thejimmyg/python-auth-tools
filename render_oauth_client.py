from markupsafe import Markup, escape

from render import render_main

oauth_client_home_markup = Markup(
    """<p>
    <a href="/oauth-client/login">Login without scopes</a>,  <a href="/oauth-client/login?scope=read">login with read scope</a>, <a href="/oauth-client/login?scope=no-such-scope">login with an invalid scope</a>, <a href="/saml2/login/">login with SAML</a>.</p>"""
)


def render_oauth_client_home(title: str):
    return render_main(title=title, body=oauth_client_home_markup)


oauth_client_success_markup = Markup(
    """<p>Successfully logged in. Here's the access token: <span id="jwt">{jwt}</span></p>"""
)


def render_oauth_client_success(jwt: str):
    return render_main(
        title="Success!", body=oauth_client_success_markup.format(jwt=jwt)
    )
