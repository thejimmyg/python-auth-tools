import helper_hooks


def hello(http):
    http.response.body = "Hello, world"


helper_hooks.hooks = {"routes": {"/": hello}}
