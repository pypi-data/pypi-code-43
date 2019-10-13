from ehelply_bootstrapper.drivers.fast_api import Fastapi
from ehelply_bootstrapper.drivers.mongo import Mongo
from ehelply_bootstrapper.drivers.redis import Redis
from ehelply_bootstrapper.drivers.mysql import Mysql
from ehelply_bootstrapper.drivers.socketio import Socketio
from ehelply_bootstrapper.drivers.aws import AWS
from ehelply_logger.Logger import Logger
from ehelply_bootstrapper.integrations.integration import IntegrationManager


class State:
    """
    A state class used to hold globally accessible values across the application
    It can be extended or modified as needed.

    ...

    Attributes
    ----------
    app
        Holds the application instance when applicable. Some services will make use of this, others will not.
    config
        Holds the pyyml configuration object for accessing config across the app. All services should be using this.
    sockets
        Holds the socket application. This will only be used in some services.
    mongo
        Holds the mongo DB object
    redis
        Holds the redis DB object
    """

    app: Fastapi = None
    config = None
    logger: Logger = None
    sockets: Socketio = None
    mongo: Mongo = None
    redis: Redis = None
    mysql: Mysql = None
    aws: AWS = None
    integrations: IntegrationManager = None
    services: dict = {}

    @staticmethod
    def service(name: str):
        if name in State.services:
            return State.services[name]
        else:
            return None
