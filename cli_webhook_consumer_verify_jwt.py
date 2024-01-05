if __name__ == "__main__":
    import sys

    from helper_webhook_consumer import helper_webhook_consumer_verify_jwt

    print(
        helper_webhook_consumer_verify_jwt(
            sig=sys.argv[1], body=sys.argv[2].encode("utf8"), jwks_url=sys.argv[3]
        )
    )
