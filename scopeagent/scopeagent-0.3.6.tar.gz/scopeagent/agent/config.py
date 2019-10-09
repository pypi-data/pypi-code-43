import json
import logging
from os.path import expanduser
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


SCOPE_CONFIG_PATH = expanduser("~/.scope/config.json")
logger = logging.getLogger(__name__)


def load_config_file(path=None):
    """Attempts to read the API endpoint and API key from the native Scope app configuration file."""
    path = path or SCOPE_CONFIG_PATH
    try:
        with open(str(path), 'r') as config_file:
            config = json.load(config_file)
            try:
                profile = config['profiles'][config['currentProfile']]
                logger.debug("autodetected config profile: %s", profile)
                return profile
            except KeyError:
                raise Exception("Invalid format in Scope configuration file at %s" % path)
    except FileNotFoundError:
        return {}
