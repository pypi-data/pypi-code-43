import os
import sys
import re
import yaml
from upvest.tenancy import UpvestTenancyAPI
from upvest.clientele import UpvestClienteleAPI
from pathlib import Path
from upvest.__pkginfo__ import DEFAULT_USERAGENT

URL_RE = re.compile(r"^https?://.*$")


DEFAULT_CONFIG_LOCATIONS = (
    os.path.join(os.getcwd(), "upvest.yaml"),
    os.path.join(os.getcwd(), ".upvest.yaml"),
    os.path.join(str(Path.home()), "upvest.yaml"),
    os.path.join(str(Path.home()), ".upvest.yaml"),
)


def append_to_config_file():
    pass


class UpvestCLIConfig:
    def __init__(self, args):
        self.args = args
        self.config = self._load_config()
        # make sure we know where we're pointing
        self.endpoint_config = self.config.get("endpoints", {}).get(self.args.endpoint)
        if self.endpoint_config is None:
            if URL_RE.match(self.args.endpoint):
                self.base_url = self.args.endpoint
            else:
                print("The endpoint %s is not in the config file and does not appear to be a URL" % self.args.endpoint)
                sys.exit(1)
        else:
            self.base_url = self.endpoint_config.get("base_url")
            if self.base_url is None:
                print("The endpoint base_url must be set in the configuration file")
                sys.exit(1)

    def _load_config(self):
        configfile = self.args.configfile
        if not configfile:
            for trypath in DEFAULT_CONFIG_LOCATIONS:
                if os.path.exists(trypath):
                    configfile = trypath
                    break
            else:
                return {}

        return yaml.safe_load(open(configfile))

    def _get_api_cred(self, arg_name, conf_name, env_name, help_msg):
        # api key and oauth credential values are taken in order from
        # command line args, configuration files and finally environment variables
        # try: command line arg:
        value = getattr(self.args, arg_name)
        if value is None and self.endpoint_config is not None:
            # try from the configuration file
            value = self.endpoint_config.get(conf_name)
        if value is None:
            # now try an env var
            value = os.environ.get(env_name)
        if value is None:
            print(help_msg)
            sys.exit(1)
        return value

    def get_app_api(self):
        key = self._get_api_cred(
            "key",
            "api_key",
            "UPVEST_API_KEY",
            "The API key ID must be set via -K, in the config file, or the environment variable UPVEST_API_KEY",
        )
        secret = self._get_api_cred(
            "secret",
            "api_key_secret",
            "UPVEST_API_KEY_SECRET",
            "The API key secret must be set via -S, in the config file, or the environment variable UPVEST_API_KEY_SECRET",
        )
        passphrase = self._get_api_cred(
            "passphrase",
            "api_key_passphrase",
            "UPVEST_API_KEY_PASSPHRASE",
            "The API key ID must be set via -P, in the config file, or the environment variable UPVEST_API_KEY_PASSPHRASE",
        )
        user_agent = getattr(self.args, "user_agent", DEFAULT_USERAGENT)
        return UpvestTenancyAPI(key, secret, passphrase, user_agent=user_agent, base_url=self.base_url)

    def get_user_api(self, username=None, password=None):
        client_id = self._get_api_cred(
            "client_id",
            "oauth_client_id",
            "UPVEST_OAUTH_CLIENT_ID",
            "Set the OAuth client ID to authenticate as a user via --client-id, in the configuration file or the 'UPVEST_OAUTH_CLIENT_ID' environment variable",
        )
        client_secret = self._get_api_cred(
            "client_secret",
            "oauth_client_secret",
            "UPVEST_OAUTH_CLIENT_SECRET",
            "Set the OAuth client ID to authenticate as a user via --client-secret, in the configuration file or the 'UPVEST_OAUTH_CLIENT_SECRET' environment variable",
        )

        username = username or self.args.login
        password = password or self.args.password
        if username is None or password is None:
            print("Must set the user's --login [-l] and --password [-w]")
            sys.exit(1)

        user_agent = getattr(self.args, "user_agent", DEFAULT_USERAGENT)
        return UpvestClienteleAPI(
            client_id, client_secret, username, password, user_agent=user_agent, base_url=self.base_url
        )
