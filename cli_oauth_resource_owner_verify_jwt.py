if __name__ == "__main__":
    import sys

    from helper_hooks import helper_hooks_setup
    from helper_oauth_resource_owner import helper_oauth_resource_owner_verify_jwt

    hook_module_path = sys.argv[1]
    helper_hooks_setup(hook_module_path)

    print(helper_oauth_resource_owner_verify_jwt(sys.argv[2]))
