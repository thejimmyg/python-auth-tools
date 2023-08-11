from markupsafe import Markup

import plugins

main_markup = Markup(
    """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>{title}</title>
    <link rel="stylesheet" href="/style.css">
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
  </head>
  <body>
    <main>
        <h1>{title}</h1>
        {body}
    </main>
	<script src="/script.js"></script>
  </body>
</html>"""
)


def render_main(title: str, body: Markup = Markup("")):
    return plugins.main_markup.format(title=title, body=body)
