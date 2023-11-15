import cgi
from io import BytesIO

import helper_hooks
from render import Base, Html


def hello(http):
    if http.request.method == "post":
        # print(http.request.headers)

        parts = http.request.headers["content-type"].split(";")
        assert parts[0].lower().strip() == "multipart/form-data"
        assert parts[1].strip().lower().startswith("boundary=")
        boundary = parts[1].strip().encode("ascii")[len("boundary=") :]
        # print(boundary)
        pdict = dict(boundary=boundary)
        fields = cgi.parse_multipart(BytesIO(http.request.body), pdict)
        # print(fields)
        counter = 0
        for file in fields.get("files"):
            counter += 1
            print(counter, len(file))
        http.response.body = Base(
            title="Upload files",
            body=Html("<p>Got ") + str(counter) + Html("files.</p>"),
        )
    else:
        http.response.body = Base(
            title="Upload files",
            body=Html(
                """
        <form action="" method="POST" enctype="multipart/form-data">
          <label for="files">Select files:</label>
          <input type="file" id="files" name="files" multiple><br><br>
          <input type="submit">
        </form>
    """
            ),
        )


helper_hooks.hooks = {"routes": {"/": hello}}
