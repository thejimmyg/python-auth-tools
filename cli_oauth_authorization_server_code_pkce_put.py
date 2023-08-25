if __name__ == "__main__":
    import sys

    from helper_hooks import helper_hooks_setup
    from store_oauth_authorization_server_code_pkce import (
        CodePkce,
        store_oauth_authorization_server_code_pkce_put,
    )

    hook_module_path = sys.argv[1]
    helper_hooks_setup(hook_module_path)

    store_oauth_authorization_server_code_pkce_put(
        sys.argv[2],
        CodePkce(
            redirect_uri=sys.argv[3],
            scopes=[x.strip() for x in sys.argv[4].split(" ") if x.strip()],
        ),
    )
