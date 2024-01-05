if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all()

    import sys

    from gevent.server import StreamServer

    from config import config_host, config_port
    from serve_gevent import serve_gevent
    import importlib

    routes_module_path = sys.argv[1]
    routes_module = importlib.import_module(routes_module_path)
    routes = getattr(routes_module, "routes")

    server = StreamServer(
        (config_host, config_port),
        serve_gevent(routes),
    )
    print(
        "Starting server on {host}:{port} using gevent".format(
            host=config_host, port=config_port
        )
    )
    server.serve_forever()
