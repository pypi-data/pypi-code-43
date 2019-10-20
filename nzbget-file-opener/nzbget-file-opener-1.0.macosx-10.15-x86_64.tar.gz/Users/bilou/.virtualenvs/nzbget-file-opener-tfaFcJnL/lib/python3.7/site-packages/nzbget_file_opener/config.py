import os
from configparser import ConfigParser
from urllib.parse import urlparse


class AppConfig:

    nzbgetrc = os.path.expanduser('~/.nzbgetrc')

    def __init__(self):
        """ This class holds the configuration data in order to run the app """
        self.scheme = 'http://'
        self.hostname = 'localhost'
        self.port = 6789
        self.username = None
        self.password = None

    @property
    def credentials(self):
        """ Returns the credentials string based on current state """
        return f'{self.username}:{self.password}@' if self.username and self.password else ''

    @property
    def host(self):
        """ Returns the credentials string based on current state """
        return f'{self.hostname}:{self.port}'

    @property
    def url(self):
        """ Returns the credentials string based on current state """
        return f'{self.scheme}{self.credentials}{self.host}'

    def reset(self):
        """ Reset the properties to their default state """
        self.__init__()

    def load(self, args=None):
        """ Builds the AppConfig instance """
        try:
            if args and (args.config or (args.username and args.password)):
                print(f'Configuration read from {args.config}')
                self.read_args(args)
            elif os.path.exists(self.nzbgetrc):
                print(f'Configuration read from {self.nzbgetrc}')
                self.read_file(self.nzbgetrc)
            else:
                print(f'Configuration read from environment')
                self.read_env()
        except ValueError as e:
            print(e)
            exit(1)

    def read_url(self, url):
        """ Reads an url and extract variables from it """
        parts = url.split(':')
        u = urlparse(url)
        self.scheme = u.scheme + '://' if u.scheme else 'http://'
        self.hostname = u.hostname if u.hostname else parts[0]
        try:
            self.port = u.port if u.port else int(parts[1])
        except (ValueError, IndexError):
            self.port = 6789

    def read_env(self):
        """ Reads the environment and extract variables from it """
        if 'NZBGET_URL' in os.environ:
            self.read_url(os.environ['NZBGET_URL'])
        if 'NZBGET_USERNAME' in os.environ:
            self.username = os.environ['NZBGET_USERNAME']
        if 'NZBGET_PASSWORD' in os.environ:
            self.password = os.environ['NZBGET_PASSWORD']

    def read_file(self, filepath, section=None):
        """
        Reads a config file and extract variables from it using ConfigParser.
        If not section is specified, the first one will be used
        """
        config = ConfigParser()
        config.read(filepath)
        available_sections = config.sections()
        if not available_sections:
            raise ValueError(f'\'{filepath}\' is empty or badly formatted')
        if section and section not in available_sections:
            raise ValueError(f'section \'{section}\' does not exist in \'{filepath}\'')
        section = section if section else available_sections[0]
        self.reset()
        self.hostname = section
        if 'port' in config[section]:
            self.port = config[section]['port']
        if 'username' in config[section]:
            self.username = config[section]['username']
        if 'password' in config[section]:
            self.password = config[section]['password']

    def read_args(self, args):
        """ Reads the input arguments and extract variables from it """
        if args.config:
            self.read_file(args.config, args.domain)
        if args.hostname:
            self.read_url(args.hostname)
        if args.username:
            self.username = args.username
            self.password = args.password
