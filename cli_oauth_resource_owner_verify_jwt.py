if __name__ == "__main__":
    import sys

    from helper_oauth_resource_owner import verify_jwt

    print(verify_jwt(sys.argv[1]))
