"""
Utility and helper methods.

## Configuration
Configuration variables can be set explicitly, with environment variables, or with a configuration file stored at `$HOME/.oaas/sdk.json`. If more than one of
these methods is used, explicitly set values override environment variables, and environment variables override a config file.

An example configuration file looks like this:

```json
{
  "webservice_root": "https://api.oaas.mycompany.com",
  "user": "an_oaas_user",
  "password": "an_oaas_users_password"
}
```

Environment variable names are `OAAS_` followed by the config keys in all caps. Environment variables override anything stored in `$HOME/.oaas/sdk.json`. Example:

```bash
export OAAS_WEBSERVICE_ROOT="https://api.oaas.mycompany.com"
export OAAS_USER="an_oaas_user"
export OAAS_PASSWORD="an_oaas_users_password"
```

Additionally, configuration parameters may be specified explicitly:

```python
from oaas_sdk.util import configuration
configuration.webservice_root = "https://api.oaas.mycompany.com"
configuration.user = "an_oaas_user"
configuration.password = "an_oaas_users_password"
```

If any value is not specified before use, an exception will be raised.
"""
import os
import warnings
import logging

from oaas_sdk.objects import ConfigurationException

# we use ujson if available
try:
    import ujson as json
except ImportError:
    import json

# constants
_WEBSERVICE_ROOT = 'webservice_root'
_USER = 'user'
_PASSWORD = 'password'
UPDATE_FREQUENCY = 5
"""Frequency with which SDK will query the webservice for updated values."""
MAX_DOCUMENTS = 10000000
"""Maximum number of documents which OaaS will accept in a single labeling task."""


class _Configuration:
    """
    Configuration as specified in user's local config file at `$HOME/.oaas/sdk.json`, set in environment variables, or entered by setting values
    """

    __SDK_CONFIG_FILE_LOCATION = "~/.oaas/sdk.json"

    @staticmethod
    def _env(param: str):
        """Environment variable form of a parameter"""
        return 'OAAS_{}'.format(param.upper())

    def __init__(self):
        """
        Read environment variables and configuration file and store any provided values in object for easy retrieval. Env variables take priority.
        """

        self._webservice_root = None
        self._user = None
        self._password = None

        # get from env variables first

        if self._env(_WEBSERVICE_ROOT) in os.environ:
            logging.info("Reading {} from environment variable".format(_WEBSERVICE_ROOT))
            self.webservice_root = os.environ[self._env(_WEBSERVICE_ROOT)]

        if self._env(_USER) in os.environ:
            logging.info("Reading {} from environment variable".format(_USER))
            self.user = os.environ[self._env(_USER)]

        if self._env(_PASSWORD) in os.environ:
            logging.info("Reading {} from environment variable".format(_PASSWORD))
            self.password = os.environ[self._env(_PASSWORD)]

        if self._webservice_root and self._user and self._password:
            return

        # get from config file next

        absolute_config_file_path = os.path.abspath(os.path.expanduser(self.__class__.__SDK_CONFIG_FILE_LOCATION))
        if not os.path.exists(absolute_config_file_path):
            return

        try:
            with open(absolute_config_file_path, 'r') as config_file:
                config_json = config_file.read()
                config_dict = json.loads(config_json)
        except:
            logging.warning("Malformed or unreadable sdk.json file", exc_info = True)
            return

        if not self._webservice_root and _WEBSERVICE_ROOT in config_dict:
            logging.info("Reading {} from sdk.json".format(_WEBSERVICE_ROOT))
            self.webservice_root = config_dict[_WEBSERVICE_ROOT]

        if not self._user and _USER in config_dict:
            logging.info("Reading {} from sdk.json".format(_USER))
            self.user = config_dict[_USER]

        if not self._password and _PASSWORD in config_dict:
            logging.info("Reading {} from sdk.json".format(_PASSWORD))
            self.password = config_dict[_PASSWORD]

    @property
    def webservice_root(self):
        if not self._webservice_root:
            raise ConfigurationException("{} not found in sdk.json or environment variables, and not manually specified. "
                                         "See https://docs.oaas.mscience.com/sdk/util.html for details.".format(_WEBSERVICE_ROOT))
        return self._webservice_root

    @webservice_root.setter
    def webservice_root(self, value: str):
        self._webservice_root = value

    @property
    def user(self):
        if not self._user:
            raise ConfigurationException("{} not found in sdk.json or environment variables, and not manually specified. "
                                         "See https://docs.oaas.mscience.com/sdk/util.html for details.".format(_USER))
        return self._user

    @user.setter
    def user(self, value: str):
        self._user = value

    @property
    def password(self):
        if not self._password:
            raise ConfigurationException("{} not found in sdk.json or environment variables, and not manually specified. "
                                         "See https://docs.oaas.mscience.com/sdk/util.html for details.".format(_PASSWORD))
        return self._password

    @password.setter
    def password(self, value: str):
        self._password = value


configuration = _Configuration()
"""
Singleton configuration; this is the variable the SDK imports and uses. This is also the variable to set override values on.
"""
