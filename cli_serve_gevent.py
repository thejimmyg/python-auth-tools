if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all()

    import sys

    from gevent.server import StreamServer

    import helper_hooks
    from config_common import host, port
    from serve_gevent import server

    hook_module_path = sys.argv[1]
    helper_hooks.setup_hooks(hook_module_path)

    server = StreamServer(
        (host, port),
        server(helper_hooks.hooks["routes"]),
    )
    print("Starting echo server on {host}:{port}".format(host=host, port=port))
    server.serve_forever()
