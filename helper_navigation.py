from markupsafe import Markup

import helper_hooks
from helper_log import helper_log


def find_url(navigation, url, context=None):
    if context is None:
        context = []
    for k in navigation:
        if k[0] == url:
            context.append(k)
            helper_log(__file__, "Found in key", k, url)
            return context
    for k, v in navigation.items():
        c = context[:]
        c.append(k)
        helper_log(__file__, "Looking in:", v)
        result = find_url(v, url, c)
        helper_log(__file__, "Result:", result)
        if result is not None:
            helper_log(__file__, "returning", result)
            return result
    helper_log(__file__, "not found")


_crumbs_cache = {}


def _helper_navigation_generate_and_cache_breadcrumbs(url):
    if url not in _crumbs_cache:
        navigation = helper_hooks.hooks["navigation"]
        _crumbs_cache[url] = find_url(navigation, url)
    return _crumbs_cache[url]


_html_cache = {}


def helper_navigation_generate_and_cache_breadcrumbs(url):
    if url not in _html_cache:
        crumbs = _helper_navigation_generate_and_cache_breadcrumbs(url)
        html = Markup("")
        if len(crumbs) > 1:
            for part in crumbs[:-1]:
                html += Markup('<a href="{target}">{title}</a> &gt; ').format(
                    target=part[0], title=part[1]
                )
            html += Markup("{title}").format(title=crumbs[-1][1])
        _html_cache[url] = html
    return _html_cache[url]
