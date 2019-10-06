# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import os
import configparser
import urllib.parse
import logging

__all__ = ['config', 'get_hostname', 'get_port', 'split_netloc',
    'parse_listen', 'parse_uri']
logger = logging.getLogger(__name__)


def get_hostname(netloc):
    if '[' in netloc and ']' in netloc:
        return netloc.split(']')[0][1:]
    elif ':' in netloc:
        return netloc.split(':')[0]
    else:
        return netloc


def get_port(netloc):
    netloc = netloc.split(']')[-1]
    return int(netloc.split(':')[1])


def split_netloc(netloc):
    return get_hostname(netloc).replace('*', ''), get_port(netloc)


def parse_listen(value):
    for netloc in value.split(','):
        yield split_netloc(netloc)


def parse_uri(uri):
    return urllib.parse.urlparse(uri)


class TrytonConfigParser(configparser.RawConfigParser):

    def __init__(self):
        configparser.RawConfigParser.__init__(self)
        self.add_section('web')
        self.set('web', 'listen', 'localhost:8000')
        self.set('web', 'root', os.path.join(os.path.expanduser('~'), 'www'))
        self.add_section('database')
        self.set('database', 'uri',
            os.environ.get('TRYTOND_DATABASE_URI', 'sqlite://'))
        self.set('database', 'path', os.path.join(
                os.path.expanduser('~'), 'db'))
        self.set('database', 'list', 'True')
        self.set('database', 'retry', 5)
        self.set('database', 'language', 'en')
        self.add_section('cache')
        self.set('cache', 'model', 200)
        self.set('cache', 'record', 2000)
        self.set('cache', 'field', 100)
        self.add_section('ssl')
        self.add_section('email')
        self.set('email', 'uri', 'smtp://localhost:25')
        self.add_section('session')
        self.set('session', 'authentications', 'password')
        self.set('session', 'timeout', 600)
        self.set('session', 'max_attempt', 5)
        self.add_section('password')
        self.set('password', 'length', 8)
        self.set('password', 'entropy', 0.75)
        self.add_section('report')
        self.set('report', 'unoconv',
            'pipe,name=trytond;urp;StarOffice.ComponentContext')
        self.update_etc()

    def update_etc(self, configfile=os.environ.get('TRYTOND_CONFIG')):
        if isinstance(configfile, str):
            configfile = [configfile]
        if not configfile or not [_f for _f in configfile if _f]:
            return
        read_files = self.read(configfile)
        logger.info('using %s as configuration files', ', '.join(read_files))

    def get(self, section, option, *args, **kwargs):
        default = kwargs.pop('default', None)
        try:
            return configparser.RawConfigParser.get(self, section, option,
                *args, **kwargs)
        except (configparser.NoOptionError, configparser.NoSectionError):
            return default

    def getint(self, section, option, *args, **kwargs):
        default = kwargs.pop('default', None)
        try:
            return configparser.RawConfigParser.getint(self, section, option,
                *args, **kwargs)
        except (configparser.NoOptionError, configparser.NoSectionError,
                TypeError):
            return default

    def getfloat(self, section, option, *args, **kwargs):
        default = kwargs.pop('default', None)
        try:
            return configparser.RawConfigParser.getfloat(self, section, option,
                *args, **kwargs)
        except (configparser.NoOptionError, configparser.NoSectionError,
                TypeError):
            return default

    def getboolean(self, section, option, *args, **kwargs):
        default = kwargs.pop('default', None)
        try:
            return configparser.RawConfigParser.getboolean(
                self, section, option, *args, **kwargs)
        except (configparser.NoOptionError, configparser.NoSectionError,
                AttributeError):
            return default

config = TrytonConfigParser()
