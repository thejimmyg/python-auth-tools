from markupsafe import Markup


def helper_meta_refresh_html(target):
    return Markup(
        '<html><head><meta http-equiv="refresh" content="0; url={target}"></head><body><a href="{target}"></a></body></html>'
    ).format(target=target)
