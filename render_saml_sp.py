from markupsafe import Markup, escape

from render import render_main

saml_sp_success_markup = Markup(
    """<p>Successfully logged in with SAML. Here's the session info: <span id="session_info">{session_info}</span></p>"""
)


def render_saml_sp_success(session_info: str):
    return render_main(
        title="Success!", body=saml_sp_success_markup.format(session_info=session_info)
    )
