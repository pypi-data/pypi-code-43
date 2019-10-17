import os
import sys
import logging

from auger.api.credentials import Credentials
from auger.api.cloud.rest_api import RestApi
from auger.api.utils.config_yaml import ConfigYaml

log = logging.getLogger("auger")


class Context(object):

    def __init__(self, name=''):
        super(Context, self).__init__()
        self.load_config()
        if name and len(name) > 0:
            self.name = "{:<9}".format('[%s]' % name)
        else:
            self.name = name
        self.debug = self.get_config('auger').get('debug', False)
        self.credentials = Credentials(self).load()
        self.rest_api = RestApi(
            self.credentials.api_url, self.credentials.token)

    def get_config(self, name):
        if isinstance(self.config, ConfigYaml):
            return self.config
        return self.config[name]

    def copy(self, name):
        new = Context(name)
        new.config = self.config
        return new

    def log(self, msg, *args, **kwargs):
        log.info('%s%s' %(self.name, msg), *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        log.debug('%s%s' %(self.name, msg), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        log.error('%s%s' %(self.name, msg), *args, **kwargs)

    def load_config(self, path=None):
        config = ConfigYaml()
        path = path if path else os.getcwd()
        name = os.path.abspath(os.path.join(path, 'auger.yaml'))
        if os.path.isfile(name):
            config.load_from_file(name)
        self.config = config
        return self.config

    @staticmethod
    def setup_logger(format='%(asctime)s %(name)s | %(message)s'):
        logging.basicConfig(
            stream=sys.stdout,
            datefmt='%H:%M:%S',
            format=format,
            level=logging.INFO)
