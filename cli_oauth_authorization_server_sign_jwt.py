if __name__ == "__main__":
    import sys

    from helper_oauth_authorization_server import sign_jwt

    print(
        sign_jwt(
            client_id=sys.argv[1],
            sub=sys.argv[2],
            scopes=sys.argv[3].split(" "),
            kid=sys.argv[4],
        )
    )
