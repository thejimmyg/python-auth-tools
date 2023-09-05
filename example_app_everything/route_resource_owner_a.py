from markupsafe import Markup

import helper_hooks
from render import render


def route_resource_owner_a(http):
    http.response.body = render(
        "Resource Owner A",
        Markup(
            """
<p><a href="{url_home}">Home</a> &gt; Resource Owner A</p>
<ul>
  <li><a href="{url_resource_owner_a_api}">API</a></li>
</ul>
"""
        ).format(
            url_home=helper_hooks.hooks["urls"]["url_home"],
            url_resource_owner_a_api=helper_hooks.hooks["urls"][
                "url_resource_owner_a_api"
            ],
        ),
    )


def route_resource_owner_a_api(http):
    http.response.body = render(
        "Resource Owner A API",
        Markup(
            """
<p><a href="{url_home}">Home</a> &gt; <a href="{url_resource_owner_a}">Resource Owner A</a> &gt; API</p>
<ul>
  <li><a href="{url_resource_owner_a_api_read}"><code>GET read</code></a></li>
</ul>
"""
        ).format(
            url_home=helper_hooks.hooks["urls"]["url_home"],
            url_resource_owner_a=helper_hooks.hooks["urls"]["url_resource_owner_a"],
            url_resource_owner_a_api_read=helper_hooks.hooks["urls"][
                "url_resource_owner_a_api_read"
            ],
        ),
    )


def route_resource_owner_a_api_read(http):
    http.response.body = {"msg": "Not implemented"}
