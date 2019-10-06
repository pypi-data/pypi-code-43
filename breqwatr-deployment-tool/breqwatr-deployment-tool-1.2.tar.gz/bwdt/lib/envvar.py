""" Central place to reference the environment variables used """
import os


def _env_get(env_name, default_val):
    """ Return an environment variable if defined else default value """
    if env_name in os.environ:
        return os.environ[env_name]
    return default_val


def env():
    """ Dictionary of environment variables or their default value """
    return {
        'auth_dir': _env_get('BWDT_AUTH_DIR', None),
        'region': _env_get('BWDT_REGION', 'ca-central-1'),
    }
