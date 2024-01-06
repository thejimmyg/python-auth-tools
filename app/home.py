from render import Base, Html


class Home(Base):
    def __init__(self, title):
        self._title = title

    def body(self):
        return Html(
            """\
      <p>
        <a href="/oauth-code-pkce/login">Login without scopes</a>,
        <a href="/oauth-code-pkce/login?scope=read">login with read scope</a>,
        <a href="/oauth-code-pkce/login?scope=read%20offline_access">login with read and offline access scopes</a>,
        <a href="/oauth-code-pkce/login?scope=no-such-scope">login with an invalid scope</a>,
        <a href="/saml2/login/">login with SAML</a>.
      </p>"""
        )


def route_home(http):
    http.response.body = Home(title="OAuth Client Home")
