"""Class: Config"""
import os
from pathlib import Path
import shelve

class Config():
    """manage interaction with mdk config files"""

    def __init__(self):
        config_dir_path = Path.home()/".config/mdk"
        if not config_dir_path.exists():
            config_dir_path.mkdir(parents=True)
            os.chown(
                config_dir_path,
                int(os.environ.get('UID', 1000)),
                int(os.environ.get('GID', 999)),
            )

        if not self.host_shared_path.exists():
            self.host_shared_path.mkdir(parents=True)
            os.chown(
                self.host_shared_path,
                int(os.environ.get('UID', 1000)),
                int(os.environ.get('GID', 999)),
            )


    def __getattr__(self, name):
        """get val of key from persistent storage"""
        data_store = shelve.open(str(Path.home()/".config/mdk/config.mdk"))
        config_defaults = {
            "dev_mode": True,
            "dev_compose_extension": "dev",
            "host_shared_path": Path.home()/"mdkshared",
            "target_shared_path": "/mdkshared",
        }

        # when pulling value, use data store > default > None
        val = data_store.get(
            name,
            config_defaults.get(
                name,
                None,
            )
        )

        data_store.close()
        return val


    def __setattr__(self, name, value):
        """set key:val in persistent storage"""
        data_store = shelve.open(str(Path.home()/".config/mdk/config.mdk"))
        data_store[name] = value
        data_store.close()
