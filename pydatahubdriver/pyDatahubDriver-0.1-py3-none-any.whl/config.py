"""This module contains API configuration"""

import os

class ApiConfig(object):
    """
    This class configures KAPSARC Datahub api.
    The class contains fields:
    domain -- the host where Datahub API is going to connect
    api_key -- get the api_key by accessing your profile.
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ApiConfig, cls).__new__(cls)
            cls.instance.domain = os.environ['DATAHUB_HOST'] if 'DATAHUB_HOST' in os.environ else 'apps.kapsarc.com'
            cls.instance.api_key = None
        return cls.instance

    def __init__(self):
        self.domain = self.instance.domain
        self.api_key = self.instance.api_key