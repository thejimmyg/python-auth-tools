if __name__ == "__main__":
    import sys

    from helper_hooks import helper_hooks_setup
    from helper_webhook_provider import helper_webhook_provider_sign_jwt

    hook_module_path = sys.argv[1]
    helper_hooks_setup(hook_module_path)

    print(helper_webhook_provider_sign_jwt(sys.argv[2], sys.argv[3]))
