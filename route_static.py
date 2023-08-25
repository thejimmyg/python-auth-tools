import gzip
import hashlib
import os
import urllib.parse

from config import config_tmp_dir

config_gzipped_dir = os.path.join(config_tmp_dir, "gzipped")

# XXX There is a bug in static() where if the source file mtime changes, it is still serving the old cached version with the etag. We probably don't want it to do that.

# XXX There is also a bug in that static_dir and static_dir_gz don't use etag caching, but should

etags: dict[tuple[str, str, str], str] = {}


def route_static(filename, content_type):
    def static_filename(http):
        encoding = "none"
        mtime = os.stat(filename).st_mtime
        print(mtime)
        if "gzip" in http.request.headers.get("accept-encoding", ""):
            encoding = "gzip"
        if (
            "if-none-match" in http.request.headers
            and (filename, encoding, mtime) in etags
            and etags[(filename, encoding, mtime)]
            == http.request.headers["if-none-match"]
        ):
            http.response.status = "304 Not Modified"
            return
        if "gzip" in http.request.headers.get("accept-encoding", ""):
            http.response.headers["content-encoding"] = "gzip"
            tmp_filename = os.path.join(config_gzipped_dir, filename)
            os.makedirs(os.path.split(tmp_filename)[0], exist_ok=True)
            if (
                not os.path.exists(tmp_filename)
                or mtime > os.stat(tmp_filename).st_mtime
            ):
                with open(filename, "rb") as r:
                    with open(tmp_filename, "wb") as w:
                        data = gzip.compress(r.read())
                        w.write(data)
                http.response.body = data
            else:
                with open(tmp_filename, "rb") as r:
                    http.response.body = r.read()
        else:
            with open(filename, "rb") as r:
                http.response.body = r.read()
        if (filename, encoding, mtime) not in etags:
            etags[(filename, encoding, mtime)] = hashlib.md5(
                http.response.body
            ).hexdigest()
        http.response.headers["content-type"] = content_type
        http.response.headers["etag"] = etags[(filename, encoding, mtime)]

    return static_filename


def route_static_gz_dir(url, path, content_type, ext):
    "This is for a static directory of files of the same content type, where the content is alredy gzipped. No etag caching is done."

    def static_gz_dir_handler(http):
        print(path, http.request.path)
        assert http.request.path.endswith(ext)
        assert http.request.path.startswith(url)
        filename = path + urllib.parse.unquote(http.request.path[len(url) :])
        http.response.headers["content-type"] = content_type
        http.response.headers["content-encoding"] = "gzip"
        with open(filename, "rb") as fp:
            http.response.body = fp.read()
        http.response.headers["content-length"] = str(len(http.response.body))

    return static_gz_dir_handler


def route_static_dir(url, path, content_type, ext):
    "This is for a static directory of files of the same content type. No etag caching is done."

    def static_dir_handler(http):
        print(path, http.request.path)
        assert http.request.path.endswith(ext)
        assert http.request.path.startswith(url)
        filename = path + urllib.parse.unquote(http.request.path[len(url) :])
        http.response.headers["content-type"] = content_type
        with open(filename, "rb") as fp:
            http.response.body = fp.read()
        http.response.headers["content-length"] = str(len(http.response.body))

    return static_dir_handler


if __name__ == "__main__":
    """
    curl -v "${URL}/static/file"
    curl -v -H 'If-None-Match: bbe02f946d5455d74616fc9777557c22' "${URL}/static/file"
    curl -v -H 'Accept-Encoding: gzip' "${URL}/static/file" > ./tmp/file.gz
    curl -v -H 'Accept-Encoding: gzip' -H 'If-None-Match: 2e17f4f8cdfe3013ebffa6b4805b1764' "${URL}/static/file" > ./tmp/file.gz
    routes = {
        "/london/": static_gz_dir(
            "/london/", "static/london/", "application/x-protobuf", ".pbf"
        ),
        "/fonts/": static_dir("/fonts/", "static/fonts/", "application/x-protobuf", ".pbf"),
    }
    """
