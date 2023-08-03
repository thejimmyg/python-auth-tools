if __name__ == "__main__":
    from helper_crypto import verify_jwt
    import sys

    print(verify_jwt(sys.argv[1]))
