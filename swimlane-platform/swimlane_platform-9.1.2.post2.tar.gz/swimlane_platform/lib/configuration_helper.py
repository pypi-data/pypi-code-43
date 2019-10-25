#!/usr/bin/env python
from swimlane_platform.lib import DockerManager, SplitStreamLogger, names, debug_function_return


class ConfigurationHelper():

    def __init__(self, logger):
        # type: (SplitStreamLogger) -> ConfigurationHelper
        self._docker_manager = DockerManager(logger)
        self.logger = logger

    @debug_function_return
    def turbine_enabled(self):
        return self._docker_manager.container_get(names.SW_TURBINE_ENGINE) != None
