from .handlers import setup_handlers
from . import core
from .proto import minetorch_pb2
from .proto import minetorch_pb2_grpc
from . import constants
from .package_manager import package_manager
from . import g
from .plugins import CorePlugin
from .cli import cli


def _jupyter_server_extension_paths():
    return [{"module": "featurize_jupyterlab"}]


def load_jupyter_server_extension(nb_server_app):
    core.boot()
    setup_handlers(nb_server_app)
