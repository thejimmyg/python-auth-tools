if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all()

    import sys

    from gevent.server import StreamServer

    import helper_hooks
    from config import config_host, config_port
    from serve_gevent import serve_gevent

    hook_module_path = sys.argv[1]
    helper_hooks.helper_hooks_setup(hook_module_path)

    server = StreamServer(
        (config_host, config_port),
        serve_gevent(helper_hooks.hooks["routes"]),
    )
    print(
        "Starting server on {host}:{port} using gevent".format(
            host=config_host, port=config_port
        )
    )
    server.serve_forever()
