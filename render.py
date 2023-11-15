from template import Html


class Base:
    def __init__(self, title, body):
        self._title = title
        self._body = body

    def title(self):
        return self._title

    def body(self):
        return self._body

    def render(self):
        return (
            Html(
                """\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>"""
            )
            + self.title()
            + Html(
                """</title>
    <link rel="stylesheet" href="/style.css">
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
  </head>
  <body>
    <main>
      <h1>"""
            )
            + self.title()
            + Html("</h1>\n")
            + self.body()
            + Html(
                """
    </main>
    <script src="/script.js"></script>
  </body>
</html>"""
            )
        ).render()
