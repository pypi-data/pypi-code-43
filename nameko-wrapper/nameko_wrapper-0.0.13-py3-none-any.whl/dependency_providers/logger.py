from nameko.extensions import DependencyProvider

from nameko_wrapper.log.logger import Logger


class LoggerDependency(DependencyProvider):
    """Logger Dependency"""

    def __init__(self, service_name):
        self.service_name = service_name
        self.logger = Logger(service_name)

    def setup(self):
        pass

    def get_dependency(self, worker_ctx):
        return self.logger
