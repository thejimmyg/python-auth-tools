if __name__ == "__main__":
    import sys

    from helper_webhook_provider import helper_webhook_provider_sign_jwt

    print(helper_webhook_provider_sign_jwt(sys.argv[1], sys.argv[2]))
