if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all()

    import sys

    from gevent.server import StreamServer

    import plugins
    from config_common import host, port
    from helper_plugins import setup_plugins
    from serve_gevent import server

    plugin_module_path = sys.argv[1]
    setup_plugins(plugin_module_path)

    server = StreamServer(
        (host, port),
        server(plugins.routes),
    )
    print("Starting echo server on {host}:{port}".format(host=host, port=port))
    server.serve_forever()
