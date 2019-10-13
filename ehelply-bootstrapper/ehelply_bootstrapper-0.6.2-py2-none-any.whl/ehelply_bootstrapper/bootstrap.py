import sys
from typing import List
from pathlib import Path

from ehelply_bootstrapper.drivers.config import Config
from ehelply_bootstrapper.drivers.fast_api import Fastapi
from ehelply_bootstrapper.drivers.mongo import Mongo
from ehelply_bootstrapper.drivers.redis import Redis
from ehelply_bootstrapper.drivers.mysql import Mysql, MySQLCredentials
from ehelply_bootstrapper.drivers.sentry import Sentry
from ehelply_bootstrapper.drivers.socketio import Socketio
from ehelply_bootstrapper.drivers.aws import AWS
from ehelply_bootstrapper.utils.state import State
from ehelply_bootstrapper.utils.secret import SecretManager
from ehelply_bootstrapper.integrations.integration import IntegrationManager, Integration

from ehelply_logger.Logger import Logger

LOADABLE_FASTAPI = "fastapi"
LOADABLE_MONGO = "mongo"
LOADABLE_MYSQL = "mysql"
LOADABLE_REDIS = "redis"
LOADABLE_SENTRY = "sentry"
LOADABLE_SOCKET = "socket"
LOADABLE_AWS = "aws"


class Bootstrap:
    """
    Bootstrap class gets a service ready to be loaded

    This class SHOULD be overridden to ensure maximum control
    """

    def __init__(
            self,
            service_name: str,
            service_key: str,
            service_version: str,
            loadables: List[str],
            stage: str,
            config_path: str = None,
            configs: List[str] = None,
            dev_mode: bool = False,
            debug_mode: int = 0
    ):
        self.service_name: str = service_name
        self.service_key: str = service_key
        self.config_path: str = config_path
        self.dev_mode: bool = dev_mode
        self.loadables: List[str] = loadables
        self.service_version: str = service_version
        self.debug_mode = debug_mode

        # Applications and clients
        self.fastapi_driver: Fastapi = None
        self.socket_driver: Socketio = None
        self.redis_driver: Redis = None
        self.mysql_driver: Mysql = None
        self.mongo_driver: Mongo = None
        self.aws_driver: AWS = None

        if len(sys.argv) > 1 and "--dev" in sys.argv:
            self.dev_mode = True

        if self.config_path is None:
            self.config_path = str(Path(__file__).parents[1]) + "/config"

        self.logger: Logger = Logger(debug_mode=self.debug_mode)
        State.logger = self.logger

        self.logger.info(
            "Starting loading procedure for `" + self.service_name + "` with key `" + self.service_key + "`")
        self.logger.info(" * Dev mode (DEPRECATED): " + str(self.dev_mode))
        self.logger.info(" * Stage: " + str(stage))
        self.logger.info(" * Debug mode: " + str(self.debug_mode))
        self.logger.info(" * Configuration path: " + str(self.config_path))
        self.logger.info(" * Loading configs: " + str(configs))
        self.logger.info(" * Loading drivers: " + str(self.loadables))

        self.check_loadables_conflicts()
        self.logger.debug("Confliction test passed")

        self.check_loadables_improvements()

        self.logger.info("Pre loading...")
        self.pre_load()

        self.logger.info("Loading configuration...")
        Config(config_path=self.config_path, configs=configs).init()

        self.logger.info("Loading secret manager...")
        State.secrets = SecretManager()

        self.logger.info("Loading services...")

        if LOADABLE_SENTRY in self.loadables:
            self.logger.info("Loading sentry...")
            self.sentry_init()

        if LOADABLE_MYSQL in self.loadables:
            self.logger.info("Loading mysql...")
            self.mysql_init()
            State.mysql = self.mysql_driver

        if LOADABLE_FASTAPI in self.loadables:
            self.logger.info("Loading fast api...")
            self.fastapi_init()
            self.logger.debug("Registering middleware to fast api...")
            self.fastapi_middleware()
            self.logger.debug("Registering routers to fast api...")
            self.fastapi_routers()
            State.app = self.fastapi_driver

        if LOADABLE_SOCKET in self.loadables:
            self.logger.info("Loading socket io...")
            self.socket_init()
            State.sockets = self.socket_driver

        if LOADABLE_REDIS in self.loadables:
            self.logger.info("Loading redis...")
            self.redis_init()
            State.redis = self.redis_driver

        if LOADABLE_MONGO in self.loadables:
            self.logger.info("Loading mongo...")
            self.mongo_init()
            State.mongo = self.mongo_driver

        if LOADABLE_AWS in self.loadables:
            self.logger.info("Loading AWS...")
            self.aws_init()
            State.aws = self.aws_driver

        if LOADABLE_FASTAPI in self.loadables:
            self.logger.debug("Registering additional endpoints to fast api...")
            self.fastapi_register_endpoints()

        if LOADABLE_SOCKET in self.loadables:
            self.logger.debug("Registering additional events to socket io...")
            self.socket_register_events()

        self.logger.info("Loading integrations...")
        State.integrations = IntegrationManager(self.fastapi_driver.instance)
        self.register_integrations()
        State.integrations.load()

        self.logger.info("Ready")

        self.logger.debug("Running post load...")
        self.post_load()

        if (LOADABLE_FASTAPI in self.loadables) and self.dev_mode:
            self.logger.info("Starting fastapi dev server with uvicorn")
            self.fastapi_driver.run_dev_server()

    def check_loadables_conflicts(self):
        if LOADABLE_SOCKET in self.loadables and LOADABLE_FASTAPI not in self.loadables:
            raise Exception("Cannot use sockets without fastapi.")

    def check_loadables_improvements(self):
        if LOADABLE_SENTRY not in self.loadables:
            self.logger.warning(
                "You're not using sentry. Consider using sentry to improve error catching and debugging.")

    def pre_load(self):
        pass

    def post_load(self):
        pass

    def fastapi_init(self):
        """
        Create the fast api app object
        :return:
        """
        self.fastapi_driver = Fastapi(service_name=self.service_name, service_version=self.service_version,
                                      dev_mode=self.dev_mode).init()

    def fastapi_middleware(self):
        """
        Inject middleware into fast api
        :return:
        """
        # Cors
        self.fastapi_driver.cors(origins=['*'], allow_credentials=True)

        # Zipping Responses
        self.fastapi_driver.compression(min_size=500)

        if LOADABLE_SENTRY in self.loadables:
            self.fastapi_driver.sentry()

        if LOADABLE_MYSQL in self.loadables:
            self.mysql_driver.inject_fastapi_middleware(self.fastapi_driver.instance)

    def fastapi_routers(self):
        """
        Register routers to fastapi

        Example
        -------
        self.fastapi_app.include_router(
            admin.router,
            prefix="/admin",
            tags=["admin"],
            responses={404: {"description": "Not found"}},
        )

        :return:
        """
        pass

    def fastapi_register_endpoints(self):
        """
        This allows you to import other files with extra fastapi endpoints which were not inside of routers
        :return:
        """
        pass

    def sentry_init(self):
        """
        Register sentry
        :return:
        """
        Sentry(dev_mode=self.dev_mode).init()

    def get_mysql_credentials(self) -> MySQLCredentials:
        """
        Override to return MySQL credentials
        :return:
        """
        raise Exception("get_mysql_credentials must be overridden in your service file.")

    def mysql_init(self):
        """
        Register sentry
        :return:
        """
        self.mysql_driver = Mysql(self.get_mysql_credentials(), dev_mode=self.dev_mode).init()

    def socket_init(self):
        """
        This sets up the sockets app

        :return:
        """
        self.socket_driver = Socketio(dev_mode=self.dev_mode).init()
        self.fastapi_driver.mount_app("/sockets", self.socket_driver.socket_app)

    def socket_register_events(self):
        """
        This allows you to import other files and/or define events for socket io
        :return:
        """
        pass

    def register_integration(self, integration: Integration):
        """
        Registers an integration
        :param integration:
        :return:
        """
        State.integrations.register(integration)

    def register_integrations(self):
        """
        Register all the integrations the micro-service requires
        :return:
        """
        pass

    def redis_init(self):
        self.redis_driver = Redis(dev_mode=self.dev_mode).init()

    def mongo_init(self):
        """
        Sets up mongodb connection
        :return:
        """
        self.mongo_driver = Mongo(dev_mode=self.dev_mode).init()

    def aws_init(self):
        """
        Sets up a connection to AWS
        :return:
        """
        self.aws_driver = AWS(dev_mode=self.dev_mode).init()
