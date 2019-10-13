import logging
from .agent import Agent
from .service import find_my_ip

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

class Consumer(Agent):
    def __init__(self, **kwargs):
        logging.info("Initializing consumer with args: %s" % kwargs)
        super().__init__(**kwargs)
        self.description["@type"] = "swarm:Consumer"
        self.description["@id"] = find_my_ip()
        self.description["broker"] = "http://localhost:4000/broker"
        self.description["pricing"] = {"walletId": self.keys["walletId"]}

    def __repr__(self):
        return super().__repr__()
