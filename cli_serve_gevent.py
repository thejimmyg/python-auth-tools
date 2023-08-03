if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all()

    from config import host, port
    from http_gevent import RespondEarly, StreamServer, server
    from route import routes

    server = StreamServer(
        (host, port),
        server(routes),
    )
    print("Starting echo server on {host}:{port}".format(host=host, port=port))
    server.serve_forever()
