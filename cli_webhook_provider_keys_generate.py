if __name__ == "__main__":
    import sys

    from helper_hooks import helper_hooks_setup
    from helper_webhook_provider import (
        helper_webhook_provider_generate_keys_to_store_dir,
    )

    hook_module_path = sys.argv[1]
    helper_hooks_setup(hook_module_path)

    helper_webhook_provider_generate_keys_to_store_dir(sys.argv[2])
