import pytest 
from smart_utils.logging import LoggerConstructor
from smart_utils.logging.config import ConfigGetter


class ConfigGetterTest(ConfigGetter):
    
    def __init__(self,yml,sentry_dsn):
        self.yml = yml
        self.sentry_dsn = sentry_dsn

    def get_config(self):
        return self.yml, self.sentry_dsn


def test_init(yml,sentry_dsn):

    Logger = LoggerConstructor(ConfigGetterTest(yml,sentry_dsn),"test")
    assert Logger.environment == "test"
    assert isinstance(Logger.getter,ConfigGetter)

def test_activate_sentry_error(yml,sentry_dsn):
        
    Logger = LoggerConstructor(ConfigGetterTest(yml,sentry_dsn),"test")
    assert Logger._activate_sentry(sentry_dsn) == False

def test_generate_logger_loaded(yml,sentry_dsn):

    Logger = LoggerConstructor(ConfigGetterTest(yml,sentry_dsn),"test")
    assert Logger.generate_logger().name == 'main'

def test_generate_logger_error(yml_error,sentry_dsn):
    
    Logger = LoggerConstructor(ConfigGetterTest(yml_error,sentry_dsn),"test")
    assert Logger.generate_logger().name == 'root'

def test_generate_logger_yml_none(yml_none,sentry_dsn):
    
    Logger = LoggerConstructor(ConfigGetterTest(yml_none,sentry_dsn),"test")
    assert Logger.generate_logger().name == 'root'