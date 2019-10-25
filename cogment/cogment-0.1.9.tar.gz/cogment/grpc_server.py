from cogment.agent_service import AgentService, Agent
from cogment.env_service import EnvService, Environment
from cogment.utils import list_versions

from cogment.api.environment_pb2_grpc import add_EnvironmentServicer_to_server
from cogment.api.agent_pb2_grpc import add_AgentServicer_to_server

from cogment.api.environment_pb2 import _ENVIRONMENT as env_descriptor
from cogment.api.agent_pb2 import _AGENT as agent_descriptor

from cogment.errors import ConfigError

from grpc_reflection.v1alpha import reflection
from concurrent.futures import ThreadPoolExecutor
import grpc
import os
import signal
from threading import Event

from distutils.util import strtobool

ENABLE_REFLECTION_VAR_NAME = 'COGMENT_GRPC_REFLECTION'
DEFAULT_PORT = 9000
MAX_WORKERS = 10


# A Grpc endpoint serving a cogment service
class GrpcServer:
    def __init__(self, service_type, settings, port=DEFAULT_PORT):
        print("Versions:")
        for v in list_versions(service_type).versions:
            print(f'  {v.name}: {v.version}')

        self._port = port
        self._grpc_server = grpc.server(ThreadPoolExecutor(
          max_workers=MAX_WORKERS))

        # Register service
        if issubclass(service_type, Agent):
            self._service_type = agent_descriptor
            add_AgentServicer_to_server(
              AgentService(service_type, settings), self._grpc_server)
        elif issubclass(service_type, Environment):
            self._service_type = env_descriptor
            add_EnvironmentServicer_to_server(
              EnvService(service_type, settings), self._grpc_server)
        else:
            raise ConfigError('Invalid service type')

        # Enable grpc reflection if requested
        if strtobool(os.getenv(ENABLE_REFLECTION_VAR_NAME, 'false')):
            SERVICE_NAMES = (
                self._service_type.full_name,
                reflection.SERVICE_NAME,
            )
            reflection.enable_server_reflection(
              SERVICE_NAMES, self._grpc_server)

        self._grpc_server.add_insecure_port(f'[::]:{port}')

    def serve(self):
        self.start()
        print("start serving...")
        stop_serving_event = Event()

        def finished(a, b):
            stop_serving_event.set()

        for sig in ('TERM', 'HUP', 'INT'):
            signal.signal(getattr(signal, 'SIG'+sig), finished)

        stop_serving_event.wait()
        print("done serving...")

    def start(self):
        self._grpc_server.start()
        print(f"{self._service_type.full_name} service"
              f" listening on port {self._port}")

    def stop(self):
        self._grpc_server.stop(0)
