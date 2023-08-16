if __name__ == "__main__":
    import sys

    from store_webhook_server_keys import put_current_kid_value

    put_current_kid_value(sys.argv[1])
