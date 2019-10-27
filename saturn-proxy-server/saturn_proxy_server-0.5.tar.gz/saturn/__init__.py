import logging
from ipaddress import ip_network

from . import protocol
from . import auth
from . import config
from . import dispatcher
from . import engine
from . import socks
from . import state
from .version import __version__

logging.basicConfig(level=logging.INFO)


def validate_config():
    if hasattr(config, "ALLOWED_DESTINATIONS"):
        ips = []
        for ip in config.ALLOWED_DESTINATIONS:
            ips.append(ip_network(ip))
        config.ALLOWED_DESTINATIONS = ips


validate_config()


def start_server(host="0.0.0.0", port=8080):
    server = engine.Server(host, port)
    server.start()
