"""The Python implementation of the Yunanbao FSB Pipeline service"""
import os
import grpc
import time
import logging
from concurrent import futures
from kubernetes import config
from traitlets.config import Application
from .experiment import ExperimentService
from ._version import __version__
from traitlets import (
    Integer,
    Unicode,
    Dict,
    default
)

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_NAMESPACE_IN_CLUSTER = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'


aliases = {
    'log-level': 'Application.log_level',
    'config': 'WFPipelineService.config_file',
    'ip': 'WFPipelineService.ip',
    'port': 'WFPipelineService.port',
    'workers': 'WFPipelineService.workers',
}


flags = {
    'debug': (
        {'Application': {'log_level': logging.DEBUG}},
        "set log level to logging.DEBUG (maximize logging output)",
    ),
}


class WFPipelineService(Application):
    name = 'wfp'
    version = __version__
    description = """An application for starting a pipeline proxy server to kubeflow
    """

    aliases = Dict(aliases)
    flags = Dict(flags)

    config_file = Unicode(
        'wfp_config.py', help="The config file to load"
    ).tag(config=True)

    ip = Unicode(
        '0.0.0.0', help="Host IP address for listening (default 0.0.0.0)."
    ).tag(config=True)

    port = Integer(
        50051, help="Port (default 50051)."
    ).tag(config=True)

    workers = Integer(
        10, help="Max workers."
    ).tag(config=True)

    # the grpc server handle
    server = None

    @default('log_level')
    def _log_level_default(self):
        return logging.INFO

    @default('log_datefmt')
    def _log_datefmt_default(self):
        """Exclude date from default date format"""
        return "%Y-%m-%d %H:%M:%S"

    @default('log_format')
    def _log_format_default(self):
        """override default log format to include time"""
        return "[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s"

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)

        logger = logging.getLogger('wfp')
        logger.propagate = True
        logger.parent = self.log
        logger.setLevel(self.log.level)

        if os.path.exists(_NAMESPACE_IN_CLUSTER):
            config.load_incluster_config()
        else:
            config.load_kube_config()

    def start(self, argv=None):
        self.initialize(argv)
        self.server = grpc.server(
            futures.ThreadPoolExecutor(
                max_workers=self.workers))
        ExperimentService.add_to_server(self.server)

        self.server.add_insecure_port('%s:%d' % (self.ip, self.port))
        self.server.start()
        self.log.info(
            "Pipeline proxy server listening on %s:%s..." %
            (self.ip, self.port))

        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            self.server.stop(0)

    @classmethod
    def launch(cls, argv=None):
        self = cls.instance()
        self.start(argv)


main = WFPipelineService.launch

if __name__ == '__main__':
    main()
