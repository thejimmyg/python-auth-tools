if __name__ == "__main__":
    import sys

    from helper_hooks import helper_hooks_setup
    from helper_webhook_consumer import helper_webhook_consumer_verify_jwt

    hook_module_path = sys.argv[1]
    helper_hooks_setup(hook_module_path)

    print(
        helper_webhook_consumer_verify_jwt(
            sig=sys.argv[2], body=sys.argv[3].encode("utf8"), jwks_url=sys.argv[4]
        )
    )
