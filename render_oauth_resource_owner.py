from render import render_main
from markupsafe import Markup, escape

oauth_resource_owner_home_markup = Markup(
    "<p>This is where the API V1 definitions will go.</p>"
)


def render_oauth_resource_owner_home(title: str):
    return render_main(title=title, body=oauth_resource_owner_home_markup)


if __name__ == "__main__":
    print(render_oauth_resource_owner_home(title="OAuth Resource Owner Home"))
