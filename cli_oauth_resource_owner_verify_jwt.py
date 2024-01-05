if __name__ == "__main__":
    import sys

    from helper_oauth_resource_owner import helper_oauth_resource_owner_verify_jwt

    print(helper_oauth_resource_owner_verify_jwt(sys.argv[1]))
