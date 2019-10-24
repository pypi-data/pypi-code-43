import configparser
from annofetch.lib.exception.config_error import ConfigError
import re
from pkg_resources import resource_filename
from io import StringIO

E_MAIL = ""
QUERY_PAUSE = 0.33 #default
LINES_TO_FILE = 50 #default

PATH_TO_FUN = 'fun2003-2014.tab'
PATH_TO_COGNAMES = 'cognames_function.tab'

class Config:

    def __init__(self):
        self.email = E_MAIL
        self.query_pause = QUERY_PAUSE
        self.lines_to_file = LINES_TO_FILE

    def read_config(self):
        config = configparser.ConfigParser()

        try:
            config_path = resource_filename(__name__, 'config.ini')
            config.read(config_path)
        except Exception as ex:
            raise ConfigError("*** Config File is broken. *** \n" + str(ex))

        try:
            self.email = config['ncbi']['email']
            self.query_pause = float(config['other']['query_pause'])
            self.lines_to_file = int(config['other']['lines_to_file'])
        except:
            raise ConfigError("***Couln't parse all config entries.***")

    def check_email(self, email = None):
        if not email:
            email = self.email
        email_pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
        match = re.fullmatch(email_pattern, email)
        if match:
            return True
        else:
            return False

    def set_email(self, email):
        if not self.check_email(email):
            return False
        self.email = email
        self.write_config()
        return True

    def write_config(self):
        config = configparser.ConfigParser()
        config['ncbi'] = {}
        config['ncbi']['email'] = str(self.email)
        config['other'] = {}
        config['other']['query_pause'] = str(self.query_pause)
        config['other']['lines_to_file'] = str(self.lines_to_file)

        try:
            config_path = resource_filename(__name__, 'config.ini')
            with open(config_path, 'w') as configfile:
                config.write(configfile)
        except Exception as err:
            raise ConfigError("***Unable to write config file*** \n" + str(err))
