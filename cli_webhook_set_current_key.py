if __name__ == "__main__":
    import sys

    from helper_hooks import setup_hooks
    from store_webhook_server_current_key import put_current_kid_value

    hook_module_path = sys.argv[1]
    setup_hooks(hook_module_path)

    put_current_kid_value(sys.argv[2])
