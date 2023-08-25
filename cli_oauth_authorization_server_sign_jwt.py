if __name__ == "__main__":
    import sys

    from helper_hooks import helper_hooks_setup
    from helper_oauth_authorization_server import (
        helper_oauth_authorization_server_sign_jwt,
    )

    hook_module_path = sys.argv[1]
    helper_hooks_setup(hook_module_path)

    print(
        helper_oauth_authorization_server_sign_jwt(
            client_id=sys.argv[2],
            sub=sys.argv[3],
            scopes=sys.argv[4].split(" "),
            kid=sys.argv[5],
        )
    )
