from typing import List

from ehelply_bootstrapper.bootstrap import Bootstrap
from ehelply_bootstrapper.utils.state import State

from ehelply_bootstrapper.bootstrap import LOADABLE_REDIS, LOADABLE_SENTRY, LOADABLE_SOCKET, \
    LOADABLE_FASTAPI, LOADABLE_MONGO, LOADABLE_AWS, LOADABLE_MYSQL

from pathlib import Path

"""
SECTION: CONFIGURATION AND SETUP

THESE VARIABLES ARE EXTREMELY IMPORTANT AND MUST BE SET FOR EACH SERVICE
"""

"""
loadables
This defines which drivers should be loaded when the service runs
Each driver has an associated constant
Add the applicable constant to the list for the drivers you wish to use
"""
loadables = [LOADABLE_FASTAPI, LOADABLE_MYSQL]

"""
service_name
The name of this service
"""
service_name = "Service Template"

"""
service_key
The 'key' name of this server. It should be all lowercase and without any spaces or special symbols.
This name is used for the path to the configuration for this service
"""
service_key = "service-template"

"""
service_version
This is the version of the service
"""
service_version = "0.1.0"

"""
configs
This is used to define the names (including .yaml) of other configuraiton files you would like to have the application
    load for you.
If you are satisfied with the app.yaml and bootstrap.yaml configuration files, leave this value at None
"""
configs: List[str] = None

"""
dev_mode
This can either be toggled here or by launching the application with the `--dev` argument
Dev mode will preform tests on each driver, run the fastapi dev server if fastapi is enabled, and use the alternate
    configuration files
"""
dev_mode: bool = True

"""
debug_mode
This is used to define the level of debug we want to preform. Typically this is just used within the logger to output
    different amounts of information. The typical range is between 0 (No debug) to 3 (Full Debug)
"""
debug_mode: int = 3

"""
config_path
This is an override for the configuration path
It is very unlikely that you should need to change this, but if you have configs stored somewhere else and this
    makes it convenient, go for it. 
"""
config_path: str = str(Path(__file__).parents[1]) + "/config"

"""
SECTION: BOOTSTRAPPING
"""


class ServiceBootstrap(Bootstrap):
    """
    This class sets up the entire service

    There are plenty of methods you can override in this class.
    Most of these methods have defaults that just work. However, in the case of custom functionality or more control
        just override them.
    The methods which you are most likely to require have a '!' to the left of their name

    Note: If you do not override post_load, the application will end immediately if you are not using fast api

    pre_load()
        * This method is called prior to any drivers being loaded

    sentry_init()
        * This method is used to setup sentry

    fastapi_init()
        * This method is used to setup fastapi

    ! fastapi_middleware()
        * This method is used to inject middleware into fastapi

    ! fastapi_routers()
        * This method is used to inject routers into fastapi

    socket_init()
        * This method is used to setup socket io

    redis_init()
        * This method is used to setup redis

    mongo_init()
        * This method is used to setup mongo

    rabbitmq_init()
        * This method is used to setup rabbitmq

    ! fastapi_register_endpoints()
        * This method is used to define extra endpoints for fastapi which are not already in a router

    ! socket_register_events()
        * This method is used to define all of your socket io events

    ! post_load()
        * This method is called after all of the drivers have been loaded
        * In other words, this method should be where your application logic begins
    """

    def __init__(self):
        super().__init__(service_name=service_name,
                         service_key=service_key,
                         service_version=service_version,
                         loadables=loadables,
                         stage="dev",
                         config_path=config_path,
                         configs=configs,
                         dev_mode=dev_mode,
                         debug_mode=debug_mode)

    def register_integrations(self):
        super().register_integrations()

    def post_load(self):
        State.logger.warning("No application code added to the post_load function inside of the service_bootstrap")
        if LOADABLE_FASTAPI not in loadables:
            State.logger.info("The service will now close as a result.")
        else:
            State.logger.debug("The service will now delegate control to the fastapi server")
