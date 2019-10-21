from ehelply_bootstrapper.drivers.driver import Driver
from pymongo import MongoClient


class Mongo(Driver):
    def setup(self):
        from ehelply_bootstrapper.utils.state import State
        self.instance = MongoClient(host=State.config.bootstrap.mongo.host,
                                    port=State.config.bootstrap.mongo.port,
                                    username=State.config.bootstrap.mongo.username,
                                    password=State.config.bootstrap.mongo.password,
                                    authSource=State.config.bootstrap.mongo.authsource)

