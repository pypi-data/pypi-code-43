"""
Server configuration profiles
"""

from __future__ import annotations

from healer.config import CONFIG
from healer.persist.arkon import PersistSupport


class Config(object):
    """
    Flask application settings
    Note: use upper case names
    """

    SECRET_KEY = "secret-secret"

    # produce database on demand
    DATAMAKE = lambda : PersistSupport.cluster_database()

    BOOTSTRAP_SERVE_LOCAL = True  # see bootstrap-flask

    BLUEPRINT_PACKAGE_LIST = [
        'healer.station.server.area',
    ]

    BRYTHON_CONFIG = "{ debug:1, pythonpath:[ '/import' ] }"

    JWT_ACCESS_TOKEN_EXPIRES = int(CONFIG['station/server/token']['access_window'])
    JWT_REFRESH_TOKEN_EXPIRES = int(CONFIG['station/server/token']['refresh_window'])


class ProdConfig(Config):
    "prod"
    
    DEBUG = False
    DEVELOP = False
    TESTING = False


class DevsConfig(Config):
    ""

    DEBUG = True
    DEVELOP = True
    TESTING = False

    EXPLAIN_TEMPLATE_LOADING = True

    BLUEPRINT_PACKAGE_LIST = [
        'healer.station.server.area',
        'healer_test.station.server.area',
    ]


class TestConfig(Config):
    ""

    DEBUG = False
    DEVELOP = False
    TESTING = True

    BLUEPRINT_PACKAGE_LIST = [
        'healer.station.server.area',
        'healer_test.station.server.area',
    ]
