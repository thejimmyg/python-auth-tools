from markupsafe import Markup

import helper_hooks
from render import render


def route_resource_owner_b(http):
    http.response.body = render(
        "Resource Owner B",
        Markup(
            """
<p><a href="{url_home}">Home</a> &gt; Resource Owner B</p>
<ul>
  <li><a href="{url_resource_owner_b_api}">API</a></li>
</ul>
"""
        ).format(
            url_home=helper_hooks.hooks["urls"]["url_home"],
            url_resource_owner_b_api=helper_hooks.hooks["urls"][
                "url_resource_owner_b_api"
            ],
        ),
    )


def route_resource_owner_b_api(http):
    http.response.body = render(
        "Resource Owner B API",
        Markup(
            """
<p><a href="{url_home}">Home</a> &gt; <a href="{url_resource_owner_b}">Resource Owner B</a> &gt; API</p>
<ul>
  <li><a href="{url_resource_owner_b_api_write}"><code>GET write</code></li>
</ul>
"""
        ).format(
            url_home=helper_hooks.hooks["urls"]["url_home"],
            url_resource_owner_b=helper_hooks.hooks["urls"]["url_resource_owner_b"],
            url_resource_owner_b_api_write=helper_hooks.hooks["urls"][
                "url_resource_owner_b_api_write"
            ],
        ),
    )


def route_resource_owner_b_api_write(http):
    http.response.body = {"msg": "Not implemented"}
