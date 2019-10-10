import os

import toml


class Config(object):
    """Configuration helper."""

    _instance = None

    @classmethod
    def init(cls):
        """Initialize the configuration.

        If the config file contains a dictionary keyed by ``env``, all its
        content will be set as environment variables.

        This function should not be called externally. The ``Config.get``
        function lazily initializes the config object automatically.
        """
        dqenv = os.getenv('DQENV') or 'local'
        with open('config/{}.toml'.format(dqenv)) as conffile:
            cls._instance = toml.loads(conffile.read())
            env = cls._instance.get('env')
            if isinstance(env, dict):
                for key, value in env.items():
                    os.environ[key] = value

    @classmethod
    def get(cls, key):
        """Get the config value specified by the provided key.

        TOML config files should be stored in the config folder, and the
        environment (i.e. which file to choose) should be specified by the
        ``DQENV`` environment variable.

        :param string key: The key to retrieve the value for. Nested key should
            have its components separated by dot, such as ``owner.email``.
        :returns: The value of the key if it exists, and ``None`` otherwise.
        """
        if cls._instance is None:
            cls.init()

        parts = key.split('.')
        cfg = cls._instance
        for part in parts:
            cfg = cfg.get(part)
            if cfg is None:
                return None

        return cfg
