from markupsafe import Markup

import helper_hooks
from render import render


def route_home(http):
    urls = helper_hooks.hooks["urls"]
    http.response.body = render(
        "Home",
        Markup(
            """
<ul>
  <li><a href="{url_auth}">Auth</a> (Stub)</li>
  <li><a href="{url_client}">Client</a> (System Under Test)</li>
  <li><a href="{url_resource_owner_a}">Resource Owner A</a> (Stub)</li>
  <li><a href="{url_resource_owner_b}">Resource Owner B</a> (Stub)</li>
</ul>
"""
        ).format(
            url_auth=urls["url_auth"],
            url_client=urls["url_client"],
            url_resource_owner_a=urls["url_resource_owner_a"],
            url_resource_owner_b=urls["url_resource_owner_b"],
        ),
    )
