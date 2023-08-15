if __name__ == "__main__":
    import sys

    from helper_webhook import sign_jwt

    print(sign_jwt(sys.argv[1]))
