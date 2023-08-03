import gzip
import hashlib
import os

etags: dict[tuple[str, str], str] = {}


def static(filename, content_type):
    def static_filename(http):
        encoding = "none"
        if "gzip" in http.request.headers.get("accept-encoding", ""):
            encoding = "gzip"
        if (
            "if-none-match" in http.request.headers
            and (filename, encoding) in etags
            and etags[(filename, encoding)] == http.request.headers["if-none-match"]
        ):
            http.response.status = "304 Not Modified"
            return
        if "gzip" in http.request.headers.get("accept-encoding", ""):
            http.response.headers["content-encoding"] = "gzip"
            tmp_filename = os.path.join(gzipped_dir, filename)
            os.makedirs(os.path.split(tmp_filename)[0], exist_ok=True)
            if not os.path.exists(tmp_filename):
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
        if (filename, encoding) not in etags:
            etags[(filename, encoding)] = hashlib.md5(http.response.body).hexdigest()
        http.response.headers["content-type"] = content_type
        http.response.headers["etag"] = etags[(filename, encoding)]

    return static_filename


if __name__ == "__main__":
    """
    curl -v "${URL}/static/file"
    curl -v -H 'If-None-Match: bbe02f946d5455d74616fc9777557c22' "${URL}/static/file"
    curl -v -H 'Accept-Encoding: gzip' "${URL}/static/file" > ./tmp/file.gz
    curl -v -H 'Accept-Encoding: gzip' -H 'If-None-Match: 2e17f4f8cdfe3013ebffa6b4805b1764' "${URL}/static/file" > ./tmp/file.gz
    """
