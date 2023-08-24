if __name__ == "__main__":
    import sys

    from helper_plugins import setup_plugins
    from store_oauth_authorization_server_current_key import put_current_kid_value

    plugin_module_path = sys.argv[1]
    setup_plugins(plugin_module_path)

    put_current_kid_value(sys.argv[2])
