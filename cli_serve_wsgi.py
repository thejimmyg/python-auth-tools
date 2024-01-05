if __name__ == "__main__":
    import sys
    from socketserver import ThreadingMixIn
    from wsgiref.simple_server import WSGIServer, make_server
    import importlib

    class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
        # This doesn't correctly set wsgi.multithread, but I can't find an easy way to fix that. Other servers will behave better.
        pass

    from config import config_host, config_port
    from serve_wsgi import serve_wsgi

    routes_module_path = sys.argv[1]
    routes_module = importlib.import_module(routes_module_path)
    routes = getattr(routes_module, "routes")

    with make_server(
        config_host,
        config_port,
        serve_wsgi(routes, debug=False),
        ThreadingWSGIServer,
    ) as server:
        print(
            "Starting server on {host}:{port} using a threaded WSGI server".format(
                host=config_host, port=config_port
            )
        )
        server.serve_forever()
