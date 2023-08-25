from markupsafe import Markup

from render import render

oauth_resource_owner_home_markup = Markup(
    "<p>This is where the API V1 definitions will go.</p>"
)


def render_oauth_resource_owner_home(title: str):
    return render(title=title, body=oauth_resource_owner_home_markup)
