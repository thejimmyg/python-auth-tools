from render import render_main
from markupsafe import Markup, escape

saml_sp_success_markup = Markup(
    """<p>Successfully logged in with SAML. Here's the session info: <span id="session_info">{session_info}</span></p>"""
)


def render_saml_sp_success(session_info: str):
    return render_main(
        title="Success!", body=saml_sp_success_markup.format(session_info=session_info)
    )


if __name__ == "__main__":
    print(render_saml_sp_success(session_info={}))
