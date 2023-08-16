if __name__ == "__main__":
    import sys

    from helper_oauth_authorization_server import generate_keys_to_store_dir

    generate_keys_to_store_dir(sys.argv[1])
