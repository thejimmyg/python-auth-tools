from render import Html


def helper_meta_refresh_html(target):
    return (
        Html('<html><head><meta http-equiv="refresh" content="0; url=')
        + target
        + Html('"></head><body><a href="')
        + target
        + Html('"></a></body></html>')
    )
