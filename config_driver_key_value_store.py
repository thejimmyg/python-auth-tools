import os

from config import config_store_dir

config_driver_key_value_store_dir = os.path.join(
    config_store_dir, "driver_key_value_store"
)
os.makedirs(config_driver_key_value_store_dir, exist_ok=True)
config_driver_key_value_store_db_path = os.path.join(
    config_driver_key_value_store_dir, "sqlite.db"
)
