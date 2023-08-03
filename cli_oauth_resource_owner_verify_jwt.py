if __name__ == "__main__":
    import sys

    from helper_crypto import verify_jwt

    print(verify_jwt(sys.argv[1]))
