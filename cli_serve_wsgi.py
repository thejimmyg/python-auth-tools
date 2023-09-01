if __name__ == "__main__":
    import sys
    from socketserver import ThreadingMixIn
    from wsgiref.simple_server import WSGIServer, make_server

    class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
        # This doesn't correctly set wsgi.multithread, but I can't find an easy way to fix that. Other servers will behave better.
        pass

    import helper_hooks
    from config import config_host, config_port
    from serve_wsgi import serve_wsgi

    hook_module_path = sys.argv[1]
    helper_hooks.helper_hooks_setup(hook_module_path)

    with make_server(
        config_host,
        config_port,
        serve_wsgi(helper_hooks.hooks["routes"], debug=False),
        ThreadingWSGIServer,
    ) as server:
        print(
            "Starting server on {host}:{port} using a threaded WSGI server".format(
                host=config_host, port=config_port
            )
        )
        server.serve_forever()
