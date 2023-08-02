from gevent import monkey

monkey.patch_all()

from http_gevent import StreamServer, server, RespondEarly
import traceback
from route import routes
from config import host, port


if __name__ == "__main__":
    server = StreamServer(
        (host, port),
        server(routes),
    )
    print("Starting echo server on {host}:{port}".format(host=host, port=port))
    server.serve_forever()
