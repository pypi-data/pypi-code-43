import json
import logging

from .broker_client import BrokerClient
from .service_executor import ServiceExecutor
from .economy import get_keys_and_wallet_id

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

class Agent():
    """Superclass for instantiating a Swarm service"""
    def __init__(self, **kwargs):
        self.description = self.new_description()
        if "keys_file" in kwargs.keys():
            self.keys_file = kwargs["keys_file"]
            self.keys = get_keys_and_wallet_id(self.keys_file)
            self.update_wallet_id(self.keys["walletId"])

    def new_description(self):
        return {"pricing": {}, "operations": [], "geolocation": {}}

    def setup_query(self, query):
        query["metadata"] = {
            "requester": {
                "@type": self.description["@type"],
                "@id": self.description["@id"],
                "pricing": {"walletId": self.description["pricing"]["walletId"]}
            }
        }
        return query

    def update_wallet_id(self, walletId):
        self.description["pricing"]["walletId"] = self.keys["walletId"]

    def discover(self, query):
        query = self.setup_query(query)
        return BrokerClient.discover(self.description, query)

    def get_executor(self, query):
        query = self.setup_query(query)
        return ServiceExecutor(self, query)

    def __repr__(self):
        return {
            "description": {
                "@id": self.description["@id"],
                "@type": self.description["@type"],
                "broker": self.description["broker"],
                "walletId": self.description["pricing"]["walletId"]
            }
        }

    def __str__(self):
        return str(self.__repr__())
