from .engine import Server
from . import config


def start_server():
    server = Server(config.loop)
    config.loop.run_until_complete(server.start())
    config.loop.run_forever()