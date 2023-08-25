from markupsafe import Markup

from render import render

saml_sp_success_markup = Markup(
    """<p>Successfully logged in with SAML. Here's the session info: <span id="session_info">{session_info}</span></p>"""
)


def render_saml_sp_success(session_info: str):
    return render(
        title="Success!", body=saml_sp_success_markup.format(session_info=session_info)
    )
