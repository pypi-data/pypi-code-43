# -*- coding: utf-8 -*-

import os


class BaseConfig(object):
    DEBUG = False
    TESTING = False
    AWS_ENDPOINT_URL = os.getenv('AWS_ENDPOINT_URL')
    CELERY_BROKER = os.getenv('BROKER_URL')
    CELERY_RESULT_BACKEND = os.getenv('RESULT_BACKEND_URL')

    WAVES_CLI_NAME = os.getenv('WAVES_CLI_NAME', 'waves')
    CELERY_QUEUE_NAME = os.getenv('QUEUE_NAME', 'waves_latest')


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    pass


def get_config(env='prod'):

    if env in ['development', 'dev']:
        return DevelopmentConfig()

    return ProductionConfig()
